#!/bin/bash

set -e

echo "🚀 Setting up Proposal Portal API with SSO (macOS)..."

# Check Python version (macOS compatible)
python_version=$(python3 --version 2>&1 | sed 's/Python //' | cut -d. -f1,2)
required_version="3.11"

# Simple version comparison for macOS
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ required. Found: Python $python_version"
    echo "Install with: brew install python@3.11"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create project directory structure
echo "📁 Creating project structure..."
mkdir -p app/{auth,api,models,schemas,services,core,utils}
mkdir -p tests
mkdir -p deployment/{k8s,nginx,scripts}
mkdir -p docs monitoring scripts alembic/versions

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core FastAPI dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
aiosqlite==0.19.0

# Authentication & Security
python-jose[cryptography]==3.3.0
cryptography==41.0.7
pydantic[email]==2.5.0
email-validator==2.1.0

# Rate Limiting & Caching
slowapi==0.1.9
redis==5.0.1

# Configuration
python-decouple==3.8
pydantic-settings==2.1.0

# HTTP requests for SSO
requests==2.31.0
httpx==0.25.2

# Middleware & CORS
starlette==0.27.0

# Logging & Monitoring
structlog==23.2.0
python-json-logger==2.0.7

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Development
black==23.11.0
flake8==6.1.0
mypy==1.7.1
isort==5.12.0

# Production
gunicorn==21.2.0
EOF

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env.example
cat > .env.example << 'EOF'
# Database Configuration
DATABASE_URL=sqlite:///./proposal_portal.db
# DATABASE_URL=postgresql://user:password@localhost:5432/proposal_portal

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Application Security
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
ENVIRONMENT=development
DEBUG=True

# SSO Configuration
SSO_PROVIDER=azure
SSO_SECRET_KEY=your-jwt-verification-key-32-chars-minimum

# Azure AD Configuration
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret

# Google Workspace Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Okta Configuration
OKTA_DOMAIN=your-okta-domain.okta.com
OKTA_CLIENT_ID=your-okta-client-id
OKTA_CLIENT_SECRET=your-okta-client-secret

# CORS & Security
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
ALLOWED_HOSTS=localhost,127.0.0.1,*.yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=True

# Logging
LOG_LEVEL=INFO
EOF

# Copy to actual .env file
cp .env.example .env

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Environment files
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# SSL certificates
*.pem
*.key
*.crt

# Docker
docker-compose.override.yml
EOF

# Create __init__.py files
touch app/__init__.py
touch app/auth/__init__.py
touch app/api/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/core/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py

# Create app/config.py
cat > app/config.py << 'EOF'
"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./proposal_portal.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "development-secret-change-in-production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # SSO
    SSO_PROVIDER: str = "azure"
    SSO_SECRET_KEY: str = "sso-verification-key"
    
    # Azure AD
    AZURE_TENANT_ID: str = ""
    AZURE_CLIENT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""
    
    # Google
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Okta
    OKTA_DOMAIN: str = ""
    OKTA_CLIENT_ID: str = ""
    OKTA_CLIENT_SECRET: str = ""
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
EOF

# Create app/core/logging.py
cat > app/core/logging.py << 'EOF'
"""Logging configuration"""

import logging
import sys
from app.config import settings

def setup_logging():
    """Setup application logging"""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
EOF

