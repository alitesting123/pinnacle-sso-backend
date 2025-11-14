# app/api/public_onboarding.py
"""Public API for client onboarding - requires API key authentication"""

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from app.database import get_db
from app.models.proposals import (
    Proposal,
    ProposalSection,
    ProposalLineItem,
    ProposalLabor,
    ProposalTimeline
)
from app.config import settings
from app.api.secure_access import create_temp_access_token
from typing import Optional, List
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LineItemRequest(BaseModel):
    """Line item details"""
    description: str
    quantity: int = 1
    duration: Optional[str] = None
    unit_price: float
    discount: float = 0
    category: Optional[str] = None
    notes: Optional[str] = None

class SectionRequest(BaseModel):
    """Section with line items"""
    section_name: str
    section_type: Optional[str] = None
    items: List[LineItemRequest]

class LaborRequest(BaseModel):
    """Labor schedule item"""
    task_name: str
    quantity: int = 1
    labor_date: Optional[str] = None
    start_time: Optional[str] = None  # HH:MM format
    end_time: Optional[str] = None    # HH:MM format
    regular_hours: float = 0
    overtime_hours: float = 0
    double_time_hours: float = 0
    hourly_rate: float
    notes: Optional[str] = None

class TimelineRequest(BaseModel):
    """Timeline event"""
    event_date: Optional[str] = None
    start_time: Optional[str] = None  # HH:MM format
    end_time: Optional[str] = None    # HH:MM format
    title: str
    location: Optional[str] = None
    setup_tasks: Optional[List[str]] = None
    equipment_needed: Optional[List[str]] = None
    cost: float = 0
    notes: Optional[str] = None

