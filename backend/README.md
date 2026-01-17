# CashFlow Backend

Alternative credit scoring API with privacy-preserving federated learning.

## Structure

```
app/
├── __init__.py
├── main.py              # FastAPI app entry point
├── config.py            # Configuration and settings
├── api/                 # API route handlers
│   ├── auth.py          # Authentication endpoints
│   ├── client_routes.py # Client-facing APIs
│   ├── staff_routes.py  # Staff-facing APIs
│   ├── scoring.py       # Scoring endpoints
│   ├── training.py      # Model training endpoints
│   └── fl_routes.py     # Federated learning endpoints
├── core/                # Core functionality
│   ├── security.py      # JWT and password hashing
│   ├── db.py           # Database operations
│   ├── schemas.py       # Pydantic models
│   └── models.py        # Data models
├── services/            # Business logic
│   ├── credit_model.py  # LightGBM scoring
│   ├── fl_engine.py     # Federated learning
│   ├── customer_service.py
│   ├── score_explain_service.py
│   └── audit_service.py
├── data/               # Bank data storage
│   ├── bank_a/
│   └── bank_b/
└── tests/              # Unit tests
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Access API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests:
```bash
pytest app/tests/
```

## Environment Variables

Create a `.env` file:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=optional
FL_SERVER_URL=http://localhost:8001
```

## API Endpoints

### Authentication
- POST `/api/auth/login/client` - Client login
- POST `/api/auth/login/staff` - Staff login

### Client Routes
- GET `/api/client/me/score` - Get my score
- GET `/api/client/me/score-details` - Score breakdown
- GET `/api/client/me/profile` - My profile

### Staff Routes
- GET `/api/staff/customers` - List customers
- POST `/api/staff/applications/score` - Score application
- GET `/api/staff/model/status` - Model metrics

### Federated Learning
- POST `/api/fl/send-update` - Send FL update
- GET `/api/fl/receive-global` - Get global model
