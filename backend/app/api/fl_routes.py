# fl_routes.py
# Federated Learning API endpoints for multi-bank collaboration.
# POST /train: triggers local FL training on bank's dataset
# POST /send-update: sends model weights to FL server
# GET /download-global: downloads latest global model from FL server
# GET /fl-status: shows current FL round and server status
# GET /check-model-update: poll for new model versions
# POST /start-polling: start background model polling
# POST /stop-polling: stop background model polling
# GET /polling-status: get polling service status

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import subprocess
import os
import sys
import shutil
import requests
from dotenv import load_dotenv
from typing import Optional
import asyncio
from datetime import datetime
from app.services.fl_model_poller import start_polling, stop_polling, get_polling_status
from app.services.new_applications_service import get_new_applications_service
import logging

load_dotenv('.env.fl')
logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
FL_SERVER_URL = os.getenv('FL_SERVER_URL', 'http://localhost:5000')
FL_TRAINING_SCRIPT = 'app/services/fl_client_training.py'
BANK_ID = os.getenv('BANK_ID', 'bank_a')
MODELS_FOLDER = 'models'
ACTIVE_MODEL_PATH = os.path.join(MODELS_FOLDER, 'active_model.h5')
GLOBAL_MODEL_PATH = os.path.join(MODELS_FOLDER, 'global_model.h5')

# Track current model round locally
local_model_state = {
    'current_round': 0,
    'last_check': None,
    'training_in_progress': False
}

class FLTrainRequest(BaseModel):
    """Request to trigger FL training"""
    bank_id: str = BANK_ID
    epochs: int = 10
    batch_size: int = 256
    learning_rate: float = 0.001

class FLStatusResponse(BaseModel):
    """FL status response"""
    status: str
    current_round: int
    clients_connected: int
    pending_updates: list
    aggregation_threshold: int
    total_aggregations: int

@router.post("/train")
async def trigger_fl_training(request: FLTrainRequest, background_tasks: BackgroundTasks):
    """
    Trigger federated learning training on local bank dataset.
    First merges new_applications.db into bank_a.db, then runs training.
    Training runs in background and uploads weights to FL server.
    """
    try:
        # Step 1: Merge new applications into bank database
        logger.info("Checking for new applications to merge...")
        new_apps_service = get_new_applications_service()
        merged_count = new_apps_service.merge_applications_to_bank(request.bank_id)

        if merged_count > 0:
            logger.info(f"Merged {merged_count} new applications into {request.bank_id}.db")
            # Delete new_applications.db after successful merge
            new_apps_service.clear_applications()
            logger.info("new_applications.db deleted after merge")
        else:
            logger.info("No new applications to merge")

        # Step 2: Check if training script exists
        if not os.path.exists(FL_TRAINING_SCRIPT):
            raise HTTPException(status_code=500, detail=f"Training script not found: {FL_TRAINING_SCRIPT}")

        # Step 3: Set environment variables for training
        env = os.environ.copy()
        env['FL_EPOCHS'] = str(request.epochs)
        env['FL_BATCH_SIZE'] = str(request.batch_size)
        env['FL_LEARNING_RATE'] = str(request.learning_rate)
        env['BANK_ID'] = request.bank_id

        # Step 4: Run training script
        print(f"🚀 Starting FL training for {request.bank_id}...")
        result = subprocess.run(
            [sys.executable, FL_TRAINING_SCRIPT],
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            # Training successful - start polling for new model
            start_polling()

            message = f"FL training completed. {merged_count} new applications merged into dataset." if merged_count > 0 else "FL training completed."

            return {
                "status": "success",
                "message": message,
                "bank_id": request.bank_id,
                "epochs": request.epochs,
                "merged_applications": merged_count,
                "output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout,
                "polling_started": True
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Training failed: {result.stderr}"
            )
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Training timeout (>10 minutes)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@router.get("/download-global")
async def download_global_model(bank_id: str = "bank_a"):
    """
    Download the latest global model from FL server.
    """
    try:
        response = requests.get(
            f"{FL_SERVER_URL}/api/download_global_model",
            params={'client_id': bank_id, 'format': 'file'},
            timeout=60
        )
        
        if response.status_code == 200:
            # Save model locally
            model_path = f"models/{bank_id}_global_model.h5"
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            with open(model_path, 'wb') as f:
                f.write(response.content)
            
            return {
                "status": "success",
                "message": "Global model downloaded",
                "model_path": model_path,
                "size_mb": len(response.content) / (1024 * 1024)
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to download model: {response.text}"
            )
    
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"FL server unavailable: {str(e)}")

