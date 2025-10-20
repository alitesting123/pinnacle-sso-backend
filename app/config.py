# app/config.py
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    # Database - will be overridden by .env
    DATABASE_URL: str = "sqlite:///./proposal_portal.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "development-secret-change-in-production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # AWS Cognito
    AWS_REGION: str = "us-east-1"
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    COGNITO_CLIENT_SECRET: str = ""
    
    # ✅ UPDATED: Frontend URL
   # app/config.py
    FRONTEND_BASE_URL: str = "https://main.dnfe4l5bsjojn.amplifyapp.com"
    
    # ✅ UPDATED: CORS Origins
    ALLOWED_ORIGINS: str = "https://main.dnfe4l5bsjojn.amplifyapp.com,https://*.dnfe4l5bsjojn.amplifyapp.com,http://localhost:3000,http://localhost:8080,http://localhost:5173"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,production-env.eba-qeuwm4sn.us-west-2.elasticbeanstalk.com"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Parse comma-separated hosts into list"""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()

# Debug print to verify settings are loaded
if settings.DEBUG:
    db_url_masked = settings.DATABASE_URL[:30] + "..." if len(settings.DATABASE_URL) > 30 else settings.DATABASE_URL
    print(f"[Config] DATABASE_URL loaded: {db_url_masked}")
    print(f"[Config] Using database: {'PostgreSQL' if 'postgresql' in settings.DATABASE_URL else 'SQLite'}")
    print(f"[Config] FRONTEND_BASE_URL: {settings.FRONTEND_BASE_URL}")
    print(f"[Config] ALLOWED_ORIGINS: {len(settings.allowed_origins_list)} origins configured")