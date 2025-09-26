# app/api/secure_links.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib
import logging
from app.database import get_db
from app.models.users import PreApprovedUser
from app.config import settings
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for active sessions (use Redis in production)
active_sessions = {}
temp_links = {}

# Mock customer-specific proposal data
CUSTOMER_PROPOSALS = {
    "admin@company.com": {
        "eventDetails": {
            "jobNumber": "306780",
            "clientName": "Internal Systems Upgrade",
            "venue": "Company Headquarters - Main Conference Room",
            "startDate": "2026-05-31",
            "endDate": "2026-06-03",
            "preparedBy": "Shahar Zlochover",
            "email": "shahar.zlochover@pinnaclelive.com",
            "status": "tentative",
            "version": "1.0",
            "lastModified": "2025-09-12T13:46:00Z"
        },
        "sections": [
            {
                "id": "audio",
                "title": "Audio Equipment",
                "isExpanded": True,
                "total": 18750,
                "items": [
                    {
                        "id": "audio-1",
                        "quantity": 18,
                        "description": "12\" Line Array Speaker",
                        "duration": "3 Days",
                        "price": 250,
                        "discount": 0,
                        "subtotal": 13500,
                        "category": "audio",
                        "notes": "3 stacks of 3 tops and one sub for front speakers"
                    }
                ]
            }
        ],
        "totalCost": 95000,
        "timeline": [
            {
                "id": "setup-day-1",
                "date": "2026-05-31",
                "startTime": "08:00",
                "endTime": "18:00",
                "title": "Load-in & Setup",
                "location": "Company Headquarters",
                "setup": ["Audio rigging", "Testing"],
                "equipment": ["Audio"],
                "cost": 12500
            }
        ]
    },
    "client@customer.com": {
        "eventDetails": {
            "jobNumber": "306781",
            "clientName": "Customer Corp Annual Meeting",
            "venue": "Grand Ballroom - Luxury Hotel",
            "startDate": "2026-06-01",
            "endDate": "2026-06-03",
            "preparedBy": "Shahar Zlochover",
            "email": "shahar.zlochover@pinnaclelive.com",
            "status": "confirmed",
            "version": "2.0",
            "lastModified": "2025-09-12T13:46:00Z"
        },
        "sections": [
            {
                "id": "audio",
                "title": "Premium Audio Equipment",
                "isExpanded": True,
                "total": 25000,
                "items": [
                    {
                        "id": "audio-1",
                        "quantity": 24,
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
        "totalCost": 120000,
        "timeline": [
            {
                "id": "setup-day-1",
                "date": "2026-06-01",
                "startTime": "08:00",
                "endTime": "18:00",
                "title": "Load-in & Setup",
                "location": "Grand Ballroom",
                "setup": ["Premium audio setup", "Executive testing"],
                "equipment": ["Premium Audio"],
                "cost": 25000
            }
        ]
    }
}

class GenerateTempLinkRequest(BaseModel):
    user_email: EmailStr
    proposal_id: str = "306780"
    session_duration_minutes: float = 0.5  # Changed to float

class TempLinkResponse(BaseModel):
    temp_url: str
    token: str
    expires_at: str
    session_duration_minutes: float  # Changed to float

class SessionInfo(BaseModel):
    session_id: str
    user_email: str
    user_name: str
    company: Optional[str]
    expires_at: str
    time_remaining_minutes: int

@router.post("/proposals/generate-temp-link", response_model=TempLinkResponse)
async def generate_temp_link(
    request_data: GenerateTempLinkRequest,
    db: Session = Depends(get_db)
):
    """Generate a temporary access link for pre-approved client"""
    
    # Validate client is pre-approved
    client = db.query(PreApprovedUser).filter(
        PreApprovedUser.email == request_data.user_email,
        PreApprovedUser.is_active == True
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client {request_data.user_email} not found in approved users"
        )
    
    # Generate secure token (long random string)
    timestamp = str(int(datetime.utcnow().timestamp()))
    random_part = secrets.token_urlsafe(32)
    client_hash = hashlib.sha256(request_data.user_email.encode()).hexdigest()[:8]
    
    # Create long token: timestamp_clienthash_randomstring
    token = f"{timestamp}_{client_hash}_{random_part}"
    
    expires_at = datetime.utcnow() + timedelta(minutes=request_data.session_duration_minutes)
    
    # Store temporary link data
    temp_links[token] = {
        "user_email": request_data.user_email,
        "user_name": client.full_name or request_data.user_email.split('@')[0],
        "company": client.company,
        "proposal_id": request_data.proposal_id,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "session_duration": request_data.session_duration_minutes,
        "is_active": True,
        "click_count": 0
    }
    
    # Generate the temporary URL with long token
    temp_url = f"{settings.FRONTEND_BASE_URL}/temp-access?t={token}"
    
    # Send email to client
    try:
        email_sent = await email_service.send_temp_access_email(
            recipient_email=request_data.user_email,
            client_name=client.full_name or request_data.user_email,
            temp_access_url=temp_url,
            proposal_id=request_data.proposal_id
        )
        
        if email_sent:
            logger.info(f"Email sent successfully to {request_data.user_email}")
        else:
            logger.warning(f"Failed to send email to {request_data.user_email}, but link was generated")
            
    except Exception as e:
        logger.error(f"Email service error: {str(e)}")
        # Continue even if email fails - admin can still copy the link
    
    return TempLinkResponse(
        temp_url=temp_url,
        token=token,
        expires_at=expires_at.isoformat(),
        session_duration_minutes=request_data.session_duration_minutes
    )

@router.get("/temp-access/{token}")
async def validate_temp_access(token: str, db: Session = Depends(get_db)):
    """Validate temporary access token and create session"""
    
    # Check if token exists
    link_data = temp_links.get(token)
    if not link_data:
        raise HTTPException(
            status_code=404,
            detail="Invalid or expired access link. Please request a new link."
        )
    
    # Check if link is still active
    if not link_data["is_active"]:
        raise HTTPException(
            status_code=410,
            detail="This access link has been used. Please request a new link."
        )
    
    # Validate client is still approved
    client = db.query(PreApprovedUser).filter(
        PreApprovedUser.email == link_data["user_email"],
        PreApprovedUser.is_active == True
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=403,
            detail="Client access has been revoked. Please contact support."
        )
    
    # Create session
    session_id = secrets.token_urlsafe(16)
    session_expires = datetime.utcnow() + timedelta(minutes=link_data["session_duration"])
    
    active_sessions[session_id] = {
        "user_email": link_data["user_email"],
        "user_name": client.full_name or link_data["user_name"],
        "company": client.company or link_data["company"],
        "proposal_id": link_data["proposal_id"],
        "created_at": datetime.utcnow(),
        "expires_at": session_expires,
        "temp_token": token,
        "is_active": True
    }
    
    # Update link usage
    link_data["click_count"] += 1
    link_data["last_used"] = datetime.utcnow()
    link_data["is_active"] = False  # One-time use link
    
    time_remaining = int((session_expires - datetime.utcnow()).total_seconds() / 60)
    
    return {
        "session_id": session_id,
        "user": {
            "email": client.email,
            "full_name": client.full_name,
            "company": client.company
        },
        "session_expires": session_expires.isoformat(),
        "time_remaining_minutes": max(0, time_remaining),
        "proposal_id": link_data["proposal_id"],
        "message": f"Welcome {client.full_name}! Your session is active for {link_data['session_duration']} minutes."
    }

@router.get("/proposals/{proposal_id}/temp-session")
async def get_proposal_with_session(proposal_id: str, session_id: str):
    """Get proposal data for active temporary session"""
    
    session = active_sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid session. Please use a new access link."
        )
    
    if not session["is_active"]:
        raise HTTPException(
            status_code=410,
            detail="Session has expired. Please request a new access link."
        )
    
    current_time = datetime.utcnow()
    if current_time > session["expires_at"]:
        session["is_active"] = False
        raise HTTPException(
            status_code=410,
            detail="Session has expired. Please request a new access link."
        )
    
    # Get customer-specific proposal
    proposal = get_customer_proposal_from_database(proposal_id, session["user_email"])
    
    # Update session last accessed
    session["last_accessed"] = current_time
    
    time_remaining = int((session["expires_at"] - current_time).total_seconds() / 60)
    
    return {
        **proposal,
        "session_info": {
            "user": {
                "email": session["user_email"],
                "full_name": session["user_name"],
                "company": session["company"]
            },
            "expires_at": session["expires_at"].isoformat(),
            "time_remaining_minutes": max(0, time_remaining)
        }
    }

def get_customer_proposal_from_database(proposal_id: str, customer_email: str) -> Dict[str, Any]:
    """Get customer-specific proposal data"""
    
    # Check if customer has a custom proposal
    if customer_email in CUSTOMER_PROPOSALS:
        proposal = CUSTOMER_PROPOSALS[customer_email].copy()
        
        # Customize proposal details for this specific customer
        proposal["eventDetails"]["jobNumber"] = proposal_id
        proposal["eventDetails"]["lastModified"] = datetime.utcnow().isoformat()
        
        return proposal
    
    # Return default proposal if no custom one exists
    from app.api.proposals import COMPLETE_MOCK_PROPOSAL
    
    default_proposal = COMPLETE_MOCK_PROPOSAL.copy()
    default_proposal["eventDetails"]["jobNumber"] = proposal_id
    default_proposal["eventDetails"]["clientName"] = f"Proposal for {customer_email}"
    default_proposal["eventDetails"]["lastModified"] = datetime.utcnow().isoformat()
    
    return default_proposal

@router.delete("/temp-sessions/{session_id}")
async def invalidate_temp_session(session_id: str):
    """Manually invalidate a temporary session"""
    if session_id in active_sessions:
        active_sessions[session_id]["is_active"] = False
        active_sessions[session_id]["invalidated_at"] = datetime.utcnow()
        return {"message": "Session invalidated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@router.get("/admin/temp-links")
async def list_temp_links():
    """List all temporary links (admin endpoint)"""
    
    links = []
    for token, data in temp_links.items():
        links.append({
            "token": token[:16] + "...",  # Partial token for security
            "user_email": data["user_email"],
            "user_name": data["user_name"],
            "company": data["company"],
            "proposal_id": data["proposal_id"],
            "created_at": data["created_at"].isoformat(),
            "expires_at": data["expires_at"].isoformat(),
            "click_count": data["click_count"],
            "is_active": data["is_active"],
            "last_used": data.get("last_used").isoformat() if data.get("last_used") else None
        })
    
    return {
        "temp_links": links,
        "total_count": len(links)
    }

@router.get("/admin/active-sessions")
async def list_active_sessions():
    """List all active sessions (admin endpoint)"""
    
    sessions = []
    current_time = datetime.utcnow()
    
    for session_id, data in active_sessions.items():
        if data["is_active"] and current_time <= data["expires_at"]:
            time_remaining = int((data["expires_at"] - current_time).total_seconds() / 60)
            sessions.append({
                "session_id": session_id[:8] + "...",
                "user_email": data["user_email"],
                "user_name": data["user_name"],
                "company": data["company"],
                "proposal_id": data["proposal_id"],
                "created_at": data["created_at"].isoformat(),
                "expires_at": data["expires_at"].isoformat(),
                "time_remaining_minutes": max(0, time_remaining),
                "last_accessed": data.get("last_accessed").isoformat() if data.get("last_accessed") else None
            })
    
    return {
        "active_sessions": sessions,
        "total_count": len(sessions)
    }

# Cleanup expired sessions (run periodically)
@router.post("/admin/cleanup-sessions")
async def cleanup_expired_sessions():
    """Clean up expired sessions and links"""
    
    current_time = datetime.utcnow()
    
    # Clean expired sessions
    expired_sessions = []
    for session_id, session_data in list(active_sessions.items()):
        if current_time > session_data["expires_at"]:
            expired_sessions.append(session_id)
            del active_sessions[session_id]
    
    # Clean old temp links (older than 24 hours)
    old_links = []
    cutoff_time = current_time - timedelta(hours=24)
    for token, link_data in list(temp_links.items()):
        if link_data["created_at"] < cutoff_time:
            old_links.append(token)
            del temp_links[token]
    
    return {
        "cleaned_sessions": len(expired_sessions),
        "cleaned_links": len(old_links),
        "message": "Cleanup completed successfully"
    }
@router.post("/temp-sessions/{session_id}/extend")
async def extend_temp_session(session_id: str):
    """Extend a temporary session by 10 minutes"""
    
    session = active_sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    if not session["is_active"]:
        raise HTTPException(
            status_code=410,
            detail="Session has expired and cannot be extended"
        )
    
    # Extend by 10 minutes
    new_expiry = datetime.utcnow() + timedelta(minutes=10)
    session["expires_at"] = new_expiry
    session["extended_at"] = datetime.utcnow()
    session["extension_count"] = session.get("extension_count", 0) + 1
    
    time_remaining = int((new_expiry - datetime.utcnow()).total_seconds() / 60)
    
    logger.info(f"Session {session_id} extended by 10 minutes. Total extensions: {session['extension_count']}")
    
    return {
        "message": "Session extended successfully",
        "new_expires_at": new_expiry.isoformat(),
        "time_remaining_minutes": time_remaining,
        "extended_by_minutes": 10,
        "extension_count": session["extension_count"]
    }