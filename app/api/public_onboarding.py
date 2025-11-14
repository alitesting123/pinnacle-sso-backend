# app/api/public_onboarding.py
"""Public API for client onboarding - requires API key authentication"""

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from app.database import get_db
from app.models.proposals import Proposal
from app.config import settings
from app.api.secure_access import create_temp_access_token
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class OnboardClientRequest(BaseModel):
    """Request to onboard a new client with a proposal"""
    # Client information
    client_name: str
    client_email: EmailStr
    client_company: Optional[str] = None
    client_contact: Optional[str] = None
    client_phone: Optional[str] = None

    # Event details
    venue_name: Optional[str] = None
    event_location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # Proposal metadata
    job_number: Optional[str] = None  # If not provided, auto-generate
    prepared_by: Optional[str] = None
    salesperson: Optional[str] = None
    salesperson_email: Optional[str] = None
    status: str = "draft"

    # Token settings
    access_duration_hours: int = 24

class OnboardClientResponse(BaseModel):
    """Response with proposal details and temporary access link"""
    success: bool
    message: str
    proposal: dict
    temp_access_url: str
    expires_at: str

# ============================================================================
# AUTHENTICATION
# ============================================================================

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Verify API key from header"""
    if x_api_key != settings.PUBLIC_API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    return x_api_key

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_job_number(db: Session) -> str:
    """Generate a unique job number"""
    # Get the highest existing job number
    latest_proposal = db.query(Proposal).order_by(Proposal.job_number.desc()).first()

    if latest_proposal and latest_proposal.job_number:
        try:
            # Try to increment if it's a number
            last_number = int(latest_proposal.job_number)
            return str(last_number + 1)
        except ValueError:
            pass

    # Default: Use timestamp-based job number
    return f"JOB{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@router.post("/public/onboard-client", response_model=OnboardClientResponse)
async def onboard_client(
    request: OnboardClientRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    🌍 PUBLIC ENDPOINT: Onboard a new client with proposal and temp access

    Authentication: Requires X-API-Key header

    Flow:
    1. Validate API key
    2. Create new proposal
    3. Generate JWT token for temp access
    4. Return proposal details and access link

    Example:
    ```bash
    curl -X POST https://api.example.com/api/v1/public/onboard-client \
      -H "X-API-Key: your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "client_name": "John Doe",
        "client_email": "john@example.com",
        "client_company": "Acme Corp",
        "venue_name": "Convention Center",
        "event_location": "New York, NY",
        "start_date": "2025-06-15"
      }'
    ```
    """

    logger.info(f"🆕 Onboarding new client: {request.client_name} ({request.client_email})")

    try:
        # 1. Generate job number if not provided
        job_number = request.job_number or generate_job_number(db)

        # Check if job number already exists
        existing = db.query(Proposal).filter(
            Proposal.job_number == job_number
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Proposal with job number {job_number} already exists"
            )

        # 2. Parse dates if provided
        start_date = None
        end_date = None

        if request.start_date:
            try:
                start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00')).date()
            except:
                # Try simple date format
                try:
                    start_date = datetime.strptime(request.start_date, '%Y-%m-%d').date()
                except:
                    logger.warning(f"Could not parse start_date: {request.start_date}")

        if request.end_date:
            try:
                end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00')).date()
            except:
                try:
                    end_date = datetime.strptime(request.end_date, '%Y-%m-%d').date()
                except:
                    logger.warning(f"Could not parse end_date: {request.end_date}")

        # If dates not provided, use a default future date
        if not start_date:
            start_date = datetime.utcnow().date()
        if not end_date:
            end_date = start_date

        # 3. Create new proposal
        new_proposal = Proposal(
            id=uuid.uuid4(),
            job_number=job_number,
            client_name=request.client_name,
            client_email=request.client_email,
            client_company=request.client_company,
            client_contact=request.client_contact,
            client_phone=request.client_phone,
            venue_name=request.venue_name,
            event_location=request.event_location,
            start_date=start_date,
            end_date=end_date,
            prepared_by=request.prepared_by or "System",
            salesperson=request.salesperson,
            salesperson_email=request.salesperson_email,
            status=request.status,
            version="1.0",
            product_subtotal=0,
            product_discount=0,
            product_total=0,
            labor_total=0,
            service_charge=0,
            tax_amount=0,
            total_cost=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_proposal)
        db.commit()
        db.refresh(new_proposal)

        logger.info(f"✅ Created proposal {new_proposal.job_number} (ID: {new_proposal.id})")

        # 4. Generate JWT token for temp access
        token, expires_at = create_temp_access_token(
            recipient_email=request.client_email,
            proposal_id=str(new_proposal.id),
            proposal_job_number=new_proposal.job_number,
            duration_hours=request.access_duration_hours
        )

        # 5. Build access URL
        frontend_url = settings.FRONTEND_BASE_URL
        temp_access_url = f"{frontend_url}/proposal?token={token}"

        logger.info(f"🔐 Generated temp access link (expires: {expires_at.isoformat()})")

        # 6. Return response
        return OnboardClientResponse(
            success=True,
            message=f"Client {request.client_name} onboarded successfully",
            proposal={
                "id": str(new_proposal.id),
                "job_number": new_proposal.job_number,
                "client_name": new_proposal.client_name,
                "client_email": new_proposal.client_email,
                "client_company": new_proposal.client_company,
                "venue_name": new_proposal.venue_name,
                "event_location": new_proposal.event_location,
                "start_date": new_proposal.start_date.isoformat() if new_proposal.start_date else None,
                "end_date": new_proposal.end_date.isoformat() if new_proposal.end_date else None,
                "status": new_proposal.status,
                "total_cost": float(new_proposal.total_cost),
                "created_at": new_proposal.created_at.isoformat()
            },
            temp_access_url=temp_access_url,
            expires_at=expires_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error onboarding client: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to onboard client: {str(e)}"
        )

@router.get("/public/health")
async def public_health_check():
    """Public health check endpoint (no auth required)"""
    return {
        "status": "healthy",
        "service": "public-onboarding-api",
        "timestamp": datetime.utcnow().isoformat()
    }
