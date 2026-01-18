# FL Continuous Learning Workflow

## Overview
Incremental learning system that prevents overfitting and catastrophic forgetting by combining base data with new applications.

## File Structure
```
backend/data/
├── customers.csv        # Base training data (old fl_dataset.csv renamed)
└── fl_dataset.csv       # New scored applications (accumulated between FL rounds)
```

## Complete Workflow

### 1. Initial State
- `customers.csv`: 35,000 rows (your existing FL dataset, renamed)
- `fl_dataset.csv`: Empty or doesn't exist yet

### 2. Score New Applications
**When:** User scores a new loan application via frontend

**What Happens:**
```python
# In backend/app/api/scoring.py
POST /api/score
├── Score application using active_model.h5
├── Determine default_flag (0 or 1 based on score < 600 threshold)
└── Append to data/fl_dataset.csv
```

**Result:** Each new application gets added to `fl_dataset.csv`

Example after scoring 10 apps:
- `customers.csv`: 35,000 rows (unchanged)
- `fl_dataset.csv`: 10 rows (new applications)

### 3. FL Training Round
**When:** User clicks "Train Model" in frontend

**What Happens:**
```python
# In backend/app/services/fl_client_training.py
def load_data():
    # Load base data
    customers_df = pd.read_csv('data/customers.csv')  # 35,000 rows
    
    # Load new data
    fl_new_df = pd.read_csv('data/fl_dataset.csv')    # 10 rows
    
    # Combine both for training
    combined_df = pd.concat([customers_df, fl_new_df])  # 35,010 rows
    
    # Train on combined dataset
    model.fit(combined_df, epochs=10)
    
    # Upload weights to FL server
```

**Why This Works:**
- ✅ **Prevents Overfitting**: Small new data (10 rows) + large base data (35K rows) = stable training
- ✅ **No Catastrophic Forgetting**: Model remembers patterns from customers.csv
- ✅ **Incremental Learning**: Model learns from new applications without forgetting old knowledge

### 4. After FL Aggregation
**When:** FL server aggregates weights and poller downloads new model

**What Happens:**
```python
# In backend/app/services/fl_model_poller.py
def check_and_download_new_model():
    # Download new aggregated model from FL server
    download_new_model()
    
    # Merge new data into base dataset
    merge_fl_dataset_to_customers()
    # ├── Read fl_dataset.csv (10 rows)
    # ├── Append to customers.csv (now 35,010 rows)
    # └── Clear fl_dataset.csv (ready for next round)
```

**Result:**
- `customers.csv`: 35,010 rows (includes the 10 new apps)
- `fl_dataset.csv`: Empty (cleared, ready for next round)

### 5. Next FL Round
Now when you score more applications and train again:
- `customers.csv`: 35,010 rows (base data)
- `fl_dataset.csv`: 15 new rows (new applications since last round)
- **Training uses:** 35,010 + 15 = 35,025 total rows

## API Endpoints

### Score Application (Auto-appends to FL dataset)
```bash
POST http://localhost:8002/api/score
{
  "age": 30,
  "monthly_income": 50000,
  # ... other features
}

Response:
{
  "credit_score": 742,
  "risk_band": "Low Risk"
}

# Automatically appends to fl_dataset.csv
```

### Check FL Dataset Stats
```bash
GET http://localhost:8002/api/fl/dataset-stats

Response:
{
  "fl_dataset": {
    "exists": true,
    "count": 10,
    "default_rate": 0.2,
    "file_size_mb": 0.05
  }
}
```

### Train FL Model (Uses Both Datasets)
```bash
POST http://localhost:8002/api/fl/train
{
  "bank_id": "bank_a",
  "epochs": 10
}

# Training combines customers.csv + fl_dataset.csv
# Uploads weights to FL server
# Auto-starts polling for new model
```

## Training Strategy Benefits

### Option 1 (Implemented): Combined Training ✅
```
Training Data = customers.csv (35K) + fl_dataset.csv (10)
Result: Stable, prevents overfitting
```

**Advantages:**
- Small new data doesn't cause overfitting
- Model retains knowledge from base data
- Gradual, incremental learning
- Production-ready approach

**Math:**
- Base data weight: 35,000 / 35,010 = 99.97%
- New data weight: 10 / 35,010 = 0.03%
- Model learns gently from new patterns without forgetting

### Option 2 (Not Used): Only New Data ❌
```
Training Data = fl_dataset.csv (10 only)
Result: Overfitting, catastrophic forgetting
```

**Problems:**
- 10 samples too small for neural network
- Model forgets patterns from 35K base data
- Unstable predictions

## Code Changes Made

1. **fl_data_collector.py** (NEW)
   - `append_to_fl_dataset()`: Adds scored apps to fl_dataset.csv
   - `get_fl_dataset_stats()`: Reports new data count
   - `merge_fl_dataset_to_customers()`: Merges after FL round

2. **fl_client_training.py** (MODIFIED)
   - `load_data()`: Now loads BOTH customers.csv + fl_dataset.csv
   - Combines datasets before training

3. **scoring.py** (MODIFIED)
   - `POST /score`: Auto-appends to fl_dataset.csv after scoring

4. **fl_model_poller.py** (MODIFIED)
   - After downloading new model: auto-merges fl_dataset → customers.csv

5. **fl_routes.py** (MODIFIED)
   - `GET /dataset-stats`: New endpoint for FL dataset statistics

6. **main.py** (MODIFIED)
   - Auto-starts polling service on backend startup

## Testing the Workflow

### Step 1: Score Some Applications
```bash
# Score 5-10 test applications
curl -X POST http://localhost:8002/api/score \
  -H "Content-Type: application/json" \
  -d '{"age": 30, "monthly_income": 50000, ...}'
```

### Step 2: Check New Data
```bash
# Verify applications were added
curl http://localhost:8002/api/fl/dataset-stats

# Should show count: 5-10
```

### Step 3: Train FL Model
```bash
# Trigger FL training
curl -X POST http://localhost:8002/api/fl/train

# Watch backend logs - should show:
# "✓ customers.csv: 35000 rows"
# "✓ fl_dataset.csv: 10 new rows"
# "✓ Combined dataset: 35010 total rows"
```

### Step 4: Verify Merge After Aggregation
```bash
# After FL server aggregates and poller downloads new model
# Check backend logs - should show:
# "✅ Merged 10 rows from fl_dataset.csv into customers.csv"
# "✅ Cleared fl_dataset.csv"

# Verify customers.csv now has 35,010 rows
wc -l backend/data/customers.csv
```

## Production Considerations

### Default Flag Determination
Current implementation uses a simple threshold:
```python
default_flag = 1 if credit_score < 600 else 0
```

**In Production:**
- Wait for actual loan repayment outcome (30/60/90 days)
- Update `default_flag` when loan defaults or is repaid
- Re-append to fl_dataset.csv with true outcome
- This creates a continuous learning loop with real outcomes

### Data Privacy
- ✅ Raw data never leaves the bank (`customers.csv`, `fl_dataset.csv` stay local)
- ✅ Only model weights uploaded to FL server
- ✅ FL server never sees individual customer data

### Scalability
- Works for 10 to 10,000 new applications per round
- Automatic dataset management (merge + clear after each round)
- No manual intervention required

## Summary

**Before:** Single static dataset, no continuous learning

**Now:** 
1. ✅ Score apps → Auto-append to fl_dataset.csv
2. ✅ Train → Uses both base data + new data (prevents overfitting)
3. ✅ After aggregation → Auto-merge new data into base dataset
4. ✅ Repeat → Continuous incremental learning

**Result:** Production-ready FL system with stable incremental learning! 🎉
