# app/main.py - FIXED IMPORTS

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import modules
from app.config import settings
from app.auth.sso_middleware import ApprovedUserMiddleware

# ✅ CORRECT IMPORTS - remove old secure_links and admin_send_proposal
from app.api import proposals, questions, users, admin, admin_read

# ✅ ADD THE NEW MODULE
from app.api import secure_access

from app.core.logging import setup_logging
from app.database import init_database

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Proposal Portal API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Frontend URL: {settings.FRONTEND_BASE_URL}")
    
    try:
        init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    logger.info("⏹️ Shutting down")

# Create FastAPI app
app = FastAPI(
    title="Proposal Portal API",
    description="SSO-enabled API with JWT temporary access",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://main.dnfe4l5bsjojn.amplifyapp.com",
        "http://localhost:5173",
        "http://localhost:8080",
        *settings.allowed_origins_list,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.add_middleware(
    ApprovedUserMiddleware,
    exempt_paths=[
        "/health", 
        "/docs", 
        "/redoc", 
        "/openapi.json", 
        "/",
        "/api/v1/debug/cors",
        "/admin/approved-users",
        "/admin/user-stats",
        "/api/v1/proposal/access",     # JWT-based access
        "/api/v1/admin/send-proposal",  # JWT generation
    ]
)

# Include routers
app.include_router(proposals.router, prefix="/api/v1", tags=["proposals"])
app.include_router(questions.router, prefix="/api/v1", tags=["questions"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(admin_read.router, prefix="/api/v1", tags=["admin-read"])

# ✅ NEW: JWT-based temporary access
app.include_router(secure_access.router, prefix="/api/v1", tags=["secure-access"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "jwt_temporary_access": True,
            "sso_validation": True,
            "cors_enabled": True,
        }
    }

@app.get("/")
async def root():
    return {
        "message": "Proposal Portal API v3.0",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )