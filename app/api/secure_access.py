# app/api/secure_access.py - COMPLETE IMPLEMENTATION
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.database import get_db
from app.models.proposals import Proposal
from app.services.email_service import email_service
from app.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# JWT Configuration
JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SendProposalRequest(BaseModel):
    recipient_email: EmailStr
    proposal_id: str  # Can be UUID or job_number
    duration_hours: int = 24

class SendProposalResponse(BaseModel):
    message: str
    temp_url: str
    expires_at: str
    proposal_info: dict

# ============================================================================
# JWT TOKEN FUNCTIONS
# ============================================================================

def create_temp_access_token(
    recipient_email: str,
    proposal_id: str,
    proposal_job_number: str,
    duration_hours: int = 24
) -> tuple[str, datetime]:
    """
    Create JWT token for temporary proposal access
    
    Returns: (token, expiration_datetime)
    """
    expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
    
    payload = {
        "sub": recipient_email,        # Subject (who this is for)
        "proposal_id": proposal_id,    # UUID
        "job_number": proposal_job_number,
        "exp": expires_at,             # Expiration
        "iat": datetime.utcnow(),      # Issued at
        "jti": str(uuid.uuid4()),      # Unique token ID
        "type": "temp_access"          # Token type
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires_at

def validate_temp_access_token(token: str) -> dict:
    """
    Validate JWT token and return payload
    
    Raises HTTPException if invalid/expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "temp_access":
            raise HTTPException(status_code=403, detail="Invalid token type")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=410, detail="Access link has expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_proposal_by_id_or_job_number(db: Session, identifier: str):
    """Get proposal by UUID or job_number"""
    try:
        # Try UUID first
        proposal_uuid = uuid.UUID(identifier)
        proposal = db.query(Proposal).filter(Proposal.id == proposal_uuid).first()
        if proposal:
            return proposal
    except ValueError:
        pass
    
    # Try job_number
    return db.query(Proposal).filter(Proposal.job_number == identifier).first()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/admin/send-proposal", response_model=SendProposalResponse)
async def send_proposal_link(
    request: SendProposalRequest,
    db: Session = Depends(get_db)
):
    """
    🎯 MAIN ENDPOINT: Admin sends proposal link to client
    
    Flow:
    1. Validate proposal exists
    2. Generate JWT token (NO DB WRITE)
    3. Send email with token link
    4. Return success
    """
    
    logger.info(f"📧 Sending proposal {request.proposal_id} to {request.recipient_email}")
    
    # 1. Get proposal
    proposal = get_proposal_by_id_or_job_number(db, request.proposal_id)
    
    if not proposal:
        raise HTTPException(
            status_code=404, 
            detail=f"Proposal {request.proposal_id} not found"
        )
    
    # 2. Generate JWT token
    token, expires_at = create_temp_access_token(
        recipient_email=request.recipient_email,
        proposal_id=str(proposal.id),
        proposal_job_number=proposal.job_number,
        duration_hours=request.duration_hours
    )
    
    # 3. Build access URL
    frontend_url = settings.FRONTEND_BASE_URL
    temp_access_url = f"{frontend_url}/proposal?token={token}"
    
    logger.info(f"🔐 Generated JWT token (expires: {expires_at.isoformat()})")
    
    # 4. Send email
    email_sent = await email_service.send_temp_access_email(
        recipient_email=request.recipient_email,
        recipient_name=request.recipient_email.split('@')[0].title(),
        temp_access_url=temp_access_url,
        proposal_id=proposal.job_number,
        proposal_client_name=proposal.client_name,
        proposal_venue=proposal.venue_name or proposal.event_location,
        proposal_total_cost=float(proposal.total_cost)
    )
    
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    logger.info(f"✅ Email sent successfully to {request.recipient_email}")
    
    # 5. Return success
    return SendProposalResponse(
        message=f"Proposal link sent to {request.recipient_email}",
        temp_url=temp_access_url,
        expires_at=expires_at.isoformat(),
        proposal_info={
            "job_number": proposal.job_number,
            "client_name": proposal.client_name,
            "total_cost": float(proposal.total_cost),
            "venue": proposal.venue_name or proposal.event_location
        }
    )

@router.get("/proposal/access/{token}")
async def access_proposal_with_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    🔓 CLIENT ENDPOINT: Validate JWT and return proposal data
    
    Flow:
    1. Validate JWT token (checks signature + expiration)
    2. Get proposal from database
    3. Return full proposal data
    """
    
    logger.info(f"🔍 Validating access token...")
    
    # 1. Validate JWT (raises HTTPException if invalid)
    payload = validate_temp_access_token(token)
    
    recipient_email = payload.get("sub")
    proposal_id = payload.get("proposal_id")
    
    logger.info(f"✅ Token valid for {recipient_email} → Proposal {proposal_id}")
    
    # 2. Get proposal
    try:
        proposal_uuid = uuid.UUID(proposal_id)
        proposal = db.query(Proposal).filter(Proposal.id == proposal_uuid).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proposal ID in token")
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # 3. Build response (same format as /proposals/{id} endpoint)
    from app.api.proposals import get_proposal
    
    # Create a mock request with user info from token
    class MockRequest:
        class State:
            user = {
                "email": recipient_email,
                "full_name": recipient_email.split('@')[0].title(),
                "roles": ["guest"]
            }
        state = State()
    
    mock_request = MockRequest()
    
    # Reuse existing proposal detail endpoint logic
    return await get_proposal(str(proposal.id), mock_request, db)

# ============================================================================
# OPTIONAL: Token Info Endpoint (for debugging)
# ============================================================================

@router.get("/proposal/token-info/{token}")
async def get_token_info(token: str):
    """
    🔍 DEBUG ENDPOINT: Decode token without validation
    (Remove in production or add admin auth)
    """
    try:
        # Decode WITHOUT verification (for debugging only)
        payload = jwt.decode(token, options={"verify_signature": False})
        return {
            "valid": "unknown",
            "payload": payload,
            "expires_at": datetime.fromtimestamp(payload['exp']).isoformat(),
            "issued_at": datetime.fromtimestamp(payload['iat']).isoformat(),
            "recipient": payload.get('sub'),
            "proposal_id": payload.get('proposal_id')
        }
    except Exception as e:
        return {"error": str(e)}