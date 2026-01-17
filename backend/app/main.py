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
from app.api import auth, client_routes, staff_routes, fl_routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(client_routes.router, prefix="/api/client", tags=["client"])
app.include_router(staff_routes.router, prefix="/api/staff", tags=["staff"])
app.include_router(fl_routes.router, prefix="/api/fl", tags=["federated-learning"])
