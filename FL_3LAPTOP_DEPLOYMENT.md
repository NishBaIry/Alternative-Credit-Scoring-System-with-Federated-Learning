# 3-Laptop Federated Learning Deployment Guide

Complete step-by-step guide for deploying the FL Credit Scoring system across 3 laptops:
- **Laptop 1**: FL Server (always online)
- **Laptop 2**: Bank A (Frontend + Backend + Local DB)
- **Laptop 3**: Bank B (Frontend + Backend + Local DB)

---

## 📋 Prerequisites

### All Laptops
1. **Anaconda/Miniconda installed**
2. **Git installed**
3. **Node.js 16+ and npm**
4. **Network connectivity** (all on same WiFi/LAN)

### Create Conda Environment (All Laptops)
```bash
conda create -n tensorflow_env python=3.9 -y
conda activate tensorflow_env
```

---

## 🖥️ LAPTOP 1: FL Server Setup

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd cashflow/server
```

### Step 2: Install Python Dependencies
```bash
conda activate tensorflow_env
pip install -r requirements.txt
```

### Step 3: Configure Server
Edit `server/.env`:
```bash
FL_SERVER_HOST=0.0.0.0
FL_SERVER_PORT=5000
AGGREGATION_THRESHOLD=2
VALIDATE_BEFORE_REPLACE=True
VALIDATION_DATASET_PATH=../backend/data/fl_dataset.csv
```

### Step 4: Prepare Base Model
Place your initial trained model at:
```bash
server/models/global_model.h5
```

### Step 5: Get Server IP Address
```bash
# Find your IP address
ip addr show | grep "inet "
# Or on macOS/Linux
ifconfig | grep "inet "

# Example output: 192.168.1.100
```

**Note this IP - you'll need it for bank configuration!**

### Step 6: Start FL Server
```bash
cd server
./start_fl_server.sh

# Or manually:
# conda activate tensorflow_env
# python fl_server.py
```

**Expected Output:**
```
========================================
🚀 FEDERATED LEARNING SERVER - CREDIT SCORING
========================================
✅ Base model found: models/global_model.h5
✅ Base model loaded successfully
========================================
Server Ready
========================================
🌐 FL Server running on 0.0.0.0:5000
```

**Keep this terminal running!**

### Verify Server
Open browser: `http://localhost:5000/api/status`

Should see:
```json
{
  "status": "online",
  "current_round": 0,
  "clients_connected": 0,
  "aggregation_threshold": 2
}
```

---

## 🏦 LAPTOP 2: Bank A Setup

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd cashflow
```

### Step 2: Backend Setup

#### Install Dependencies
```bash
cd backend
conda activate tensorflow_env
pip install -r requirements.txt
```

#### Configure FL Client
Edit `backend/.env.fl`:
```bash
BANK_ID=bank_a
BANK_NAME=Bank A
FL_SERVER_URL=http://192.168.1.100:5000  # ⚠️ Use FL Server's IP!
LOCAL_DATASET_PATH=data/fl_dataset.csv
FL_EPOCHS=10
FL_BATCH_SIZE=256
FL_LEARNING_RATE=0.001
```

#### Prepare Bank A Dataset
Place Bank A's data at:
```bash
backend/data/fl_dataset.csv
# Should contain ~35,000 customer records
```

#### Start Backend
```bash
cd backend
./start_backend.sh

# Or manually:
# conda activate tensorflow_env
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
========================================
Backend API Startup Script
========================================
✅ Conda environment activated: tensorflow_env
✅ FL configuration found: .env.fl
========================================
Starting Backend API on 0.0.0.0:8000
========================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Frontend Setup

Open **new terminal**:

```bash
cd cashflow/frontend-bank-a
```

#### Install Dependencies
```bash
npm install
```

#### Configure Frontend
Edit `frontend-bank-a/.env`:
```bash
VITE_API_URL=http://localhost:8000
VITE_BANK_NAME=Bank A
VITE_BANK_ID=bank_a
```

#### Start Frontend
```bash
npm run dev
```

**Expected Output:**
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.1.101:5173/
```

### Step 4: Verify Bank A Setup

1. Open browser: `http://localhost:5173`
2. Navigate to "Model Training" page
3. Check "FL Server Status" - should show "online"

---

