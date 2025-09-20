
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import our modules
from app.config import settings
from app.auth.sso_middleware import SSOAuthMiddleware
from app.api import proposals, questions, users, admin
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Proposal Portal API with SSO")
    yield
    # Shutdown
    logger.info("Shutting down Proposal Portal API")

# Create FastAPI app
app = FastAPI(
    title="Proposal Portal API",
    description="SSO-enabled API for B2B event planning proposal management",
    version="2.0.0",
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

# Add SSO middleware
app.add_middleware(
    SSOAuthMiddleware,
    provider_name=settings.SSO_PROVIDER,
    exempt_paths=["/health", "/docs", "/redoc", "/openapi.json", "/"]
)

# Include routers
app.include_router(proposals.router, prefix="/api/v1", tags=["proposals"])
app.include_router(questions.router, prefix="/api/v1", tags=["questions"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Proposal Portal API with SSO",
        "docs": "/docs",
        "health": "/health"
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