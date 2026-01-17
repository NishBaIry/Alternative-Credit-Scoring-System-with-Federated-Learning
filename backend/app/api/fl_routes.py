# fl_routes.py
# Federated Learning API endpoints for multi-bank collaboration.
# POST /train: triggers local FL training on bank's dataset
# POST /send-update: sends model weights to FL server
# GET /download-global: downloads latest global model from FL server
# GET /fl-status: shows current FL round and server status

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import subprocess
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv('.env.fl')

router = APIRouter()

# Configuration
FL_SERVER_URL = os.getenv('FL_SERVER_URL', 'http://localhost:5000')
FL_TRAINING_SCRIPT = 'app/services/fl_client_training.py'

class FLTrainRequest(BaseModel):
    """Request to trigger FL training"""
    bank_id: str = "bank_a"
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

@router.get("/receive-global")
async def receive_global_model(bank_id: str):
    """
    Legacy endpoint - use /download-global instead.
    Receive and apply the latest global model from FL server.
    """
    return {
        "status": "deprecated",
        "message": "Use /download-global endpoint instead",
        "bank_id": bank_id
    }

        "last_update": "1 hour ago"
    }