## 🏦 LAPTOP 3: Bank B Setup

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd cashflow
```

### Step 2: Backend Setup

#### Install Dependencies
```bash
cd backend
conda activate tensorflow_env
pip install -r requirements.txt
```

#### Configure FL Client
Edit `backend/.env.fl`:
```bash
BANK_ID=bank_b
BANK_NAME=Bank B
FL_SERVER_URL=http://192.168.1.100:5000  # ⚠️ Use FL Server's IP!
LOCAL_DATASET_PATH=data/fl_dataset.csv
FL_EPOCHS=10
FL_BATCH_SIZE=256
FL_LEARNING_RATE=0.001
```

#### Prepare Bank B Dataset
Place Bank B's data at:
```bash
backend/data/fl_dataset.csv
# Should contain ~35,000 customer records (different from Bank A!)
```

#### Start Backend
```bash
cd backend
./start_backend.sh 0.0.0.0 8001  # Use different port!

# Or manually:
# conda activate tensorflow_env
# uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Step 3: Frontend Setup

Open **new terminal**:

```bash
cd cashflow/frontend-bank-b
```

#### Install Dependencies
```bash
npm install
```

#### Configure Frontend
Edit `frontend-bank-b/.env`:
```bash
VITE_API_URL=http://localhost:8001
VITE_BANK_NAME=Bank B
VITE_BANK_ID=bank_b
```

#### Start Frontend
```bash
npm run dev --port 5174  # Different port!
```

### Step 4: Verify Bank B Setup

1. Open browser: `http://localhost:5174`
2. Navigate to "Model Training" page
3. Check "FL Server Status" - should show "online"

---

## 🚀 Running FL Training Workflow

### Phase 1: Bank A Trains

**On Laptop 2 (Bank A):**

1. Open browser: `http://localhost:5173`
2. Go to "Model Training" page
3. Click **"🚀 Start FL Training"**

**What Happens:**
```
✓ Downloads global model from server
✓ Trains on Bank A's 35,000 records (10 epochs)
✓ Uploads trained weights to FL server
✓ Starts auto-polling for new model
✓ Status: "Waiting for 1 more bank..."
```

**FL Server Log (Laptop 1):**
```
📥 NEW BANK UPLOAD
• Bank ID: bank_a
• Bank Name: Bank A
• File Size: 2.34 MB
✅ Saved to: bank_a_20260119_143022_client_weights.npz
• Pending: 1/2 banks
⏳ Waiting for 1 more bank(s)...
```

### Phase 2: Bank B Trains

**On Laptop 3 (Bank B):**

1. Open browser: `http://localhost:5174`
2. Go to "Model Training" page
3. Click **"🚀 Start FL Training"**

**What Happens:**
```
✓ Downloads global model from server
✓ Trains on Bank B's 35,000 records (10 epochs)
✓ Uploads trained weights to FL server
✓ Server triggers aggregation automatically!
```

**FL Server Log (Laptop 1):**
```
📥 NEW BANK UPLOAD
• Bank ID: bank_b
• Bank Name: Bank B
✅ Threshold reached! Starting aggregation...

🔄 FEDERATED AGGREGATION (FedAvg)
Participating Banks:
  • Bank A (bank_a) - 35000 samples
  • Bank B (bank_b) - 35000 samples
  • Total: 2 banks

Aggregation:
  • Method: FedAvg (full weights)
✅ Aggregation computed successfully

Model Validation (AUC-Based):
  • Evaluating OLD model...
    Old AUC: 0.8961 | Accuracy: 0.8961
  • Evaluating NEW model...
    New AUC: 0.9034 | Accuracy: 0.9010
✅ AUC Improvement: +0.0073

Saving Model:
✅ Saved as: global_model_round_1_20260119_143530.h5 (2.45 MB)

✅ AGGREGATION COMPLETE - Round 1
```

### Phase 3: Auto-Download New Model

**On Both Bank Laptops (Automatically):**

The backend polling service detects the new model and downloads it:

```
🆕 New model available! Round 1 (current: 0)
✅ Model downloaded and activated!
   Round: 1
   Size: 2.45 MB
   Active: models/active_model.h5
   Scoring service updated with new model
```

**Frontend shows:**
```
✅ NEW MODEL ACTIVATED (Round 1)
Size: 2.45 MB
```

---

## ✅ Verification Checklist

### FL Server (Laptop 1)
- [ ] Server running on port 5000
- [ ] `/api/status` returns `"status": "online"`
- [ ] `models/global_model.h5` exists
- [ ] Can see server logs

### Bank A (Laptop 2)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] FL configuration points to server IP
- [ ] Dataset exists at `backend/data/fl_dataset.csv`
- [ ] Can access frontend in browser

### Bank B (Laptop 3)
- [ ] Backend running on port 8001
- [ ] Frontend running on port 5174
- [ ] FL configuration points to server IP
- [ ] Dataset exists at `backend/data/fl_dataset.csv`
- [ ] Can access frontend in browser

### FL Workflow
- [ ] Bank A can start training
- [ ] Bank B can start training
- [ ] Server aggregates after both upload
- [ ] New model improves AUC
- [ ] Both banks auto-download new model
- [ ] Scoring service uses new model

---

## 🔧 Troubleshooting

### Server Connection Failed

**Problem:** Banks can't connect to FL server

**Solutions:**
1. Check server IP: `ip addr show` or `ifconfig`
2. Verify firewall allows port 5000
3. Ensure all laptops on same network
4. Test connection: `curl http://SERVER_IP:5000/api/status`
5. Update `.env.fl` with correct server IP

### Model Not Found

**Problem:** "No model file found"

**Solutions:**
1. Place base model at `server/models/global_model.h5`
2. Check file permissions
3. Verify model format (.h5 file)

### Training Fails

**Problem:** Training crashes or times out

**Solutions:**
1. Check dataset exists: `ls backend/data/fl_dataset.csv`
2. Verify conda environment: `conda activate tensorflow_env`
3. Check dependencies: `pip install -r requirements.txt`
4. Review backend logs for errors

### Aggregation Not Triggered

**Problem:** Both banks trained but no aggregation

**Solutions:**
1. Check `AGGREGATION_THRESHOLD` in server `.env` (should be 2)
2. Verify both uploads successful in server logs
3. Check server logs for errors

### Auto-Polling Not Working

**Problem:** New model not auto-downloaded

**Solutions:**
1. Check backend logs for polling service status
2. Verify polling started: Check "Backend Polling Status" in frontend
3. Manually trigger: Click "Resume Auto-Polling" in frontend
4. Check network connectivity to server

---

## 📊 Expected Results

### Round 1 (After 2 Banks Train)
- **Base Model AUC:** ~0.896
- **New Model AUC:** ~0.903-0.910 (+0.7-1.4%)
- **Training Time:** 5-10 minutes per bank
- **Model Size:** ~2-3 MB

### Round 2 (Optional - Both Banks Train Again)
- **Previous AUC:** ~0.903
- **New Model AUC:** ~0.908-0.915
- **Incremental Improvement:** +0.5-1.2%

---

## 🎯 Key Features Demonstrated

✅ **Privacy-Preserving:** No raw data shared between banks
✅ **AUC-Based Validation:** Only updates if model improves
✅ **Automatic Aggregation:** Triggers when threshold reached
✅ **Auto-Download:** Banks automatically get new models
✅ **Real-Time Monitoring:** Live FL status in frontend
✅ **Conda Integration:** Uses tensorflow_env for consistency

---

## 📝 Quick Command Reference

### Start FL Server
```bash
cd server && ./start_fl_server.sh
```

### Start Bank Backend
```bash
cd backend && ./start_backend.sh [host] [port]
```

### Start Bank Frontend
```bash
cd frontend-bank-a && npm run dev
```

### Manual FL Training
```bash
cd backend && ./run_fl_training.sh
```

### Check Server Status
```bash
curl http://SERVER_IP:5000/api/status
```

### Check Backend Status
```bash
curl http://localhost:8000/api/fl/fl-status
```

---

## 🎓 For Demo/Presentation

### Recommended Order:
1. **Start FL Server** (Laptop 1) - Show server logs
2. **Start Bank A** (Laptop 2) - Show frontend
3. **Start Bank B** (Laptop 3) - Show frontend
4. **Train Bank A** - Show training progress
5. **Train Bank B** - Show aggregation trigger
6. **Show Results** - Compare AUC improvement
7. **Demo Scoring** - Show new model in use

### Key Points to Highlight:
- No data leaves the banks (only weights shared)
- Server validates AUC before replacing model
- Automatic model distribution
- Real-time FL status monitoring
- Production-ready with conda environments

---

## 📚 Additional Resources

- `FL_IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `FL_QUICKSTART.md` - Quick testing guide
- `server/README.md` - Server-specific documentation
- `backend/FL_CLIENT_README.md` - Client documentation

---

**Need Help?** Check logs in each terminal for detailed error messages!
