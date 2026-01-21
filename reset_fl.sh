#!/bin/bash
# Reset Federated Learning to Round 1
# This script clears all FL training state and models from banks and server

set -e

echo "=========================================="
echo "FL RESET TO ROUND 1"
echo "=========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $SCRIPT_DIR"
echo ""

# Confirm before proceeding
read -p "⚠️  This will delete all FL training progress. Continue? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🧹 Cleaning Bank A..."
rm -f backend-bank-a/models/bank_a_weights.npz
rm -f backend-bank-a/models/global_model_round_*.h5
rm -f backend-bank-a/models/global_model.h5
rm -f backend-bank-a/models/global_model.weights.h5
rm -f backend-bank-a/app/services/__pycache__/fl_client_training.*.pyc
echo "  ✓ Removed bank_a_weights.npz"
echo "  ✓ Removed global_model files"
echo "  ✓ Cleared training cache"

echo ""
echo "🧹 Cleaning Bank B..."
rm -f backend-bank-b/models/bank_b_weights.npz
rm -f backend-bank-b/models/global_model_round_*.h5
rm -f backend-bank-b/models/global_model.h5
rm -f backend-bank-b/models/global_model.weights.h5
rm -f backend-bank-b/app/services/__pycache__/fl_client_training.*.pyc
echo "  ✓ Removed bank_b_weights.npz"
echo "  ✓ Removed global_model files"
echo "  ✓ Cleared training cache"

echo ""
echo "🧹 Cleaning FL Server..."
rm -rf server/uploads/*
rm -f server/models/aggregation_round_*.json
rm -f server/models/global_model_latest.h5
rm -f server/models/global_model_round_*.h5
rm -f server/models/server_state.json
echo "  ✓ Cleared uploads folder"
echo "  ✓ Removed aggregation files"
echo "  ✓ Removed server state"

echo ""
echo "📋 Ensuring base model exists on server..."
if [ ! -f "server/models/global_model.h5" ]; then
    if [ -f "backend-bank-a/models/model.h5" ]; then
        cp backend-bank-a/models/model.h5 server/models/global_model.h5
        echo "  ✓ Copied base model from Bank A"
    else
        echo "  ⚠️  Warning: Base model not found at backend-bank-a/models/model.h5"
        echo "  Please ensure a base model exists before starting FL training"
    fi
else
    echo "  ✓ Base model already exists"
fi

echo ""
echo "=========================================="
echo "✅ FL RESET COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Ensure FL server is running: cd server && bash start_fl_server.sh"
echo "  2. Start FL training from any bank's frontend"
echo "  3. Training will begin from Round 1"
echo ""