@router.get("/fl-status", response_model=FLStatusResponse)
async def get_fl_status():
    """
    Get current federated learning status from server.
    """
    try:
        response = requests.get(
            f"{FL_SERVER_URL}/api/status",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return FLStatusResponse(
                status=data.get('status', 'unknown'),
                current_round=data.get('current_round', 0),
                clients_connected=data.get('clients_connected', 0),
                pending_updates=data.get('pending_updates', []),
                aggregation_threshold=data.get('aggregation_threshold', 2),
                total_aggregations=data.get('total_aggregations', 0)
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to get FL status"
            )
    
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"FL server unavailable: {str(e)}")

@router.post("/send-update")
async def send_fl_update(bank_id: str):
    """
    Legacy endpoint - use /train instead.
    Send local model update to federated learning server.
    """
    return {
        "status": "deprecated",
        "message": "Use /train endpoint instead",
        "bank_id": bank_id
    }

@router.get("/check-model-update")
async def check_model_update():
    """
    Check if a new global model is available from FL server.
    Frontend should poll this endpoint to detect new models.
    """
    try:
        response = requests.get(
            f"{FL_SERVER_URL}/api/model_version",
            params={
                'client_id': BANK_ID,
                'current_round': local_model_state['current_round']
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            local_model_state['last_check'] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "server_round": data.get('current_round', 0),
                "local_round": local_model_state['current_round'],
                "has_new_model": data.get('has_new_model', False),
                "model_available": data.get('model_available', False),
                "model_size_mb": data.get('model_size_mb', 0),
                "model_timestamp": data.get('model_timestamp'),
                "pending_banks": data.get('pending_banks', []),
                "last_check": local_model_state['last_check']
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to check model version"
            )
    
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"FL server unavailable: {str(e)}")

@router.post("/download-and-activate")
async def download_and_activate_model():
    """
    Download the latest global model from FL server and activate it.
    This replaces the current active model with the new aggregated one.
    """
    try:
        # First check if new model available
        version_response = requests.get(
            f"{FL_SERVER_URL}/api/model_version",
            params={'client_id': BANK_ID, 'current_round': local_model_state['current_round']},
            timeout=10
        )
        
        if version_response.status_code != 200:
            raise HTTPException(status_code=503, detail="Cannot check model version")
        
        version_data = version_response.json()
        server_round = version_data.get('current_round', 0)
        
        # Download the model
        response = requests.get(
            f"{FL_SERVER_URL}/api/download_global_model",
            params={'client_id': BANK_ID, 'format': 'bytes'},
            timeout=120
        )
        
        if response.status_code == 200:
            os.makedirs(MODELS_FOLDER, exist_ok=True)
            
            # Save as timestamped version
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            versioned_path = os.path.join(MODELS_FOLDER, f"global_model_round_{server_round}_{timestamp}.h5")
            
            with open(versioned_path, 'wb') as f:
                f.write(response.content)
            
            # Copy to active model path (this is what the scoring service uses)
            shutil.copy(versioned_path, ACTIVE_MODEL_PATH)
            
            # Also update the global_model.h5 for next training round
            shutil.copy(versioned_path, GLOBAL_MODEL_PATH)
            
            # Update local state
            local_model_state['current_round'] = server_round
            
            return {
                "status": "success",
                "message": "New model downloaded and activated",
                "round": server_round,
                "model_path": ACTIVE_MODEL_PATH,
                "versioned_path": versioned_path,
                "size_mb": len(response.content) / (1024 * 1024)
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to download model: {response.text}"
            )
    
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"FL server unavailable: {str(e)}")