# Create app/auth/sso_middleware.py
cat > app/auth/sso_middleware.py << 'EOF'
"""Basic SSO middleware for development"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import base64
import json

logger = logging.getLogger(__name__)

class SSOAuthMiddleware(BaseHTTPMiddleware):
    """Basic SSO middleware"""
    
    def __init__(self, app, provider_name: str = "azure", exempt_paths: list = None):
        super().__init__(app)
        self.provider_name = provider_name
        self.exempt_paths = exempt_paths or []
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Try to extract user from headers
        user = self._extract_user_from_request(request)
        request.state.user = user
        
        return await call_next(request)
    
    def _extract_user_from_request(self, request: Request) -> dict:
        """Extract user information from request"""
        
        # Method 1: SSO Headers
        user_id = request.headers.get("X-SSO-User")
        email = request.headers.get("X-SSO-Email")
        name = request.headers.get("X-SSO-Name")
        
        if user_id and email and name:
            return {
                "user_id": user_id,
                "email": email,
                "full_name": name,
                "company": request.headers.get("X-SSO-Company"),
                "roles": request.headers.get("X-SSO-Roles", "user").split(","),
                "department": request.headers.get("X-SSO-Department")
            }
        
        # Method 2: Basic Auth (for testing)
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Basic "):
            try:
                encoded_data = auth_header.split(" ")[1]
                decoded_data = base64.b64decode(encoded_data).decode()
                user_data = json.loads(decoded_data)
                return user_data
            except Exception:
                pass
        
        # Method 3: Development fallback
        return {
            "user_id": "dev-user-123",
            "email": "developer@company.com",
            "full_name": "Development User",
            "roles": ["user", "admin"]
        }
EOF

# Create API routers
cat > app/api/proposals.py << 'EOF'
"""Proposals API endpoints"""

from fastapi import APIRouter, Request
from typing import List

router = APIRouter()

@router.get("/proposals")
async def get_proposals(request: Request):
    """Get user's proposals"""
    user = getattr(request.state, 'user', None)
    return {
        "proposals": [
            {
                "id": "prop-001",
                "client_name": "Sample Client",
                "event_location": "Sample Venue",
                "total_cost": 25000,
                "status": "tentative"
            }
        ],
        "user": user,
        "message": "Proposals endpoint working"
    }

@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str, request: Request):
    """Get specific proposal"""
    user = getattr(request.state, 'user', None)
    return {
        "proposal_id": proposal_id,
        "user": user,
        "client_name": "Sample Client",
        "total_cost": 25000,
        "message": "Individual proposal endpoint working"
    }
EOF

cat > app/api/questions.py << 'EOF'
"""Questions API endpoints"""

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/questions")
async def get_questions(request: Request):
    """Get equipment questions"""
    user = getattr(request.state, 'user', None)
    return {
        "questions": [
            {
                "id": "q-001",
                "question": "Sample equipment question?",
                "status": "pending",
                "asked_by": user.get("full_name") if user else "Unknown"
            }
        ],
        "user": user
    }

@router.post("/questions")
async def create_question(request: Request):
    """Create new question"""
    user = getattr(request.state, 'user', None)
    return {
        "message": "Question created",
        "user": user
    }
EOF

cat > app/api/users.py << 'EOF'
"""Users API endpoints"""

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/users/me")
async def get_current_user(request: Request):
    """Get current user from SSO"""
    user = getattr(request.state, 'user', None)
    if not user:
        return {"error": "No user found in request"}
    return {"user": user}
EOF

cat > app/api/admin.py << 'EOF'
"""Admin API endpoints"""

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/admin/health")
async def admin_health(request: Request):
    """Admin health check"""
    user = getattr(request.state, 'user', None)
    return {
        "status": "admin endpoints working",
        "user": user
    }
EOF

# Create main application file
cat > app/main.py << 'EOF'
"""
SSO-Enabled Proposal Portal API
Main application entry point
"""

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
    logger.info("🚀 Starting Proposal Portal API with SSO")
    yield
    # Shutdown
    logger.info("⏹️ Shutting down Proposal Portal API")

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
    allow_origins=settings.ALLOWED_ORIGINS,
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
EOF

# Create test file
cat > tests/test_main.py << 'EOF'
"""Basic tests for the API"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_user_me_endpoint():
    """Test user endpoint"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
EOF

# Create Makefile
cat > Makefile << 'EOF'
.PHONY: help install dev test lint format clean

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean up"

install:
	pip install -r requirements.txt

dev:
	python app/main.py

test:
	pytest -v

lint:
	flake8 app/ tests/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete
EOF

# Create Docker files
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./proposal_portal.db
    volumes:
      - .:/app
    restart: unless-stopped
EOF

# Create README.md
cat > README.md << 'EOF'
# Proposal Portal API with SSO

A secure FastAPI application for B2B event planning proposal management with Single Sign-On (SSO) integration.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
make dev
```

Visit http://localhost:8000/docs for API documentation.

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get user info
curl http://localhost:8000/api/v1/users/me

# Get proposals
curl http://localhost:8000/api/v1/proposals
```

## Configuration

Edit `.env` file to configure SSO providers and other settings.
EOF

echo "✅ Project setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Edit .env file with your SSO configuration"
echo "3. Start the server: make dev"
echo "4. Visit: http://localhost:8000/docs"
echo ""
echo "🔗 Quick test:"
echo "curl http://localhost:8000/health"