# app/api/admin_send_proposal.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.models.users import PreApprovedUser
from app.models.proposals import Proposal
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SendProposalRequest(BaseModel):
    client_email: EmailStr  # Can be any email - even ali2@gmail.com for testing
    proposal_id: str  # Job number like "302798"
    admin_email: EmailStr
    session_duration_minutes: float = 20

class SendProposalResponse(BaseModel):
    success: bool
    message: str
    temp_url: Optional[str] = None
    client_name: Optional[str] = None
    proposal_info: Optional[dict] = None

@router.post("/admin/send-proposal", response_model=SendProposalResponse)
async def send_proposal_to_client(
    request: SendProposalRequest,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Generate temp link and send proposal to ANY email
    Can send to client email OR test email like ali2@gmail.com
    """
    try:
        logger.info(f"=== SEND PROPOSAL REQUEST ===")
        logger.info(f"Proposal ID: {request.proposal_id}")
        logger.info(f"Recipient Email: {request.client_email}")
        logger.info(f"Admin: {request.admin_email}")
        
        # 1. Get the proposal from database by job_number
        proposal = db.query(Proposal).filter(
            Proposal.job_number == request.proposal_id
        ).first()
        
        if not proposal:
            raise HTTPException(
                status_code=404,
                detail=f"Proposal #{request.proposal_id} not found in database"
            )
        
        logger.info(f"Found proposal: {proposal.client_name}")
        
        # 2. Check if recipient exists in pre-approved users (optional - for production clients)
        client = db.query(PreApprovedUser).filter(
            PreApprovedUser.email == request.client_email,
            PreApprovedUser.is_active == True
        ).first()
        
        # Determine client name
        if client:
            client_name = client.full_name or request.client_email.split('@')[0]
            logger.info(f"Recipient is pre-approved client: {client_name}")
        else:
            # For testing emails like ali2@gmail.com - just use email name
            client_name = request.client_email.split('@')[0].title()
            logger.info(f"Recipient is TEST email: {client_name}")
        
        # 3. Generate temporary access link
        from app.api.secure_links import temp_links
        import secrets
        import hashlib
        from datetime import datetime, timedelta
        
        timestamp = str(int(datetime.utcnow().timestamp()))
        random_part = secrets.token_urlsafe(32)
        client_hash = hashlib.sha256(request.client_email.encode()).hexdigest()[:8]
        
        token = f"{timestamp}_{client_hash}_{random_part}"
        
        expires_at = datetime.utcnow() + timedelta(minutes=request.session_duration_minutes)
        
        # Store temporary link data
        temp_links[token] = {
            "user_email": request.client_email,
            "user_name": client_name,
            "company": client.company if client else "Test Company",
            "proposal_id": request.proposal_id,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "session_duration": request.session_duration_minutes,
            "is_active": True,
            "click_count": 0,
            "sent_by": request.admin_email
        }
        
        # 4. Generate the temporary URL
        from app.config import settings
        temp_url = f"{settings.FRONTEND_BASE_URL}/temp-access?t={token}"
        
        logger.info(f"Generated temp URL: {temp_url[:50]}...")
        
        # 5. Send email to recipient
        logger.info(f"Sending email to {request.client_email}...")
        
        email_sent = await email_service.send_temp_access_email(
            recipient_email=request.client_email,  # Goes to ANY email
            client_name=client_name,
            temp_access_url=temp_url,
            proposal_id=request.proposal_id
        )
        
        if not email_sent:
            logger.warning(f"Email sending failed for {request.client_email}, but link was created")
            return SendProposalResponse(
                success=True,
                message=f"Link generated but email failed. Please share manually: {temp_url}",
                temp_url=temp_url,
                client_name=client_name,
                proposal_info={
                    "job_number": proposal.job_number,
                    "client_name": proposal.client_name,
                    "venue": proposal.venue_name
                }
            )
        
        logger.info(f"✅ SUCCESS! Proposal {request.proposal_id} sent to {request.client_email}")
        
        return SendProposalResponse(
            success=True,
            message=f"✅ Proposal #{request.proposal_id} successfully sent to {request.client_email}",
            temp_url=temp_url,
            client_name=client_name,
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
        logger.error(f"Failed to send proposal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send proposal: {str(e)}"
        )


# Add this to app/main.py:
# from app.api import admin_send_proposal
# app.include_router(admin_send_proposal.router, prefix="/api/v1", tags=["admin"])