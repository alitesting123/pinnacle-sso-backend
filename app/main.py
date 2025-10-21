# app/main.py - COMPLETE UPDATED VERSION WITH JWT TEMPORARY ACCESS

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import modules
from app.config import settings
from app.auth.sso_middleware import ApprovedUserMiddleware

# API routers
from app.api import proposals, questions, users, admin, admin_read
from app.api import secure_access  # ✅ NEW: JWT temporary access module

from app.core.logging import setup_logging
from app.database import init_database

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# ============================================================================
# APPLICATION LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic"""
    logger.info("=" * 80)
    logger.info("🚀 Starting Proposal Portal API v3.0")
    logger.info("=" * 80)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Frontend URL: {settings.FRONTEND_BASE_URL}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    try:
        init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    logger.info("=" * 80)
    logger.info("🎯 Features Enabled:")
    logger.info("  • JWT Temporary Access (Stateless)")
    logger.info("  • SSO User Validation (Cognito)")
    logger.info("  • Proposal Management")
    logger.info("  • Q&A System")
    logger.info("=" * 80)
    
    yield
    
    logger.info("⏹️ Shutting down Proposal Portal API")

# ============================================================================
# CREATE FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Proposal Portal API",
    description="B2B Event Planning Proposal Management with JWT Temporary Access",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# 1. GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Production frontend
        "https://main.dnfe4l5bsjojn.amplifyapp.com",
        # Development frontends
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3000",
        # Additional origins from config
        *settings.allowed_origins_list,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# 3. Authentication Middleware (SSO)
app.add_middleware(
    ApprovedUserMiddleware,
    exempt_paths=[
        # Public endpoints
        "/health",
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        
        # CORS debug
        "/api/v1/debug/cors",
        
        # Admin read-only (no auth needed for listing)
        "/api/v1/admin/approved-users",
        "/api/v1/admin/user-stats",
        
        # ✅ JWT Temporary Access Endpoints (NO SSO REQUIRED)
        "/api/v1/proposal/access",          # Client validates JWT token
        "/api/v1/admin/send-proposal",      # Admin generates JWT link
        "/api/v1/proposal/token-info",      # Optional: Debug token info
    ]
)

# ============================================================================
# INCLUDE API ROUTERS
# ============================================================================

# Core proposal management
app.include_router(
    proposals.router, 
    prefix="/api/v1", 
    tags=["proposals"]
)

# Q&A system
app.include_router(
    questions.router, 
    prefix="/api/v1", 
    tags=["questions"]
)

# User management
app.include_router(
    users.router, 
    prefix="/api/v1", 
    tags=["users"]
)

# Admin endpoints (write operations - requires auth)
app.include_router(
    admin.router, 
    prefix="/api/v1", 
    tags=["admin"]
)

# Admin read-only endpoints
app.include_router(
    admin_read.router, 
    prefix="/api/v1", 
    tags=["admin-read"]
)

# ✅ NEW: JWT-based temporary access (stateless, no sessions)
app.include_router(
    secure_access.router, 
    prefix="/api/v1", 
    tags=["secure-access"]
)

logger.info("✅ All API routers registered")

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    Returns system status and feature flags
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "environment": settings.ENVIRONMENT,
        "database": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite",
        "features": {
            "jwt_temporary_access": True,      # ✅ Stateless link generation
            "sso_validation": True,            # ✅ Cognito integration
            "cors_enabled": True,              # ✅ Multi-origin support
            "proposal_management": True,       # ✅ Full CRUD operations
            "qa_system": True,                 # ✅ Client questions
            "email_notifications": True,       # ✅ Gmail SMTP
        },
        "endpoints": {
            "docs": "/docs" if settings.DEBUG else None,
            "health": "/health",
            "proposals": "/api/v1/proposals",
            "send_proposal": "/api/v1/admin/send-proposal",
            "access_proposal": "/api/v1/proposal/access/{token}"
        }
    }

@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Proposal Portal API v3.0 - JWT Temporary Access",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs" if settings.DEBUG else "Contact admin for API docs",
        "features": [
            "JWT-based temporary proposal access (24-hour links)",
            "Stateless authentication (no session management)",
            "Email notifications via Gmail SMTP",
            "Real-time proposal Q&A system",
            "Multi-venue event support",
            "Comprehensive labor scheduling"
        ]
    }

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    """
    Handle CORS preflight requests
    """
    return {"message": "OK"}

# ============================================================================
# DEBUG ENDPOINT (Development only)
# ============================================================================

if settings.DEBUG:
    @app.get("/api/v1/debug/cors")
    async def debug_cors(request: Request):
        """
        Debug CORS configuration
        Only available in development mode
        """
        return {
            "origin": request.headers.get("origin"),
            "host": request.headers.get("host"),
            "allowed_origins": settings.allowed_origins_list,
            "cors_configured": True
        }

# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting development server...")
    logger.info(f"API will be available at: http://localhost:8000")
    logger.info(f"API docs will be available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )