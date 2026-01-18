# FL Quick Reference Card

## 🚀 Starting Services (with Conda)

### FL Server (Laptop 1)
```bash
cd ~/cashflow/server
./start_fl_server.sh
# Server: http://0.0.0.0:5000
```

### Bank A Backend (Laptop 2)
```bash
cd ~/cashflow/backend
./start_backend.sh
# Backend: http://0.0.0.0:8000
```

### Bank A Frontend (Laptop 2)
```bash
cd ~/cashflow/frontend-bank-a
npm run dev
# Frontend: http://localhost:5173
```

### Bank B Backend (Laptop 3)
```bash
cd ~/cashflow/backend
./start_backend.sh 0.0.0.0 8001
# Backend: http://0.0.0.0:8001
```

### Bank B Frontend (Laptop 3)
```bash
cd ~/cashflow/frontend-bank-b
npm run dev -- --port 5174
# Frontend: http://localhost:5174
```

---

## 🔧 Configuration Files

### Server: `server/.env`
```bash
FL_SERVER_HOST=0.0.0.0
FL_SERVER_PORT=5000
AGGREGATION_THRESHOLD=2
VALIDATE_BEFORE_REPLACE=True
```

### Bank A: `backend/.env.fl`
```bash
BANK_ID=bank_a
BANK_NAME=Bank A
FL_SERVER_URL=http://192.168.1.100:5000  # Server IP!
LOCAL_DATASET_PATH=data/fl_dataset.csv
```

### Bank B: `backend/.env.fl`
```bash
BANK_ID=bank_b
BANK_NAME=Bank B
FL_SERVER_URL=http://192.168.1.100:5000  # Server IP!
LOCAL_DATASET_PATH=data/fl_dataset.csv
```

---

## 📡 API Endpoints

### FL Server
- `GET /api/status` - Server status
- `POST /api/upload_weights` - Upload trained weights
- `GET /api/download_global_model` - Download global model
- `GET /api/model_version` - Check model version

### Bank Backend
- `POST /api/fl/train` - Start FL training
- `GET /api/fl/fl-status` - FL server status
- `POST /api/fl/start-polling` - Start auto-polling
- `POST /api/fl/stop-polling` - Stop auto-polling
- `GET /api/fl/polling-status` - Polling status
- `GET /api/fl/local-model-info` - Local model info
- `POST /api/score/reload-model` - Reload scoring model

---

## 🔍 Testing Commands

### Check Server Status
```bash
curl http://SERVER_IP:5000/api/status
```

### Check Bank Backend
```bash
curl http://localhost:8000/api/fl/fl-status
```

### Check Polling Status
```bash
curl http://localhost:8000/api/fl/polling-status
```

### Manual FL Training (Backend)
```bash
cd backend
./run_fl_training.sh
```

---

## 📊 What to Monitor

### FL Server Terminal
```
✅ Base model loaded successfully
📥 NEW BANK UPLOAD - Bank A
📥 NEW BANK UPLOAD - Bank B
✅ Threshold reached! Starting aggregation...
Old AUC: 0.8961 | New AUC: 0.9034
✅ AUC Improvement: +0.0073
✅ AGGREGATION COMPLETE - Round 1
```

### Bank Backend Terminal
```
✅ FL training completed and weights uploaded
Backend polling service started
🆕 New model available! Round 1
✅ Model downloaded and activated!
Scoring service updated with new model
```

### Frontend (Model Training Page)
```
✅ FL Server Status: online
✅ Auto-polling active (green indicator)
✅ Backend Polling Status: 🟢 Running
✅ NEW MODEL ACTIVATED (Round 1)
```

---

## 🎯 Workflow

1. **Start FL Server** (always on)
2. **Start Bank A** (backend + frontend)
3. **Start Bank B** (backend + frontend)
4. **Bank A → Click "Start FL Training"**
   - Downloads model
   - Trains locally (10 epochs)
   - Uploads weights
   - Starts auto-polling
5. **Bank B → Click "Start FL Training"**
   - Downloads model
   - Trains locally (10 epochs)
   - Uploads weights
   - Triggers aggregation
6. **Server Aggregates**
   - FedAvg algorithm
   - AUC validation
   - Saves new model
7. **Banks Auto-Download**
   - Detect new model
   - Download automatically
   - Activate for scoring

---

## ⚠️ Troubleshooting

### Can't Connect to Server
```bash
# Get server IP
ip addr show | grep "inet "

# Test connection
curl http://SERVER_IP:5000/api/status

# Check firewall
sudo ufw allow 5000
```

### Training Fails
```bash
# Check conda env
conda activate tensorflow_env

# Check dataset
ls backend/data/fl_dataset.csv

# Check dependencies
pip install -r backend/requirements.txt
```

### Polling Not Working
```bash
# Check polling status
curl http://localhost:8000/api/fl/polling-status

# Restart polling
curl -X POST http://localhost:8000/api/fl/start-polling
```

---

## 📁 Important Files

### Models
- `server/models/global_model.h5` - Base model (initial)
- `server/models/global_model_latest.h5` - Current best
- `backend/models/active_model.h5` - Active scoring model

### Datasets
- `backend/data/fl_dataset.csv` - Bank's local data

### Logs
- Check terminal outputs for all services

---

## 🎓 Key Metrics

### Model Performance
- **Base AUC:** ~0.896
- **Round 1 AUC:** ~0.903-0.910 (improvement!)
- **Round 2 AUC:** ~0.910-0.915

### Training Time
- **Per Bank:** 5-10 minutes
- **Aggregation:** 1-2 minutes
- **Auto-Download:** 5-10 seconds

### File Sizes
- **Model:** ~2-3 MB
- **Weights:** ~2-3 MB
- **Dataset:** Varies (35k records ≈ 5-10 MB)

---

## ✅ Pre-Flight Checklist

- [ ] Conda environment `tensorflow_env` created
- [ ] All dependencies installed
- [ ] Server has base model
- [ ] Banks have datasets
- [ ] `.env.fl` configured with server IP
- [ ] All laptops on same network
- [ ] Ports available (5000, 8000, 8001, 5173, 5174)

---

## 🚦 Quick Commands

```bash
# Activate conda
conda activate tensorflow_env

# Start everything (separate terminals)
cd server && ./start_fl_server.sh
cd backend && ./start_backend.sh
cd frontend-bank-a && npm run dev

# Check status
curl http://localhost:5000/api/status
curl http://localhost:8000/api/fl/fl-status

# Manual training
cd backend && ./run_fl_training.sh
```

---

**📖 Full Documentation:** See `FL_3LAPTOP_DEPLOYMENT.md`
