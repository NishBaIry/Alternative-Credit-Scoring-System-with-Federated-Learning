#!/bin/bash
# FL Client Training Script with Conda Environment Activation
# Activates tensorflow_env and runs FL training

set -e

echo "=========================================="
echo "FL Client Training Script"
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
if [ ! -f "app/services/fl_client_training.py" ]; then
    echo "❌ Error: fl_client_training.py not found"
    exit 1
fi

if [ ! -f ".env.fl" ]; then
    echo "⚠️  Warning: .env.fl file not found"
    echo "Using default configuration"
else
    echo "✅ FL configuration found: .env.fl"
    source .env.fl
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  Bank ID: ${BANK_ID:-bank_a}"
echo "  FL Server: ${FL_SERVER_URL:-http://localhost:5000}"
echo "  Dataset: ${LOCAL_DATASET_PATH:-data/fl_dataset.csv}"
echo ""

# Check if dataset exists
if [ -n "$LOCAL_DATASET_PATH" ] && [ ! -f "$LOCAL_DATASET_PATH" ]; then
    echo "⚠️  Warning: Dataset not found at $LOCAL_DATASET_PATH"
fi

echo "=========================================="
echo "Starting FL Training..."
echo "=========================================="
echo ""

# Run FL training
python app/services/fl_client_training.py

echo ""
echo "=========================================="
echo "Training Complete"
echo "=========================================="
