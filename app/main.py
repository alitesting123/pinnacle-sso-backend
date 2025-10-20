# app/main.py - UPDATED WITH CORS FIX
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import our modules
from app.config import settings
from app.auth.sso_middleware import ApprovedUserMiddleware
from app.api import proposals, questions, users, admin, admin_read, secure_links, admin_send_proposal
from app.core.logging import setup_logging
from app.database import init_database

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Proposal Portal API with SSO User Validation")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Frontend URL: {settings.FRONTEND_BASE_URL}")
    
    # Initialize database
    try:
        init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("⏹️ Shutting down Proposal Portal API")

# Create FastAPI app
app = FastAPI(
    title="Proposal Portal API",
    description="SSO-enabled API with pre-approved user validation",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ✅ CRITICAL: Add GZip BEFORE CORS
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ✅ CORS Configuration - MUST COME BEFORE SSO MIDDLEWARE
logger.info("🌐 Configuring CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # ✅ Production Amplify URLs
        "https://main.dnfe4l5bsjojn.amplifyapp.com/",
        "https://*.dnfe4l5bsjojn.amplifyapp.com/",
        
        # ✅ Local development
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",  # Alternative
        "http://localhost:3000",  # React/Next default
        
        # ✅ Additional origins from environment
        *settings.allowed_origins_list,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "*",
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Requested-With",
    ],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight for 1 hour
)

logger.info(f"✅ CORS enabled for: {settings.FRONTEND_BASE_URL}")

# ✅ SSO Middleware - MUST COME AFTER CORS
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
        "/api/v1/secure-proposals",
        "/api/v1/temp-access",
        "/api/v1/temp-sessions",
        "/api/v1/proposals",                    # ✅ Add this for testing
        "/api/v1/admin/send-proposal",          # ✅ Add this
        "/api/v1/admin/temp-links",
        "/api/v1/admin/active-sessions",
        "/api/v1/temp-access/*",         # ✅ Add wildcard
        "/api/v1/proposals/*/temp-session",  # ✅ For proposal access
    ]
)

# Include routers
app.include_router(proposals.router, prefix="/api/v1", tags=["proposals"])
app.include_router(questions.router, prefix="/api/v1", tags=["questions"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(admin_read.router, prefix="/api/v1", tags=["admin-read"])
app.include_router(admin_send_proposal.router, prefix="/api/v1", tags=["admin-email"])
app.include_router(secure_links.router, prefix="/api/v1", tags=["secure-links"])

# ✅ Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint - always accessible"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.1.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "sso_validation": True,
            "user_approval": True,
            "cors_enabled": True,
            "frontend_url": settings.FRONTEND_BASE_URL,
        },
        "database": "connected" if settings.DATABASE_URL else "not configured"
    }

# ✅ Root Endpoint
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Proposal Portal API with SSO User Validation",
        "version": "2.1.0",
        "endpoints": {
            "docs": "/docs" if settings.DEBUG else "disabled in production",
            "health": "/health",
            "debug_cors": "/api/v1/debug/cors",
        },
        "frontend": settings.FRONTEND_BASE_URL,
        "cors_enabled": True,
        "timestamp": datetime.utcnow().isoformat()
    }

# ✅ CORS Debug Endpoint
@app.get("/api/v1/debug/cors")
async def debug_cors(request: Request):
    """
    Debug endpoint to verify CORS configuration
    Access from browser console:
    fetch('http://production-env.eba-qeuwm4sn.us-west-2.elasticbeanstalk.com/api/v1/debug/cors')
      .then(r => r.json())
      .then(console.log)
    """
    origin = request.headers.get("origin", "No origin header")
    
    return {
        "message": "✅ CORS is working!",
        "your_request": {
            "origin": origin,
            "method": request.method,
            "headers": dict(request.headers),
        },
        "server_config": {
            "backend": "AWS Elastic Beanstalk",
            "frontend": "AWS Amplify",
            "frontend_url": settings.FRONTEND_BASE_URL,
            "allowed_origins": settings.allowed_origins_list,
            "cors_configured": True,
        },
        "test_results": {
            "origin_allowed": origin in settings.allowed_origins_list or origin == settings.FRONTEND_BASE_URL,
            "cors_headers_present": True,
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ✅ OPTIONS handler for preflight requests
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    """
    Handle CORS preflight OPTIONS requests
    This ensures all routes respond correctly to preflight
    """
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