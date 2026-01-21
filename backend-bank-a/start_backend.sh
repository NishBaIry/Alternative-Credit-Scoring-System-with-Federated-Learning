#!/bin/bash
# Backend API Startup Script with Conda Environment Activation
# Activates tensorflow_env and starts the FastAPI backend

set -e

echo "=========================================="
echo "Backend API Startup Script"
echo "=========================================="
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda not found in PATH"
    echo "Please install Anaconda/Miniconda or ensure conda is in your PATH"
    exit 1
fi

# Initialize conda for bash
eval "$(conda shell.bash hook)"

# Check if tensorflow_env exists
if ! conda env list | grep -q "tensorflow_env"; then
    echo "❌ Error: tensorflow_env conda environment not found"
    echo "Please create it first with: conda create -n tensorflow_env python=3.9"
    exit 1
fi

# Activate conda environment
echo "🔄 Activating conda environment: tensorflow_env"
conda activate tensorflow_env

# Check if we're in the tensorflow_env
if [[ "$CONDA_DEFAULT_ENV" != "tensorflow_env" ]]; then
    echo "❌ Error: Failed to activate tensorflow_env"
    exit 1
fi

echo "✅ Conda environment activated: $CONDA_DEFAULT_ENV"
echo ""

# Change to backend directory
cd "$(dirname "$0")"

# Check if required files exist
if [ ! -d "app" ]; then
    echo "❌ Error: app directory not found"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "⚠️  Warning: requirements.txt not found"
else
    echo "📦 Checking dependencies..."
    pip install -q -r requirements.txt
fi

# Check if .env.fl file exists
if [ ! -f ".env.fl" ]; then
    echo "⚠️  Warning: .env.fl file not found"
    echo "Using default FL configuration"
else
    echo "✅ FL configuration found: .env.fl"
fi

# Get host and port from arguments or use defaults
HOST="${1:-127.0.0.1}"
PORT="${2:-8000}"

echo ""
echo "=========================================="
echo "Starting Backend API on $HOST:$PORT"
echo "=========================================="
echo ""

# Start the backend using uvicorn
uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
