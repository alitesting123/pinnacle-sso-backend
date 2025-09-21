# app/api/secure_links.py
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import json
from app.database import get_db
from app.models.users import PreApprovedUser
from app.api.proposals import COMPLETE_MOCK_PROPOSAL

router = APIRouter()

# In-memory storage for demo (replace with database in production)
secure_links_storage = {}

# Mock customer-specific proposal data
CUSTOMER_PROPOSALS = {
    "admin@company.com": {
        **COMPLETE_MOCK_PROPOSAL,
        "eventDetails": {
            **COMPLETE_MOCK_PROPOSAL["eventDetails"],
            "clientName": "Internal Systems Upgrade",
            "venue": "Company Headquarters - Main Conference Room",
            "preparedBy": "Shahar Zlochover",
            "email": "shahar.zlochover@pinnaclelive.com"
        },
        "totalCost": 95000  # Different pricing for internal client
    },
    "client@customer.com": {
        **COMPLETE_MOCK_PROPOSAL,
        "eventDetails": {
            **COMPLETE_MOCK_PROPOSAL["eventDetails"],
            "clientName": "Customer Corp Annual Meeting",
            "venue": "Grand Ballroom - Luxury Hotel",
            "preparedBy": "Shahar Zlochover",
            "email": "shahar.zlochover@pinnaclelive.com"
        },
        "sections": [
            # Enhanced proposal for external client
            {
                "id": "audio",
                "title": "Premium Audio Equipment",
                "isExpanded": True,
                "total": 25000,  # Upgraded pricing
                "items": [
                    {
                        "id": "audio-1",
                        "quantity": 24,  # More equipment
                        "description": "Premium Line Array Speaker System",
                        "duration": "3 Days",
                        "price": 350,
                        "discount": 0,
                        "subtotal": 25200,
                        "category": "audio",
                        "notes": "Top-tier audio setup for executive presentation"
                    }
                ]
            }
        ],
        "totalCost": 120000  # Premium pricing for external client
    }
}

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
    customer_email: str
    proposal_id: str

@router.post("/proposals/{proposal_id}/generate-link", response_model=GenerateLinkResponse)
async def generate_secure_link(
    proposal_id: str,
    request_data: GenerateLinkRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Generate a secure link for proposal access"""
    
    # Validate that the user is pre-approved
    pre_approved = db.query(PreApprovedUser).filter(
        PreApprovedUser.email == request_data.user_email,
        PreApprovedUser.is_active == True
    ).first()
    
    if not pre_approved:
        raise HTTPException(
            status_code=403, 
            detail=f"User {request_data.user_email} is not authorized to access proposals"
        )
    
    # Check if customer has a specific proposal
    if request_data.user_email not in CUSTOMER_PROPOSALS:
        raise HTTPException(
            status_code=404,
            detail=f"No proposal found for customer {request_data.user_email}"
        )
    
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(hours=request_data.expires_in_hours)
    
    link_data = {
        "token": token,
        "proposal_id": proposal_id,
        "user_email": request_data.user_email,
        "user_name": request_data.user_name or pre_approved.full_name,
        "company": request_data.company or pre_approved.company,
        "permissions": request_data.permissions,
        "expires_at": expires_at,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "pre_approved_user_id": pre_approved.id
    }
    
    secure_links_storage[token] = link_data
    
    # Generate frontend URL
    frontend_url = f"http://localhost:3000/secure/{token}"
    
    return GenerateLinkResponse(
        url=frontend_url,
        token=token,
        expires_at=expires_at.isoformat(),
        customer_email=request_data.user_email,
        proposal_id=proposal_id
    )

def get_customer_proposal_from_database(proposal_id: str, customer_email: str, db: Session) -> Dict[str, Any]:
    """Get customer-specific proposal data from database"""
    
    proposal = db.query(CustomerProposal).filter(
        CustomerProposal.customer_email == customer_email,
        CustomerProposal.status == "active"
    ).first()
    
    if proposal:
        return proposal.proposal_data
    
    # Return default if no custom proposal exists
    return COMPLETE_MOCK_PROPOSAL

@router.get("/secure-proposals/{token}")
async def access_secure_proposal(token: str, request: Request, db: Session = Depends(get_db)):
    """Access proposal via secure token with database validation"""
    
    link_data = secure_links_storage.get(token)
    
    if not link_data:
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    
    if not link_data["is_active"]:
        raise HTTPException(status_code=410, detail="Link has been revoked")
    
    if datetime.utcnow() > link_data["expires_at"]:
        raise HTTPException(status_code=410, detail="Link has expired")
    
    # Validate user is still pre-approved in database
    pre_approved = db.query(PreApprovedUser).filter(
        PreApprovedUser.email == link_data["user_email"],
        PreApprovedUser.is_active == True
    ).first()
    
    if not pre_approved:
        raise HTTPException(
            status_code=403, 
            detail="User access has been revoked. Please contact administrator."
        )
    
    # Get customer-specific proposal data
    try:
        proposal = get_customer_proposal_from_database(
            proposal_id=link_data["proposal_id"],
            customer_email=link_data["user_email"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load proposal data: {str(e)}"
        )
    
    # Create user context from database and link data
    temp_user = {
        "user_id": f"secure-{token[:8]}",
        "email": link_data["user_email"],
        "full_name": pre_approved.full_name or link_data.get("user_name", "Guest User"),
        "company": pre_approved.company or link_data.get("company"),
        "department": pre_approved.department,
        "roles": ["guest"],
        "permissions": link_data["permissions"],
        "access_method": "secure_link"
    }
    
    # Update access tracking
    link_data["last_accessed"] = datetime.utcnow()
    link_data["access_count"] = link_data.get("access_count", 0) + 1
    
    # Optional: Update database tracking
    if not pre_approved.last_login:
        pre_approved.last_login = datetime.utcnow()
        db.commit()
    
    return {
        **proposal,
        "user": temp_user,
        "access_type": "secure_link",
        "link_expires": link_data["expires_at"].isoformat(),
        "access_count": link_data["access_count"],
        "message": f"Welcome {temp_user['full_name']}! Secure proposal access granted."
    }

@router.delete("/secure-links/{token}")
async def revoke_secure_link(token: str, request: Request):
    """Revoke a secure link"""
    
    if token in secure_links_storage:
        secure_links_storage[token]["is_active"] = False
        secure_links_storage[token]["revoked_at"] = datetime.utcnow()
        return {"message": "Link revoked successfully"}
    else:
        raise HTTPException(status_code=404, detail="Link not found")

@router.get("/admin/secure-links")
async def list_active_links(db: Session = Depends(get_db)):
    """List all active secure links (admin endpoint)"""
    
    active_links = [
        {
            "token": token[:16] + "...",  # Partial token for security
            "user_email": data["user_email"],
            "proposal_id": data["proposal_id"],
            "created_at": data["created_at"].isoformat(),
            "expires_at": data["expires_at"].isoformat(),
            "access_count": data.get("access_count", 0),
            "is_active": data["is_active"]
        }
        for token, data in secure_links_storage.items()
        if data["is_active"]
    ]
    
    return {
        "active_links": active_links,
        "total_count": len(active_links)
    }