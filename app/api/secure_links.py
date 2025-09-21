# app/api/secure_links.py (create this new file)
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
from app.database import get_db
from app.api.proposals import COMPLETE_MOCK_PROPOSAL

router = APIRouter()

# In-memory storage for demo (replace with database in production)
secure_links_storage = {}

class GenerateLinkRequest(BaseModel):
    user_email: EmailStr
    user_name: Optional[str] = None
    company: Optional[str] = None
    expires_in_hours: int = 24
    permissions: List[str] = ["view", "comment"]

class GenerateLinkResponse(BaseModel):
    url: str
    token: str
    expires_at: str

@router.post("/proposals/{proposal_id}/generate-link", response_model=GenerateLinkResponse)
async def generate_secure_link(
    proposal_id: str,
    request_data: GenerateLinkRequest,
    request: Request
):
    """Generate a secure link for proposal access"""
    
    # For demo purposes, we'll create the link without authentication
    # In production, you'd check if current user has permission
    
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(hours=request_data.expires_in_hours)
    
    link_data = {
        "token": token,
        "proposal_id": proposal_id,
        "user_email": request_data.user_email,
        "user_name": request_data.user_name,
        "company": request_data.company,
        "permissions": request_data.permissions,
        "expires_at": expires_at,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    secure_links_storage[token] = link_data
    
    # Generate frontend URL
    frontend_url = f"http://localhost:3000/secure/{token}"
    
    return GenerateLinkResponse(
        url=frontend_url,
        token=token,
        expires_at=expires_at.isoformat()
    )

@router.get("/secure-proposals/{token}")
async def access_secure_proposal(token: str, request: Request):
    """Access proposal via secure token"""
    
    link_data = secure_links_storage.get(token)
    
    if not link_data:
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    
    if not link_data["is_active"]:
        raise HTTPException(status_code=410, detail="Link has been revoked")
    
    if datetime.utcnow() > link_data["expires_at"]:
        raise HTTPException(status_code=410, detail="Link has expired")
    
    # Create temporary user context
    temp_user = {
        "user_id": f"secure-{token[:8]}",
        "email": link_data["user_email"],
        "full_name": link_data.get("user_name", "Guest User"),
        "company": link_data.get("company"),
        "roles": ["guest"],
        "permissions": link_data["permissions"]
    }
    
    # Return proposal data with user context
    return {
        **COMPLETE_MOCK_PROPOSAL,
        "user": temp_user,
        "access_type": "secure_link",
        "link_expires": link_data["expires_at"].isoformat(),
        "message": "Secure proposal access granted"
    }