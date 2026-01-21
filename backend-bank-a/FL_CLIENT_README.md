# Backend - Bank FL Client

This folder contains everything a bank needs to participate in federated learning.

## 📁 What's Inside

```
backend/
├── models/
│   ├── global_model.h5            # Base neural network model (89.61% accuracy)
│   ├── train_neural_network.py    # Training script (if needed standalone)
│   ├── scaler.pkl                 # Feature scaler
│   └── encoders.pkl               # Categorical encoders
│
├── data/
│   ├── bank_a/
│   │   └── bank_a_fl_dataset.csv  # Bank A private dataset (35k samples)
│   └── bank_b/
│       └── bank_b_fl_dataset.csv  # Bank B private dataset (35k samples)
│
├── app/
│   ├── services/
│   │   └── fl_client_training.py  # FL training script (main)
│   └── api/
│       └── fl_routes.py           # FL API endpoints
│
├── .env.fl                        # FL configuration
└── requirements.txt               # Python dependencies
```

## 🚀 Quick Start for Banks

### Option 1: Direct Python Script (Recommended)

**Bank A:**
```bash
cd backend
python app/services/fl_client_training.py
```

**Bank B:**
```bash
cd backend
export BANK_ID=bank_b
export BANK_NAME="Bank B"
export LOCAL_DATASET_PATH=data/bank_b/bank_b_fl_dataset.csv
python app/services/fl_client_training.py
```

### Option 2: Via FastAPI

**Start backend server:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Trigger FL training:**
```bash
curl -X POST "http://localhost:8000/api/fl/train" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_id": "bank_a",
    "epochs": 10,
    "batch_size": 256,
    "learning_rate": 0.001
  }'
```

## ⚙️ Configuration (.env.fl)

```bash
# Bank Identity
BANK_ID=bank_a
BANK_NAME=Bank A

# FL Server (UPDATE THIS for multi-machine setup!)
FL_SERVER_URL=http://localhost:5000

# Local Dataset
LOCAL_DATASET_PATH=app/data/bank_a/bank_a_fl_dataset.csv

# Model Paths
BASE_MODEL_PATH=models/global_model.h5
LOCAL_MODEL_PATH=models/bank_a_finetuned.h5
WEIGHTS_UPLOAD_PATH=models/bank_a_weights.npz

# Training Hyperparameters
FL_EPOCHS=10
FL_BATCH_SIZE=256
FL_LEARNING_RATE=0.001
FL_VALIDATION_SPLIT=0.2
```

## 🏦 For Each Bank

Each bank gets:
1. **Base Model** (`models/global_model.h5`) - Pre-trained neural network
2. **Local Dataset** - Private customer data (35k samples)
3. **Training Script** - Fine-tunes model on local data
4. **Upload Script** - Sends weights to FL server

**Key Point:** Only model weights are uploaded, never customer data!

## 📊 What Happens During Training

1. **Download** global model from FL server (or use local base)
2. **Load** bank's private dataset (35k samples)
3. **Fine-tune** model for 10 epochs on local data
4. **Upload** trained weights to FL server
5. **Wait** for server aggregation
6. **Download** improved global model (next round)

## 🔐 Privacy

- ✅ Customer data stays in `data/bank_*/` (never uploaded)
- ✅ Only model weights uploaded (~2-3 MB)
- ✅ Server cannot reverse-engineer customer data
- ✅ Each bank trains independently on private data

## 🌐 Multi-Machine Setup

**If FL server is on different machine (e.g., 192.168.1.100):**

Edit `.env.fl`:
```bash
FL_SERVER_URL=http://192.168.1.100:5000
```

Or set environment variable:
```bash
export FL_SERVER_URL=http://192.168.1.100:5000
python app/services/fl_client_training.py
```

## 📈 Expected Performance

**Base Model (before FL):**
- Accuracy: 89.61%
- Trained centrally on 71k samples

**After FL Round 1:**
- Bank A fine-tunes on 35k samples
- Bank B fine-tunes on 35k samples
- Server aggregates → ~89.8-90.5% accuracy

**After FL Rounds 3-5:**
- Multiple aggregation cycles
- Expected: 90-91% accuracy
- Both banks benefit from collaborative learning!

## 🔧 Troubleshooting

**Can't connect to FL server:**
```bash
# Test connectivity
curl http://<server-ip>:5000/api/status

# Check FL_SERVER_URL in .env.fl
cat .env.fl | grep FL_SERVER_URL
```

**Dataset not found:**
```bash
# Verify dataset exists
ls -lh data/bank_a/bank_a_fl_dataset.csv
ls -lh data/bank_b/bank_b_fl_dataset.csv
```

**Model not found:**
```bash
# Verify base model exists
ls -lh models/global_model.h5

# Re-run setup if missing
cd ..
bash setup_fl.sh
```

## 📝 Files in `models/`

- **`global_model.h5`** - Base neural network (512→256→128→64→32 architecture)
- **`scaler.pkl`** - StandardScaler for feature normalization
- **`encoders.pkl`** - LabelEncoders for categorical variables
- **`train_neural_network.py`** - Original training script (reference)

These are used by `app/services/fl_client_training.py` during FL training.

## 🎯 Key Points

1. Each bank has identical folder structure
2. Only difference: Bank A uses `bank_a_fl_dataset.csv`, Bank B uses `bank_b_fl_dataset.csv`
3. Both banks use same base model to start
4. FL training script downloads latest global model automatically
5. After aggregation, both banks benefit from improved model

## 📚 Full Documentation

See main FL documentation:
- `../FL_SETUP.md` - Complete guide
- `../FL_QUICKSTART.md` - Quick testing
- `../FL_IMPLEMENTATION_SUMMARY.md` - What was built

## 🚀 Ready to Train!

Everything is set up. Just run:
```bash
python app/services/fl_client_training.py
```

And watch the magic happen! 🎉
