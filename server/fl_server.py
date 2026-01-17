"""
Federated Learning Server - Flask API for Credit Scoring
Aggregates neural network weights from multiple banks using FedAvg
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import logging
import joblib
from datetime import datetime
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

# Load environment variables
load_dotenv()

# Import FedAvg algorithm
from fedavg import FedAvg

# Configure logging with cleaner format
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MODELS_FOLDER = os.getenv('MODELS_FOLDER', 'models')
BASE_MODEL_PATH = os.getenv('BASE_MODEL_PATH', 'models/global_model.h5')
GLOBAL_MODEL_PATH = os.getenv('GLOBAL_MODEL_PATH', 'models/global_model_latest.h5')
VALIDATION_DATASET_PATH = os.getenv('VALIDATION_DATASET_PATH', 'data/bank_a_fl_dataset.csv')
VALIDATE_BEFORE_REPLACE = os.getenv('VALIDATE_BEFORE_REPLACE', 'True').lower() == 'true'

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Initialize FedAvg aggregator
fed_avg = FedAvg(base_model_path=BASE_MODEL_PATH)

# State persistence file
STATE_FILE = os.path.join(MODELS_FOLDER, 'server_state.json')

# Load persisted state or initialize new
def load_server_state():
    """Load server state from disk"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                saved_state = json.load(f)
                print(f"📂 Loaded server state: Round {saved_state.get('current_round', 0)}, Total aggregations: {saved_state.get('total_aggregations', 0)}")
                return saved_state
        except Exception as e:
            print(f"⚠️ Could not load state file: {e}")
    return {
        'current_round': 0,
        'clients_connected': 0,
        'pending_updates': {},
        'aggregation_threshold': int(os.getenv('AGGREGATION_THRESHOLD', 2)),
        'total_aggregations': 0
    }

def save_server_state():
    """Save server state to disk"""
    try:
        # Don't save pending_updates (transient data)
        state_to_save = {
            'current_round': server_state['current_round'],
            'total_aggregations': server_state['total_aggregations'],
            'aggregation_threshold': server_state['aggregation_threshold']
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state_to_save, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save state: {e}")

# Server state
server_state = load_server_state()
server_state['clients_connected'] = 0
server_state['pending_updates'] = {}

# Sync fed_avg round counter with loaded state
fed_avg.current_round = server_state['current_round']

# ============================================
# HELPER FUNCTIONS
# ============================================

def print_header(text, char="="):
    """Print a formatted header"""
    logger.info("")
    logger.info(char * 70)
    logger.info(f"  {text}")
    logger.info(char * 70)

def print_subheader(text):
    """Print a formatted subheader"""
    logger.info("")
    logger.info(f"▸ {text}")
    logger.info("─" * 70)

def print_success(text):
    """Print success message"""
    logger.info(f"✅ {text}")

def print_error(text):
    """Print error message"""
    logger.error(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    logger.warning(f"⚠️  {text}")

def print_info(text, indent=0):
    """Print info message"""
    prefix = "  " * indent
    logger.info(f"{prefix}• {text}")

def load_weights_from_file(filepath):
    """Load model weights from .h5 or .npz file"""
    try:
        if filepath.endswith('.h5'):
            model = tf.keras.models.load_model(filepath, compile=False)
            return model.get_weights()
        elif filepath.endswith('.npz'):
            data = np.load(filepath, allow_pickle=True)
            # Load arrays in correct order (arr_0, arr_1, arr_2, ...)
            weights = []
            for i in range(len(data.files)):
                key = f'arr_{i}'
                if key in data:
                    weights.append(data[key])
            if not weights:
                # Fallback to sorted keys if arr_N pattern not found
                weights = [data[key] for key in sorted(data.files)]
            return weights
        else:
            print_error(f"Unsupported file format: {filepath}")
            return None
    except Exception as e:
        print_error(f"Failed to load weights from {filepath}: {e}")
        return None

def save_upload_info(client_id, metadata):
    """Save upload metadata"""
    info_file = f"{UPLOAD_FOLDER}/{client_id}_info.json"
    with open(info_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def evaluate_model_accuracy(model, dataset_path):
    """
    Evaluate model accuracy on validation dataset (CSV format)
    """
    try:
        import pandas as pd
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        if not os.path.exists(dataset_path):
            print_warning(f"Validation dataset not found at {dataset_path}")
            return None
        
        # Load validation data
        df = pd.read_csv(dataset_path)
        
        # Remove authentication and ID columns
        remove_cols = ['customer_id', 'password']
        df = df.drop(columns=[col for col in remove_cols if col in df.columns])
        
        # Separate features and target
        if 'default_flag' not in df.columns:
            print_warning("default_flag not found in validation dataset")
            return None
        
        y = df['default_flag'].astype(int).values
        X = df.drop(columns=['default_flag'])
        
        # Handle categorical and numerical columns
        categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
        numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        
        # Fill missing values
        for col in numerical_cols:
            if X[col].isnull().any():
                median_val = X[col].median()
                X[col].fillna(median_val, inplace=True)
        
        for col in categorical_cols:
            if X[col].isnull().any():
                mode_val = X[col].mode()
                if len(mode_val) > 0:
                    X[col].fillna(mode_val[0], inplace=True)
        
        # Encode categorical variables
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Make predictions
        y_pred_proba = model.predict(X_scaled, verbose=0)
        y_pred = (y_pred_proba > 0.5).astype(int).flatten()
        
        # Calculate metrics
        metrics = {
            'accuracy': float(accuracy_score(y, y_pred)),
            'precision': float(precision_score(y, y_pred)),
            'recall': float(recall_score(y, y_pred)),
            'f1': float(f1_score(y, y_pred)),
            'auc': float(roc_auc_score(y, y_pred_proba))
        }
        
        return metrics
    
    except Exception as e:
        print_error(f"Error evaluating model: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def home():
    """Home page"""
    return jsonify({
        'message': 'Federated Learning Server - Credit Scoring',
        'status': 'online',
        'version': '1.0.0',
        'endpoints': {
            'status': '/api/status',
            'upload': '/api/upload_weights',
            'download': '/api/download_global_model'
        }
    })

@app.route('/api/status', methods=['GET'])
def status():
    """Get server status"""
    stats = fed_avg.get_stats()
    
    return jsonify({
        'status': 'online',
        'current_round': server_state['current_round'],
        'clients_connected': len(server_state['pending_updates']),
        'pending_updates': list(server_state['pending_updates'].keys()),
        'aggregation_threshold': server_state['aggregation_threshold'],
        'total_aggregations': server_state['total_aggregations'],
        'fedavg_stats': stats
    })

@app.route('/api/upload_weights', methods=['POST'])
def upload_weights():
    """
    Upload model weights from bank client
    """
    try:
        # Check if weights file is present
        if 'weights' not in request.files:
            return jsonify({'error': 'No weights file provided'}), 400
        
        weights_file = request.files['weights']
        
        if weights_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Get metadata
        metadata_str = request.form.get('metadata', '{}')
        metadata = json.loads(metadata_str)
        
        client_id = metadata.get('client_id', 'unknown')
        client_name = metadata.get('client_name', 'Unknown Bank')
        upload_type = metadata.get('upload_type', 'full_weights')
        
        print_header(f"📥 NEW BANK UPLOAD", "=")
        print_info(f"Bank ID: {client_id}")
        print_info(f"Bank Name: {client_name}")
        print_info(f"Upload Type: {upload_type}")
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(f"{client_id}_{timestamp}_{weights_file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        weights_file.save(filepath)
        
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print_info(f"File Size: {file_size_mb:.2f} MB")
        print_success(f"Saved to: {filename}")
        
        # Load weights from file
        weights = load_weights_from_file(filepath)
        
        if weights is None:
            print_error("Failed to load weights from file")
            return jsonify({'error': 'Failed to load weights'}), 500
        
        # Store in pending updates
        server_state['pending_updates'][client_id] = {
            'weights': weights,
            'filepath': filepath,
            'upload_type': upload_type,
            'metadata': metadata,
            'timestamp': timestamp,
            'num_samples': metadata.get('num_samples', 1000)
        }
        
        # Save metadata
        save_upload_info(client_id, metadata)
        
        pending_count = len(server_state['pending_updates'])
        threshold = server_state['aggregation_threshold']
        
        print_info(f"Pending: {pending_count}/{threshold} banks")
        
        # Check if we have enough banks to aggregate
        if pending_count >= threshold:
            print_success(f"Threshold reached! Starting aggregation...")
            success = perform_aggregation()
            
            if success:
                return jsonify({
                    'message': 'Aggregation successful',
                    'upload_id': filename,
                    'client_id': client_id,
                    'round': fed_avg.current_round,
                    'new_model_available': True
                }), 200
            else:
                return jsonify({
                    'message': 'Aggregation failed',
                    'upload_id': filename,
                    'client_id': client_id
                }), 500
        else:
            print_info(f"Waiting for {threshold - pending_count} more bank(s)...")
        
        return jsonify({
            'message': 'Upload successful - Waiting for more banks',
            'upload_id': filename,
            'client_id': client_id,
            'pending_clients': pending_count,
            'threshold': threshold
        }), 200
    
    except Exception as e:
        print_error(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_global_model', methods=['GET'])
def download_global_model():
    """
    Download the latest global model
    """
    client_id = request.args.get('client_id', 'unknown')
    response_format = request.args.get('format', 'file')
    
    print_subheader(f"📤 Model Download Request")
    print_info(f"Bank: {client_id}")
    print_info(f"Format: {response_format}")
    
    try:
        # Check for aggregated model first, fall back to base model
        model_to_send = None
        if os.path.exists(GLOBAL_MODEL_PATH):
            model_to_send = GLOBAL_MODEL_PATH
            print_info("Sending aggregated global model")
        elif os.path.exists(BASE_MODEL_PATH):
            model_to_send = BASE_MODEL_PATH
            print_info("Sending base model (no aggregation yet)")
        else:
            print_warning("No global model available yet")
            return jsonify({'error': 'No global model available'}), 404
        
        if response_format == 'bytes':
            # Return raw bytes
            with open(model_to_send, 'rb') as f:
                model_bytes = f.read()
            
            print_success("H5 model sent (bytes)")
            
            return model_bytes, 200, {
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'attachment; filename=global_model.h5'
            }
        else:
            # Default file download (H5)
            print_success("H5 model sent (file)")
            return send_file(model_to_send, as_attachment=True, download_name='global_model.h5')
    
    except Exception as e:
        print_error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trigger_aggregation', methods=['POST'])
def trigger_aggregation():
    """
    Manually trigger aggregation (admin endpoint)
    """
    if len(server_state['pending_updates']) == 0:
        return jsonify({'error': 'No pending updates'}), 400
    
    logger.info("Manual aggregation triggered")
    success = perform_aggregation()
    
    if success:
        return jsonify({'message': 'Aggregation successful', 'round': fed_avg.current_round}), 200
    else:
        return jsonify({'error': 'Aggregation failed'}), 500

@app.route('/api/model_version', methods=['GET'])
def get_model_version():
    """
    Get current global model version info for polling.
    Banks can poll this endpoint to check if a new model is available.
    """
    client_id = request.args.get('client_id', 'unknown')
    client_current_round = request.args.get('current_round', 0, type=int)
    
    current_round = server_state['current_round']
    has_new_model = current_round > client_current_round
    
    model_size = 0
    model_timestamp = None
    model_available = False
    
    # Check aggregated model first, then base model
    if os.path.exists(GLOBAL_MODEL_PATH):
        model_size = os.path.getsize(GLOBAL_MODEL_PATH) / (1024 * 1024)
        model_timestamp = datetime.fromtimestamp(os.path.getmtime(GLOBAL_MODEL_PATH)).isoformat()
        model_available = True
    elif os.path.exists(BASE_MODEL_PATH):
        model_size = os.path.getsize(BASE_MODEL_PATH) / (1024 * 1024)
        model_timestamp = datetime.fromtimestamp(os.path.getmtime(BASE_MODEL_PATH)).isoformat()
        model_available = True
    
    return jsonify({
        'current_round': current_round,
        'has_new_model': has_new_model,
        'model_available': model_available,
        'model_size_mb': round(model_size, 2),
        'model_timestamp': model_timestamp,
        'total_aggregations': server_state['total_aggregations'],
        'pending_banks': list(server_state['pending_updates'].keys())
    })

# ============================================
# AGGREGATION LOGIC
# ============================================

def perform_aggregation():
    """
    Perform FedAvg aggregation on pending updates
    """
    try:
        print_header("🔄 FEDERATED AGGREGATION (FedAvg)", "=")
        
        # Load global model if not loaded
        if fed_avg.global_model is None:
            print_info("Loading base global model...")
            if not fed_avg.load_global_model():
                print_error("Failed to load base model")
                return False
        
        # Collect client weights and metadata
        client_weights_list = []
        client_samples_list = []
        client_ids = []
        
        print_subheader("Participating Banks")
        for client_id, update_info in server_state['pending_updates'].items():
            client_name = update_info['metadata'].get('client_name', 'Unknown')
            num_samples = update_info.get('num_samples', 1000)
            client_weights_list.append(update_info['weights'])
            client_samples_list.append(num_samples)
            client_ids.append(client_id)
            print_info(f"{client_name} ({client_id}) - {num_samples} samples", indent=1)
        
        print_info(f"Total: {len(client_weights_list)} banks")
        
        # Check if clients sent deltas or full weights
        upload_type = server_state['pending_updates'][list(server_state['pending_updates'].keys())[0]].get('upload_type', 'full_weights')
        use_deltas = (upload_type == 'weight_deltas')
        
        print_subheader("Aggregation")
        print_info(f"Method: FedAvg ({'weight deltas' if use_deltas else 'full weights'})")
        
        # Perform aggregation
        if use_deltas:
            success = fed_avg.update_global_model(
                client_deltas=client_weights_list,
                client_samples=client_samples_list,
                use_deltas=True
            )
        else:
            success = fed_avg.update_global_model(
                client_weights=client_weights_list,
                client_samples=client_samples_list,
                use_deltas=False
            )
        
        if not success:
            print_error("Aggregation computation failed")
            return False
        
        print_success("Aggregation computed successfully")
        
        # Validation check
        should_replace = True
        old_accuracy = None
        new_accuracy = None
        
        if VALIDATE_BEFORE_REPLACE and os.path.exists(VALIDATION_DATASET_PATH):
            print_subheader("Model Validation")
            
            # Evaluate old model (if exists)
            if os.path.exists(GLOBAL_MODEL_PATH):
                print_info("Evaluating OLD model...", indent=1)
                old_model = tf.keras.models.load_model(GLOBAL_MODEL_PATH, compile=False)
                old_metrics = evaluate_model_accuracy(old_model, VALIDATION_DATASET_PATH)
                if old_metrics:
                    old_accuracy = old_metrics['accuracy']
                    print_info(f"Old Accuracy: {old_accuracy:.4f}", indent=2)
            
            # Evaluate new aggregated model
            print_info("Evaluating NEW model...", indent=1)
            new_metrics = evaluate_model_accuracy(fed_avg.global_model, VALIDATION_DATASET_PATH)
            if new_metrics:
                new_accuracy = new_metrics['accuracy']
                print_info(f"New Accuracy: {new_accuracy:.4f}", indent=2)
                
                # Compare accuracies
                if old_accuracy is not None:
                    if new_accuracy >= old_accuracy:
                        print_success(f"Improvement: +{(new_accuracy - old_accuracy):.4f}")
                        should_replace = True
                    else:
                        print_warning(f"Degradation: {(new_accuracy - old_accuracy):.4f}")
                        should_replace = False
                else:
                    should_replace = True
            else:
                print_warning("Could not evaluate new model - skipping validation")
                should_replace = True
        else:
            print_info("Validation disabled or dataset not found")
        
        # Save updated global model only if validation passed
        if should_replace:
            print_subheader("Saving Model")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            round_model_path = f"{MODELS_FOLDER}/global_model_round_{fed_avg.current_round}_{timestamp}.h5"
            
            fed_avg.save_global_model(round_model_path)
            fed_avg.save_global_model(GLOBAL_MODEL_PATH)
            
            model_size_mb = os.path.getsize(round_model_path) / (1024 * 1024)
            print_success(f"Saved as: {os.path.basename(round_model_path)} ({model_size_mb:.2f} MB)")
        else:
            print_warning("Model NOT replaced (performance degraded)")
            fed_avg.current_round -= 1  # Revert round increment
            return False
        
        # Update server state
        server_state['current_round'] = fed_avg.current_round
        server_state['total_aggregations'] += 1
        
        # Persist state to disk
        save_server_state()
        
        # Clean up old files
        print_info("Cleaning up old files...", indent=1)
        model_files = sorted(Path(MODELS_FOLDER).glob('global_model_round_*.h5'), key=lambda p: p.stat().st_mtime)
        if len(model_files) > 5:
            for old_model in model_files[:-5]:
                old_model.unlink()
        
        upload_files = sorted(Path(UPLOAD_FOLDER).glob('*.npz'), key=lambda p: p.stat().st_mtime)
        if len(upload_files) > 10:
            for old_upload in upload_files[:-10]:
                old_upload.unlink()
        
        # Save aggregation info
        aggregation_info = {
            'round': fed_avg.current_round,
            'timestamp': timestamp,
            'num_clients': len(client_ids),
            'client_ids': client_ids,
            'client_samples': dict(zip(client_ids, client_samples_list)),
            'model_path': round_model_path if should_replace else 'not_saved',
            'validation': {
                'enabled': VALIDATE_BEFORE_REPLACE,
                'old_accuracy': old_accuracy,
                'new_accuracy': new_accuracy,
                'replaced': should_replace
            }
        }
        
        info_file = f"{MODELS_FOLDER}/aggregation_round_{fed_avg.current_round}_info.json"
        with open(info_file, 'w') as f:
            json.dump(aggregation_info, f, indent=2)
        
        print_header(f"✅ AGGREGATION COMPLETE - Round {fed_avg.current_round}", "=")
        
        # Clear pending updates
        server_state['pending_updates'].clear()
        
        return True
    
    except Exception as e:
        print_error(f"Aggregation error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================
# INITIALIZATION
# ============================================

def initialize_server():
    """Initialize server on startup"""
    print_header("🚀 FEDERATED LEARNING SERVER - CREDIT SCORING", "=")
    
    logger.info("")
    print_info(f"Upload Folder: {UPLOAD_FOLDER}")
    print_info(f"Models Folder: {MODELS_FOLDER}")
    print_info(f"Aggregation Threshold: {server_state['aggregation_threshold']} banks")
    print_info(f"Validation: {'Enabled' if VALIDATE_BEFORE_REPLACE else 'Disabled'}")
    
    # Check if base model exists
    logger.info("")
    if not os.path.exists(BASE_MODEL_PATH):
        print_warning(f"Base model not found: {BASE_MODEL_PATH}")
        print_warning("Place your initial model at this path")
    else:
        print_success(f"Base model found: {BASE_MODEL_PATH}")
        # Load it
        if fed_avg.load_global_model():
            print_success("Base model loaded successfully")
        else:
            print_error("Failed to load base model")
    
    print_header("Server Ready", "=")

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    initialize_server()
    
    # Get host and port from environment or use defaults
    host = os.getenv('FL_SERVER_HOST', '0.0.0.0')
    port = int(os.getenv('FL_SERVER_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info("")
    logger.info("="*70)
    logger.info(f"  🌐 FL Server running on {host}:{port}")
    logger.info(f"  📍 Local: http://localhost:{port}")
    logger.info(f"  📍 Network: http://<your-ip>:{port}")
    logger.info("="*70)
    logger.info("")
    
    app.run(host=host, port=port, debug=debug)
