# app/auth/sso_middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth.cognito_provider import CognitoProvider
from app.services.user_service import UserService, UserValidationError
from app.database import get_db
import logging

logger = logging.getLogger(__name__)

class ApprovedUserMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        self.cognito = CognitoProvider()
        self.exempt_paths = exempt_paths or [
            "/health", "/docs", "/redoc", "/openapi.json", "/", 
            "/admin/approved-users"  # Read-only endpoint
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401, 
                detail="Authorization header required"
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Validate with Cognito
            cognito_data = await self.cognito.validate_token(token)
            
            # Check against pre-approved users table
            db = next(get_db())
            user_service = UserService(db)
            user = user_service.validate_and_get_user(cognito_data)
            
            # Add user to request state
            request.state.user = {
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "roles": user.roles,
                "company": user.company,
                "department": user.department,
                "is_active": user.is_active
            }
            
            logger.debug(f"Authenticated user: {user.email}")
            
        except UserValidationError as e:
            logger.warning(f"User validation failed: {str(e)}")
            raise HTTPException(
                status_code=403, 
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise HTTPException(
                status_code=401, 
                detail="Authentication failed"
            )
        
        return await call_next(request)