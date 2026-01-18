#!/bin/bash
# FL Server Startup Script with Conda Environment Activation
# Activates tensorflow_env and starts the FL server

set -e

echo "=========================================="
echo "FL Server Startup Script"
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

# Change to server directory
cd "$(dirname "$0")"

# Check if required files exist
if [ ! -f "fl_server.py" ]; then
    echo "❌ Error: fl_server.py not found in current directory"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "⚠️  Warning: requirements.txt not found"
else
    echo "📦 Checking dependencies..."
    pip install -q -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Using default configuration"
else
    echo "✅ Configuration file found: .env"
fi

# Check if base model exists
if [ ! -f "models/global_model.h5" ]; then
    echo "⚠️  Warning: Base model not found at models/global_model.h5"
    echo "Please place your initial model at this location"
fi

echo ""
echo "=========================================="
echo "Starting FL Server..."
echo "=========================================="
echo ""

# Start the FL server
python fl_server.py
