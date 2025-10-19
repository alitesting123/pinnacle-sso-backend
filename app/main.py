# app/main.py (update existing file)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import our modules
from app.config import settings
from app.auth.sso_middleware import ApprovedUserMiddleware
from app.api import proposals, questions, users, admin, admin_read
from app.core.logging import setup_logging
from app.database import init_database
from app.api import proposals, questions, users, admin, admin_read, secure_links, admin_send_proposal

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Proposal Portal API with SSO User Validation")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Proposal Portal API")

# Create FastAPI app
app = FastAPI(
    title="Proposal Portal API",
    description="SSO-enabled API with pre-approved user validation",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add SSO middleware with user validation
app.add_middleware(
    ApprovedUserMiddleware,
    exempt_paths=["/health", "/docs", "/redoc", "/openapi.json", "/", "/admin/approved-users", "/admin/user-stats"]
)

# Include routers
app.include_router(questions.router, prefix="/api/v1", tags=["questions"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(admin_read.router, prefix="/api/v1", tags=["admin-read"])
app.include_router(admin_send_proposal.router, prefix="/api/v1", tags=["admin-email"])
# Include the new router

app.include_router(secure_links.router, prefix="/api/v1", tags=["secure-links"])
app.include_router(proposals.router, prefix="/api/v1", tags=["proposals"])
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.1.0",
        "environment": settings.ENVIRONMENT,
        "features": ["sso_validation", "user_approval"]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Proposal Portal API with SSO User Validation",
        "docs": "/docs",
        "health": "/health",
        "version": "2.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )