# fl_routes.py
# Federated Learning API endpoints for multi-bank collaboration.
# POST /train: triggers local FL training on bank's dataset
# POST /send-update: sends model weights to FL server
# GET /download-global: downloads latest global model from FL server
# GET /fl-status: shows current FL round and server status
# GET /check-model-update: poll for new model versions

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

load_dotenv('.env.fl')

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
    Training runs in background and uploads weights to FL server.
    """
    try:
        # Check if training script exists
        if not os.path.exists(FL_TRAINING_SCRIPT):
            raise HTTPException(status_code=500, detail=f"Training script not found: {FL_TRAINING_SCRIPT}")
        
        # Set environment variables for training
        env = os.environ.copy()
        env['FL_EPOCHS'] = str(request.epochs)
        env['FL_BATCH_SIZE'] = str(request.batch_size)
        env['FL_LEARNING_RATE'] = str(request.learning_rate)
        env['BANK_ID'] = request.bank_id
        
        # Run training script
        print(f"🚀 Starting FL training for {request.bank_id}...")
        result = subprocess.run(
            [sys.executable, FL_TRAINING_SCRIPT],
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "FL training completed and weights uploaded",
                "bank_id": request.bank_id,
                "epochs": request.epochs,
                "output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
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