@router.get("/local-model-info")
async def get_local_model_info():
    """
    Get information about the local active model.
    """
    active_exists = os.path.exists(ACTIVE_MODEL_PATH)
    global_exists = os.path.exists(GLOBAL_MODEL_PATH)
    
    active_info = None
    if active_exists:
        stat = os.stat(ACTIVE_MODEL_PATH)
        active_info = {
            "path": ACTIVE_MODEL_PATH,
            "size_mb": stat.st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    global_info = None
    if global_exists:
        stat = os.stat(GLOBAL_MODEL_PATH)
        global_info = {
            "path": GLOBAL_MODEL_PATH,
            "size_mb": stat.st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    return {
        "status": "success",
        "local_round": local_model_state['current_round'],
        "training_in_progress": local_model_state['training_in_progress'],
        "last_server_check": local_model_state['last_check'],
        "active_model": active_info,
        "global_model": global_info
    }

@router.get("/training-status")
async def get_training_status():
    """
    Get current training status.
    """
    return {
        "training_in_progress": local_model_state['training_in_progress'],
        "local_round": local_model_state['current_round'],
        "bank_id": BANK_ID
    }

@router.post("/start-polling")
async def start_model_polling():
    """
    Start background polling for new FL models.
    Will automatically download and activate new models when available.
    """
    try:
        start_polling()
        status = get_polling_status()
        return {
            "status": "success",
            "message": "Polling service started",
            "polling_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start polling: {str(e)}")

@router.post("/stop-polling")
async def stop_model_polling():
    """
    Stop background polling for FL models.
    """
    try:
        stop_polling()
        return {
            "status": "success",
            "message": "Polling service stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop polling: {str(e)}")

@router.get("/polling-status")
async def get_polling_service_status():
    """
    Get current status of the polling service.
    """
    try:
        status = get_polling_status()
        return {
            "status": "success",
            "polling": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get polling status: {str(e)}")

@router.get("/dataset-stats")
async def get_fl_dataset_statistics():
    """
    Get statistics about FL dataset (new data since last training round).
    """
    try:
        from app.services.fl_data_collector import get_fl_dataset_stats
        stats = get_fl_dataset_stats()
        return {
            "status": "success",
            "fl_dataset": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dataset stats: {str(e)}")

@router.get("/list-models")
async def list_available_models():
    """
    List all available FL models (base + round models).
    """
    try:
        import glob
        models = []
        
        # Find all round models
        round_models = glob.glob(os.path.join(MODELS_FOLDER, "global_model_round_*.h5"))
        for model_path in sorted(round_models):
            filename = os.path.basename(model_path)
            # Extract round number from filename: global_model_round_1.h5
            round_num = filename.replace("global_model_round_", "").replace(".h5", "")
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            
            models.append({
                "id": f"round_{round_num}",
                "name": f"Round {round_num}",
                "round": int(round_num) if round_num.isdigit() else 0,
                "path": filename,
                "size_mb": round(size_mb, 2)
            })
        
        # Check active model
        active_model_name = "Base Model"
        if os.path.exists(ACTIVE_MODEL_PATH):
            # Check which round model is currently active
            import filecmp
            for model in models:
                model_full_path = os.path.join(MODELS_FOLDER, model["path"])
                if filecmp.cmp(ACTIVE_MODEL_PATH, model_full_path, shallow=False):
                    active_model_name = model["name"]
                    break
        
        return {
            "status": "success",
            "models": sorted(models, key=lambda x: x["round"]),
            "active_model": active_model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@router.post("/switch-model")
async def switch_active_model(model_id: str):
    """
    Switch the active model to a specific round model.
    """
    try:
        import shutil
        
        # Extract round number from model_id (e.g., "round_1" -> "1")
        round_num = model_id.replace("round_", "")
        model_filename = f"global_model_round_{round_num}.h5"
        model_path = os.path.join(MODELS_FOLDER, model_filename)
        
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail=f"Model not found: {model_filename}")
        
        # Copy to active_model.h5
        shutil.copy(model_path, ACTIVE_MODEL_PATH)
        
        # Reload scoring service
        from app.services.nn_scoring_service import get_scoring_service
        scoring_service = get_scoring_service()
        scoring_service.reload_model()
        
        return {
            "status": "success",
            "message": f"Switched to Round {round_num} model",
            "active_model": f"Round {round_num}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch model: {str(e)}")


