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
