"""
FL Model Polling Service - Automatically checks for and downloads new global models
Runs as a background daemon that polls the FL server every 5 seconds
Auto-downloads and activates new models when available
"""

import os
import time
import requests
import shutil
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import threading

load_dotenv('.env.fl')

# Configuration
FL_SERVER_URL = os.getenv('FL_SERVER_URL', 'http://localhost:5000')
BANK_ID = os.getenv('BANK_ID', 'bank_a')
MODELS_FOLDER = 'models'
ACTIVE_MODEL_PATH = os.path.join(MODELS_FOLDER, 'active_model.h5')
GLOBAL_MODEL_PATH = os.path.join(MODELS_FOLDER, 'global_model.h5')
POLL_INTERVAL = 5  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FLModelPoller:
    """Background service to poll for and download new FL models"""
    
    def __init__(self):
        self.current_round = 0
        self.running = False
        self.thread = None
        self.last_check = None
        
    def start(self):
        """Start the polling service"""
        if self.running:
            logger.warning("Poller already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info(f"✅ FL Model Poller started (interval: {POLL_INTERVAL}s)")
        
    def stop(self):
        """Stop the polling service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("⏹️  FL Model Poller stopped")
    
    def _poll_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                self.check_and_download_new_model()
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
            
            time.sleep(POLL_INTERVAL)
    
    def check_and_download_new_model(self):
        """Check if new model is available and download it"""
        try:
            self.last_check = datetime.now().isoformat()
            
            # Check model version
            response = requests.get(
                f"{FL_SERVER_URL}/api/model_version",
                params={
                    'client_id': BANK_ID,
                    'current_round': self.current_round
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return
            
            data = response.json()
            server_round = data.get('current_round', 0)
            has_new_model = data.get('has_new_model', False)
            
            if not has_new_model or server_round <= self.current_round:
                return
            
            logger.info(f"🆕 New model available! Round {server_round} (current: {self.current_round})")
            
            # Download the new model
            download_response = requests.get(
                f"{FL_SERVER_URL}/api/download_global_model",
                params={'client_id': BANK_ID, 'format': 'bytes'},
                timeout=120
            )
            
            if download_response.status_code == 200:
                os.makedirs(MODELS_FOLDER, exist_ok=True)
                
                # Save as round-numbered version (no timestamp, prevents duplicates)
                versioned_path = os.path.join(
                    MODELS_FOLDER, 
                    f"global_model_round_{server_round}.h5"
                )
                
                # Only save if this round doesn't exist yet (prevent duplicates)
                if not os.path.exists(versioned_path):
                    with open(versioned_path, 'wb') as f:
                        f.write(download_response.content)
                    logger.info(f"   Saved: global_model_round_{server_round}.h5")
                else:
                    logger.info(f"   Round {server_round} model already exists, skipping save")
                
                # Copy to active model path (used by scoring service)
                shutil.copy(versioned_path, ACTIVE_MODEL_PATH)
                
                # Also update global_model.h5 for next training round
                shutil.copy(versioned_path, GLOBAL_MODEL_PATH)
                
                # Update current round
                self.current_round = server_round
                
                size_mb = len(download_response.content) / (1024 * 1024)
                logger.info(f"✅ Model downloaded and activated!")
                logger.info(f"   Round: {server_round}")
                logger.info(f"   Size: {size_mb:.2f} MB")
                logger.info(f"   Active: {ACTIVE_MODEL_PATH}")
                
                # Reload scoring model to use the new model
                try:
                    from app.services.nn_scoring_service import get_scoring_service
                    scoring_service = get_scoring_service()
                    if scoring_service.reload_model():
                        logger.info("   Scoring service updated with new model")
                except Exception as e:
                    logger.warning(f"   Could not reload scoring service: {e}")
                
                # Merge fl_dataset.csv into customers.csv after successful FL round
                try:
                    from app.services.fl_data_collector import merge_fl_dataset_to_customers
                    if merge_fl_dataset_to_customers():
                        logger.info("   ✅ New data merged into customers.csv for next round")
                except Exception as e:
                    logger.warning(f"   Could not merge datasets: {e}")
            else:
                logger.error(f"Download failed: {download_response.status_code}")
        
        except requests.RequestException as e:
            logger.debug(f"Server connection error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
    
    def get_status(self):
        """Get poller status"""
        return {
            'running': self.running,
            'current_round': self.current_round,
            'last_check': self.last_check,
            'poll_interval': POLL_INTERVAL
        }

# Global poller instance
_poller_instance = None

def get_poller() -> FLModelPoller:
    """Get singleton poller instance"""
    global _poller_instance
    if _poller_instance is None:
        _poller_instance = FLModelPoller()
    return _poller_instance

def start_polling():
    """Start the polling service"""
    poller = get_poller()
    poller.start()

def stop_polling():
    """Stop the polling service"""
    poller = get_poller()
    poller.stop()

def get_polling_status():
    """Get polling status"""
    poller = get_poller()
    return poller.get_status()

if __name__ == "__main__":
    # Run as standalone service
    logger.info("="*70)
    logger.info(f"FL Model Polling Service - {BANK_ID}")
    logger.info(f"Server: {FL_SERVER_URL}")
    logger.info("="*70)
    
    poller = FLModelPoller()
    poller.start()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        poller.stop()
