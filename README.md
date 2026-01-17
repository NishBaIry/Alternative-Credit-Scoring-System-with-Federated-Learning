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
├── frontend/          # React + Vite + TailwindCSS UI
│   ├── src/
│   │   ├── pages/     # Client & Staff pages
│   │   ├── components/ # Reusable UI components
│   │   ├── hooks/     # Custom React hooks
│   │   ├── lib/       # API client & utilities
│   │   └── context/   # Global state management
│   └── ...
│
├── backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── api/       # REST API endpoints
│   │   ├── core/      # Security, DB, schemas
│   │   ├── services/  # Business logic
│   │   ├── data/      # Bank datasets
│   │   └── tests/     # Unit tests
│   └── requirements.txt
│
└── README.md
```

## 🚀 Quick Start

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:3000

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000
API docs: http://localhost:8000/docs

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

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 🙏 Acknowledgments

Built for demonstrating AI for Social Good principles in financial inclusion.

---

**Note**: This is a demonstration project for hackathons/learning. For production use, additional security hardening, compliance reviews, and regulatory approvals are required.
