# Backend Setup & Startup Instructions

## ✅ Completed Setup

All backend components have been updated to use:
- **SQLite databases**: `data/bank_a.db` and `data/bank_b.db` (35,000 customers each)
- **Trained NN model**: `models/model.h5` with scaler and encoders
- **Alternative Credit Score**: Formula `300 + 600 * (1 - p_default)`

## 🚀 Start the Backend

### 1. Activate the TensorFlow environment:
```bash
cd /home/nishanth/cashflow/backend
conda activate tensorflow_env
```

### 2. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

Or use the startup script:
```bash
chmod +x start_backend.sh
./start_backend.sh
```

## 📊 Database Structure

- **Bank A**: `/home/nishanth/cashflow/backend/data/bank_a.db` (35,000 customers)
- **Bank B**: `/home/nishanth/cashflow/backend/data/bank_b.db` (35,000 customers)

### Sample Customer Login:
- Username: `00000001`
- Password: `00000001` (SHA256 hashed in database)

## 🔧 Model Files

Located in `models/`:
- `model.h5` - Full Keras model (2.4 MB)
- `model.weights.h5` - Weights only for FL
- `scaler.pkl` - StandardScaler for features
- `encoders.pkl` - LabelEncoders for categorical features (gender, marital_status, education)

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login/client` - Customer login
- `POST /api/auth/login/staff` - Staff login (admin/admin123)

### Customer Operations
- `GET /api/staff/customers?bank_id=bank_a` - List customers
- `GET /api/staff/customers/{customer_id}?bank_id=bank_a` - Get customer details
- `POST /api/staff/applications/score?bank_id=bank_a` - Score application

### Scoring
- `POST /api/score` - Score feature vector
- `POST /api/score/customer/{customer_id}?bank_id=bank_a` - Score specific customer
- `GET /api/score/model-info` - Get model information

## ⚠️ Known Issues

### GPU/CUDA Issues
The model has CUDA libdevice issues with BatchNormalization layers. Currently configured to use CPU execution with `tf.device('/CPU:0')`.

If you encounter JIT compilation errors, the fallback values are:
- Score: 400
- Risk: High  
- P(default): 0.83

To fully resolve, either:
1. Use CPU-only: `export CUDA_VISIBLE_DEVICES=-1`
2. Or retrain the model without BatchNormalization layers
3. Or fix CUDA installation and libdevice paths

## 🧪 Testing

Test database connection:
```python
from app.core.db import db_manager
customer = db_manager.get_customer('bank_a', '00000001')
print(customer['customer_id'], customer['monthly_income'])
```

Test model loading:
```python
from app.services.nn_scoring_service import get_scoring_service
service = get_scoring_service()
print(service.get_model_info())
```

## 📝 Next Steps

1. Fix GPU/CUDA issues for proper predictions
2. Test all API endpoints with Postman/curl
3. Connect frontend-bank-a to backend
4. Implement FL training workflow
5. Add proper error handling and logging