class OnboardClientRequest(BaseModel):
    """Request to onboard a new client with complete proposal"""
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
    version: str = "1.0"
    notes: Optional[str] = None
    internal_notes: Optional[str] = None

    # Proposal content
    sections: Optional[List[SectionRequest]] = []
    labor: Optional[List[LaborRequest]] = []
    timeline: Optional[List[TimelineRequest]] = []

    # Pricing (optional - will be calculated from line items if not provided)
    service_charge: float = 0
    tax_amount: float = 0

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
    🌍 PUBLIC ENDPOINT: Onboard a new client with complete proposal and temp access

    Authentication: Requires X-API-Key header

    Creates a full proposal with sections, line items, labor, timeline, and generates
    a temporary JWT access link for the client to view the proposal.
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

        # 3. Calculate pricing from line items and labor
        product_subtotal = 0
        product_discount = 0
        labor_total = 0

        # Calculate product pricing from sections/items
        for section in (request.sections or []):
            for item in section.items:
                product_subtotal += (item.unit_price * item.quantity)
                product_discount += item.discount

        # Calculate labor total
        for labor_item in (request.labor or []):
            labor_subtotal = (
                (labor_item.regular_hours * labor_item.hourly_rate) +
                (labor_item.overtime_hours * labor_item.hourly_rate * 1.5) +
                (labor_item.double_time_hours * labor_item.hourly_rate * 2.0)
            ) * labor_item.quantity
            labor_total += labor_subtotal

        product_total = product_subtotal + product_discount  # discount is negative
        total_cost = product_total + labor_total + request.service_charge + request.tax_amount

        logger.info(f"💰 Calculated pricing: product_subtotal={product_subtotal}, product_discount={product_discount}, product_total={product_total}, labor_total={labor_total}, total_cost={total_cost}")

        # 4. Create new proposal
        proposal_id = uuid.uuid4()
        new_proposal = Proposal(
            id=proposal_id,
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
            version=request.version,
            notes=request.notes,
            internal_notes=request.internal_notes,
            product_subtotal=Decimal(str(product_subtotal)),
            product_discount=Decimal(str(product_discount)),
            product_total=Decimal(str(product_total)),
            labor_total=Decimal(str(labor_total)),
            service_charge=Decimal(str(request.service_charge)),
            tax_amount=Decimal(str(request.tax_amount)),
            total_cost=Decimal(str(total_cost)),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_proposal)
        db.flush()  # Get the proposal ID before adding related items

        logger.info(f"✅ Created proposal {new_proposal.job_number} (ID: {new_proposal.id})")

        # 5. Create sections and line items
        for section_idx, section_data in enumerate(request.sections or []):
            section_id = uuid.uuid4()
            section_total = sum(
                (item.unit_price * item.quantity) + item.discount
                for item in section_data.items
            )

            new_section = ProposalSection(
                id=section_id,
                proposal_id=proposal_id,
                section_name=section_data.section_name,
                section_type=section_data.section_type,
                section_total=Decimal(str(section_total)),
                display_order=section_idx,
                is_expanded=True
            )
            db.add(new_section)

            # Add line items
            for item_idx, item_data in enumerate(section_data.items):
                item_subtotal = (item_data.unit_price * item_data.quantity) + item_data.discount

                new_item = ProposalLineItem(
                    id=uuid.uuid4(),
                    section_id=section_id,
                    proposal_id=proposal_id,
                    description=item_data.description,
                    quantity=item_data.quantity,
                    duration=item_data.duration,
                    unit_price=Decimal(str(item_data.unit_price)),
                    discount=Decimal(str(item_data.discount)),
                    subtotal=Decimal(str(item_subtotal)),
                    category=item_data.category,
                    notes=item_data.notes,
                    display_order=item_idx
                )
                db.add(new_item)

            logger.info(f"  ✓ Added section: {section_data.section_name} ({len(section_data.items)} items)")

        # 6. Create labor schedule
        for labor_idx, labor_data in enumerate(request.labor or []):
            # Parse labor date and times
            labor_date = None
            start_time_obj = None
            end_time_obj = None

            if labor_data.labor_date:
                try:
                    labor_date = datetime.strptime(labor_data.labor_date, '%Y-%m-%d').date()
                except:
                    pass

            if labor_data.start_time:
                try:
                    start_time_obj = datetime.strptime(labor_data.start_time, '%H:%M').time()
                except:
                    pass

            if labor_data.end_time:
                try:
                    end_time_obj = datetime.strptime(labor_data.end_time, '%H:%M').time()
                except:
                    pass

            labor_subtotal = (
                (labor_data.regular_hours * labor_data.hourly_rate) +
                (labor_data.overtime_hours * labor_data.hourly_rate * 1.5) +
                (labor_data.double_time_hours * labor_data.hourly_rate * 2.0)
            ) * labor_data.quantity

            new_labor = ProposalLabor(
                id=uuid.uuid4(),
                proposal_id=proposal_id,
                task_name=labor_data.task_name,
                quantity=labor_data.quantity,
                labor_date=labor_date or start_date,
                start_time=start_time_obj,
                end_time=end_time_obj,
                regular_hours=Decimal(str(labor_data.regular_hours)),
                overtime_hours=Decimal(str(labor_data.overtime_hours)),
                double_time_hours=Decimal(str(labor_data.double_time_hours)),
                hourly_rate=Decimal(str(labor_data.hourly_rate)),
                subtotal=Decimal(str(labor_subtotal)),
                notes=labor_data.notes,
                display_order=labor_idx
            )
            db.add(new_labor)

        if request.labor:
            logger.info(f"  ✓ Added {len(request.labor)} labor items")

        # 7. Create timeline events
        for timeline_idx, timeline_data in enumerate(request.timeline or []):
            # Parse event date and times
            event_date = None
            event_start_time = None
            event_end_time = None

            if timeline_data.event_date:
                try:
                    event_date = datetime.strptime(timeline_data.event_date, '%Y-%m-%d').date()
                except:
                    pass

            if timeline_data.start_time:
                try:
                    event_start_time = datetime.strptime(timeline_data.start_time, '%H:%M').time()
                except:
                    pass

            if timeline_data.end_time:
                try:
                    event_end_time = datetime.strptime(timeline_data.end_time, '%H:%M').time()
                except:
                    pass

            new_timeline = ProposalTimeline(
                id=uuid.uuid4(),
                proposal_id=proposal_id,
                event_date=event_date or start_date,
                start_time=event_start_time,
                end_time=event_end_time,
                title=timeline_data.title,
                location=timeline_data.location,
                setup_tasks=timeline_data.setup_tasks or [],
                equipment_needed=timeline_data.equipment_needed or [],
                cost=Decimal(str(timeline_data.cost)),
                notes=timeline_data.notes,
                display_order=timeline_idx
            )
            db.add(new_timeline)

        if request.timeline:
            logger.info(f"  ✓ Added {len(request.timeline)} timeline events")

        # 8. Commit all changes
        db.commit()
        db.refresh(new_proposal)

        logger.info(f"✅ Completed proposal creation with all sections, items, labor, and timeline")

        # 9. Generate JWT token for temp access
        token, expires_at = create_temp_access_token(
            recipient_email=request.client_email,
            proposal_id=str(new_proposal.id),
            proposal_job_number=new_proposal.job_number,
            duration_hours=request.access_duration_hours
        )

        # 10. Build access URL
        frontend_url = settings.FRONTEND_BASE_URL
        temp_access_url = f"{frontend_url}/proposal?token={token}"

        logger.info(f"🔐 Generated temp access link (expires: {expires_at.isoformat()})")

        # 11. Return response
        return OnboardClientResponse(
            success=True,
            message=f"Client {request.client_name} onboarded successfully with complete proposal",
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
                "product_subtotal": float(new_proposal.product_subtotal),
                "product_discount": float(new_proposal.product_discount),
                "product_total": float(new_proposal.product_total),
                "labor_total": float(new_proposal.labor_total),
                "service_charge": float(new_proposal.service_charge),
                "tax_amount": float(new_proposal.tax_amount),
                "total_cost": float(new_proposal.total_cost),
                "sections_count": len(request.sections or []),
                "items_count": sum(len(s.items) for s in (request.sections or [])),
                "labor_count": len(request.labor or []),
                "timeline_count": len(request.timeline or []),
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
