# app/api/admin.py - COMPLETE FIXED FILE
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.proposals import Proposal
from app.services.email_service import email_service
from app.api.secure_links import temp_links
from app.config import settings
import secrets
import hashlib
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

class SendProposalRequest(BaseModel):
    client_email: EmailStr  # ANY email entered by admin
    proposal_id: str
    admin_email: EmailStr
    session_duration_minutes: int = 20

class SendProposalResponse(BaseModel):
    success: bool
    message: str
    temp_url: str
    proposal_info: dict

@router.get("/admin/health")
async def admin_health():
    """Admin health check"""
    return {
        "status": "admin endpoints working",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/admin/send-proposal", response_model=SendProposalResponse)
async def send_proposal_via_email(
    request: SendProposalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send proposal to ANY email address entered by admin
    
    CRITICAL: Use request.client_email ONLY - do NOT query database for email
    """
    
    try:
        # Use the ENTERED email directly - DO NOT query database
        recipient_email = request.client_email  # ✅ This is the entered email
        recipient_name = recipient_email.split('@')[0]  # Simple name from email
        
        logger.info("=" * 80)
        logger.info(f"🔍 DEBUG: REQUEST DATA FROM FRONTEND")
        logger.info(f"   client_email: {request.client_email}")
        logger.info(f"   proposal_id: {request.proposal_id}")
        logger.info(f"   admin_email: {request.admin_email}")
        logger.info("=" * 80)
        logger.info(f"📧 RECIPIENT EMAIL SET TO: {recipient_email}")
        logger.info(f"   Admin: {request.admin_email}")
        logger.info(f"   Proposal: {request.proposal_id}")
        logger.info("=" * 80)
        
        # Get proposal data (for content, not email address)
        proposal = None
        try:
            proposal_uuid = uuid.UUID(request.proposal_id)
            proposal = db.query(Proposal).filter(Proposal.id == proposal_uuid).first()
        except ValueError:
            proposal = db.query(Proposal).filter(
                Proposal.job_number == request.proposal_id
            ).first()
        
        if not proposal:
            raise HTTPException(
                status_code=404,
                detail=f"Proposal {request.proposal_id} not found"
            )
        
        logger.info(f"✅ Found proposal: {proposal.client_name}")
        
        # Generate secure token using ENTERED email
        timestamp = str(int(datetime.utcnow().timestamp()))
        random_part = secrets.token_urlsafe(32)
        email_hash = hashlib.sha256(recipient_email.encode()).hexdigest()[:8]
        token = f"{timestamp}_{email_hash}_{random_part}"
        
        expires_at = datetime.utcnow() + timedelta(minutes=request.session_duration_minutes)
        
        # Store temp link with ENTERED email
        temp_links[token] = {
            "user_email": recipient_email,  # ✅ ENTERED EMAIL
            "user_name": recipient_name,
            "company": None,
            "proposal_id": str(proposal.id),
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "session_duration": request.session_duration_minutes,
            "is_active": True,
            "click_count": 0,
            "sent_by_admin": request.admin_email
        }
        
        logger.info(f"✅ Token generated for: {recipient_email}")
        
        # Generate URL
        temp_url = f"{settings.FRONTEND_BASE_URL}/temp-access?t={token}"
        
        # Send email to ENTERED email address
        logger.info(f"✅ Queueing email to: {recipient_email}")
        
        background_tasks.add_task(
            email_service.send_temp_access_email,
            recipient_email=recipient_email,  # ✅ SEND TO ENTERED EMAIL
            recipient_name=recipient_name,
            temp_access_url=temp_url,
            proposal_id=proposal.job_number,
            proposal_client_name=proposal.client_name,
            proposal_venue=proposal.venue_name,
            proposal_total_cost=float(proposal.total_cost) if proposal.total_cost else 0
        )
        
        logger.info(f"✅ Email queued to: {recipient_email}")
        logger.info("=" * 80)
        
        return SendProposalResponse(
            success=True,
            message=f"✅ Proposal #{proposal.job_number} successfully sent to {recipient_email}",
            temp_url=temp_url,
            proposal_info={
                "job_number": proposal.job_number,
                "client_name": proposal.client_name,
                "venue": proposal.venue_name,
                "total_cost": float(proposal.total_cost) if proposal.total_cost else 0
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to send proposal: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send proposal: {str(e)}"
        )