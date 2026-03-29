# CashFlow - Alternative Credit Scoring Platform

Privacy-preserving credit scoring system using alternative data and federated learning.

## 🎯 Project Overview

CashFlow is an **AI for Social Good** project that provides alternative credit scoring for thin-file borrowers (students, gig workers, self-employed) who lack traditional credit histories. The system uses:

- **Alternative Data**: UPI transactions, utility bill payments, behavioral patterns
- **LightGBM Model**: Gradient boosting for accurate default prediction
- **Federated Learning**: Privacy-preserving collaborative training across banks
- **Differential Privacy**: Mathematical guarantees for data protection

## 🏗️ Project Structure

```
cashflow/
├── frontend-client/   # React UI - Client Portal (Port 3000)
│   ├── src/
│   │   ├── pages/     # Client pages only
│   │   ├── components/ # Reusable UI components
│   │   ├── hooks/     # Custom React hooks
│   │   ├── lib/       # API client & utilities
│   │   └── context/   # Global state management
│   └── .env           # Client config
│
├── frontend-bank-a/   # React UI - Bank A Staff Portal (Port 3001)
│   ├── src/
│   │   ├── pages/     # Staff pages only
│   │   └── ...
│   └── .env           # Bank A config (hardcoded bank_id)
│
├── frontend-bank-b/   # React UI - Bank B Staff Portal (Port 3002)
│   ├── src/
│   │   ├── pages/     # Staff pages only
│   │   └── ...
│   └── .env           # Bank B config (hardcoded bank_id)
│
├── backend/           # FastAPI Python backend (Port 8000)
│   ├── app/
│   │   ├── api/       # REST API endpoints
│   │   ├── core/      # Security, DB, schemas
│   │   ├── services/  # Business logic
│   │   ├── data/      # Bank datasets
│   │   └── tests/     # Unit tests
│   └── requirements.txt
│
└── package.json       # Monorepo scripts
```

## 🚀 Quick Start

### Install All Dependencies

```bash
npm run install-all
```

### Run All Services (Federated Learning Demo)

```bash
npm run dev
```

This starts all 4 services:
- **Client Portal** → http://localhost:3000
- **Bank A Staff** → http://localhost:3001  
- **Bank B Staff** → http://localhost:3002
- **Backend API** → http://localhost:8000 (docs: /docs)

### Run Individual Services

```bash
# Client Portal only
npm run client

# Bank A Staff Portal only
npm run bank-a

# Bank B Staff Portal only
npm run bank-b

# Backend only
npm run backend
```

## 📱 Architecture

### 3-Frontend Design for FL Demo

This project uses **3 separate frontend applications** to demonstrate federated learning effectively:

1. **frontend-client** (Port 3000)
   - Multi-tenant client portal
   - Bank selection flow
   - Client login and dashboard
   - View credit scores and recommendations

2. **frontend-bank-a** (Port 3001)
   - Bank A staff portal (single-tenant)
   - Hardcoded `bank_id=bank_a`
   - Staff dashboard and customer management
   - Local model training for Bank A data

3. **frontend-bank-b** (Port 3002)
   - Bank B staff portal (single-tenant)
   - Hardcoded `bank_id=bank_b`
   - Staff dashboard and customer management
   - Local model training for Bank B data

**Why 3 Frontends?**
- Demonstrates FL collaboration visually (side-by-side browsers)
- Clean separation of concerns (client vs bank portals)
- Proper bank data isolation (no accidental cross-bank access)
- Realistic multi-organization deployment scenario

## 📱 User Interfaces

### Client UI (Borrowers)
- **Bank Selection**: Choose your bank
- **Login**: Customer ID + password
- **Dashboard**: View your Alternative Credit Score (300-900)
- **Score Details**: Understand factors affecting your score
- **Recommendations**: Get actionable tips to improve
- **Profile**: View and edit your information

### Staff UI (Bank Personnel)
- **Login**: Username + password with role (Admin/Analyst)
- **Dashboard**: Overview metrics and navigation
- **Customer List**: View all customers with scores
- **Customer Detail**: Deep dive into individual profiles
- **Score Application**: Score new loan applications
- **Model Training**: Train local models and participate in FL
- **Analytics**: Feature importance, fairness metrics

## 🔐 Privacy & Security

- **Data Locality**: Customer data never leaves the bank
- **Federated Learning**: Only model updates are shared (not raw data)
- **Differential Privacy**: Noise added to prevent data leakage
- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt for secure password storage

## 🎓 Key Features

1. **Alternative Data Scoring**
   - UPI transaction patterns
   - Utility bill payment history
   - Behavioral spending ratios
   - Cash flow consistency

2. **Explainability**
   - Top factors driving score
   - Natural language explanations
   - Actionable recommendations
   - SHAP values (optional)

3. **Federated Learning**
   - Multi-bank collaboration
   - Privacy-preserving aggregation
   - Improved model accuracy
   - Compliance with data regulations

4. **Financial Inclusion**
   - Score thin-file borrowers
   - No traditional credit history required
   - Fair and transparent decisions
   - Reduces bias from legacy systems

## 🧪 Testing

### Frontend
```bash
cd frontend
npm run test  # (when tests are added)
```

### Backend
```bash
cd backend
pytest app/tests/
```

## 📊 Technology Stack

**Frontend:**
- React 18
- Vite
- TailwindCSS 3
- React Router
- Axios

**Backend:**
- FastAPI
- LightGBM
- Pandas & NumPy
- JWT Authentication
- Pydantic

## 🎯 Use Cases

1. **Students**: First loan without credit history
2. **Gig Workers**: Income from multiple platforms
3. **Self-Employed**: Non-traditional income sources
4. **Thin-File Borrowers**: Limited credit bureau records

## 📈 Future Enhancements

- Real-time UPI integration
- SHAP-based explanations
- Advanced fairness metrics
- Production database (PostgreSQL)
- Docker containerization
- CI/CD pipeline


