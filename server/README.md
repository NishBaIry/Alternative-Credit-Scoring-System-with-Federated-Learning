# Federated Learning Server

FL aggregation server for credit scoring neural network using FedAvg algorithm.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup (from main-el/)
../setup_fl.sh

# Configure
nano .env

# Run server
python fl_server.py
```

Server starts on `http://0.0.0.0:5000`

## 📝 Configuration (.env)

```bash
# Minimum banks before aggregation
AGGREGATION_THRESHOLD=2

# Validate accuracy before replacing model
VALIDATE_BEFORE_REPLACE=True

# Server settings
FL_SERVER_HOST=0.0.0.0
FL_SERVER_PORT=5000

# Paths
BASE_MODEL_PATH=models/global_model.h5
GLOBAL_MODEL_PATH=models/global_model_latest.h5
VALIDATION_DATASET_PATH=../backend/data/bank_a/bank_a_fl_dataset.csv
```

## 📡 API Endpoints

### GET /
Server info and status

### GET /api/status
```json
{
  "status": "online",
  "current_round": 3,
  "clients_connected": 0,
  "pending_updates": [],
  "aggregation_threshold": 2,
  "total_aggregations": 3
}
```

### POST /api/upload_weights
Upload trained weights from bank client.

**Form Data:**
- `weights`: Binary file (.npz or .h5)
- `metadata`: JSON string with client info

**Response:**
```json
{
  "message": "Aggregation successful",
  "upload_id": "bank_a_20260117_143022.npz",
  "client_id": "bank_a",
  "round": 4,
  "new_model_available": true
}
```

### GET /api/download_global_model
Download latest global model.

**Query Params:**
- `client_id`: Bank identifier
- `format`: `file` or `bytes`

**Response:** Model file (.h5)

### POST /api/trigger_aggregation
Manually trigger aggregation (admin).

## 🔄 FL Workflow

1. **Wait for Banks:** Server waits for `AGGREGATION_THRESHOLD` banks to upload weights
2. **Aggregate:** Applies FedAvg weighted averaging
3. **Validate:** Evaluates accuracy on validation dataset
4. **Update:** Replaces global model only if accuracy improved
5. **Distribute:** Banks download new global model

## 📊 FedAvg Algorithm

```python
# Weighted average based on sample counts
w_new = Σ(w_i * n_i) / Σ(n_i)

# Example with 2 banks:
# Bank A: 35,000 samples, weights w_A
# Bank B: 35,000 samples, weights w_B
# Result: w_new = (w_A * 0.5) + (w_B * 0.5)
```

## 📁 Directory Structure

```
server/
├── fl_server.py          # Main Flask API server
├── fedavg.py             # FedAvg aggregation algorithm
├── requirements.txt      # Python dependencies
├── .env                  # Configuration
├── models/               # Model storage
│   ├── global_model.h5              # Base model
│   ├── global_model_latest.h5       # Current best model
│   └── global_model_round_*.h5      # Historical models
└── uploads/              # Client weight uploads
    └── bank_*_*.npz                 # Uploaded weights
```

## 🐛 Troubleshooting

**Base model not found:**
```bash
# Copy from outputs/
cp ../outputs/model.h5 models/global_model.h5
```

**Aggregation not triggering:**
```bash
# Check pending uploads
curl http://localhost:5000/api/status

# Manually trigger
curl -X POST http://localhost:5000/api/trigger_aggregation
```

**Accuracy validation failing:**
- Check `VALIDATION_DATASET_PATH` exists
- Ensure dataset has correct format (CSV with default_flag column)
- Set `VALIDATE_BEFORE_REPLACE=False` to disable validation

## 🔐 Security Notes

- Server accepts connections from any IP (0.0.0.0)
- No authentication implemented (add if needed)
- Suitable for trusted internal networks
- For production: Add API keys, HTTPS, rate limiting

## 📈 Monitoring

Server logs show detailed progress:
```
═══════════════════════════════════════════════════════════════════════
  📥 NEW BANK UPLOAD
═══════════════════════════════════════════════════════════════════════
  • Bank ID: bank_a
  • Bank Name: Bank A
  • Pending: 1/2 banks

═══════════════════════════════════════════════════════════════════════
  🔄 FEDERATED AGGREGATION (FedAvg)
═══════════════════════════════════════════════════════════════════════

▸ Participating Banks
  • Bank A (bank_a) - 35000 samples
  • Bank B (bank_b) - 35000 samples
  • Total: 2 banks

▸ Aggregation
  • Method: FedAvg (full weights)
  ✅ Aggregation computed successfully

▸ Model Validation
  • Evaluating OLD model...
    • Old Accuracy: 0.8961
  • Evaluating NEW model...
    • New Accuracy: 0.8987
  ✅ Improvement: +0.0026

▸ Saving Model
  ✅ Saved as: global_model_round_4_20260117_143525.h5 (2.35 MB)

═══════════════════════════════════════════════════════════════════════
  ✅ AGGREGATION COMPLETE - Round 4
═══════════════════════════════════════════════════════════════════════
```

## 🎯 Performance Tips

1. **Fast Aggregation:** Use SSD for model storage
2. **Network:** Gigabit ethernet for faster uploads
3. **Validation:** Disable if accuracy check not needed
4. **Cleanup:** Old models auto-deleted (keeps last 5)

## 📞 Support

See main documentation: `../FL_SETUP.md`
