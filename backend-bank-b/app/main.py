# main.py
# FastAPI application entry point.
# Defines the app instance, includes all routers (auth, client, staff, FL).
# Configures CORS for frontend, middleware for logging/security.
# Runs with: uvicorn app.main:app --reload
# This is the central hub connecting all API modules.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CashFlow - Alternative Credit Scoring API",
    description="Privacy-preserving credit scoring with federated learning",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "CashFlow API",
        "status": "running",
        "version": "1.0.0"
    }

# Import and include routers
from app.api import auth, client_routes, staff_routes, fl_routes, scoring
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(client_routes.router, prefix="/api/client", tags=["client"])
app.include_router(staff_routes.router, prefix="/api/staff", tags=["staff"])
app.include_router(fl_routes.router, prefix="/api/fl", tags=["federated-learning"])
app.include_router(scoring.router, prefix="/api", tags=["scoring"])

# Auto-start FL model polling service on startup
@app.on_event("startup")
async def startup_event():
    """Auto-start background services on application startup"""
    from app.services.fl_model_poller import start_polling
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        start_polling()
        logger.info("✅ FL Model Polling Service auto-started")
    except Exception as e:
        logger.warning(f"⚠️  Could not start FL polling service: {e}")
