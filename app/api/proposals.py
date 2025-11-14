# app/api/proposals.py
"""Proposals API endpoints - uses real database data from seeding scripts"""

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.database import get_db
from app.models.proposals import (
    Proposal, 
    ProposalSection, 
    ProposalLineItem, 
    ProposalTimeline, 
    ProposalLabor,
    ProposalQuestion
)
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/proposals")
async def get_proposals(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None
):
    """Get list of proposals with pagination"""
    user = getattr(request.state, 'user', None)
    
    try:
        # Build query
        query = db.query(Proposal)
        
        # Filter by status if provided
        if status:
            query = query.filter(Proposal.status == status)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        proposals = query.order_by(
            desc(Proposal.created_at)
        ).offset(skip).limit(limit).all()
        
        return {
            "proposals": [
                {
                    "id": str(proposal.id),
                    "job_number": proposal.job_number,
                    "client_name": proposal.client_name,
                    "client_email": proposal.client_email,
                    "client_company": proposal.client_company,
                    "venue": proposal.venue_name,
                    "event_location": proposal.event_location,
                    "start_date": proposal.start_date.isoformat() if proposal.start_date else None,
                    "end_date": proposal.end_date.isoformat() if proposal.end_date else None,
                    "product_subtotal": float(proposal.product_subtotal) if proposal.product_subtotal else 0,
                    "labor_total": float(proposal.labor_total) if proposal.labor_total else 0,
                    "total_cost": float(proposal.total_cost) if proposal.total_cost else 0,
                    "status": proposal.status,
                    "prepared_by": proposal.prepared_by,
                    "version": proposal.version,
                    "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
                    "updated_at": proposal.updated_at.isoformat() if proposal.updated_at else None
                }
                for proposal in proposals
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "user": user
        }
    except Exception as e:
        logger.error(f"Error fetching proposals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposals: {str(e)}")

@router.get("/proposals/{proposal_id}")
async def get_proposal(
    proposal_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get detailed proposal with all sections, items, timeline, and labor"""
    user = getattr(request.state, 'user', None)
    
    try:
        # Check if proposal_id is a valid UUID format
        import uuid
        try:
            uuid_obj = uuid.UUID(proposal_id)
            # If valid UUID, search by ID
            proposal = db.query(Proposal).filter(
                Proposal.id == uuid_obj
            ).first()
        except ValueError:
            # Not a valid UUID, search by job_number instead
            proposal = db.query(Proposal).filter(
                Proposal.job_number == proposal_id
            ).first()
        
        if not proposal:
            raise HTTPException(
                status_code=404, 
                detail=f"Proposal {proposal_id} not found"
            )
        
        # ... rest of your code stays the same
        
        # Get sections with their line items
        sections = db.query(ProposalSection).filter(
            ProposalSection.proposal_id == proposal.id
        ).order_by(ProposalSection.display_order).all()
        
        sections_data = []
        for section in sections:
            line_items = db.query(ProposalLineItem).filter(
                ProposalLineItem.section_id == section.id
            ).order_by(ProposalLineItem.display_order).all()
            
            sections_data.append({
                "id": str(section.id),
                "title": section.section_name,
                "section_type": section.section_type,
                "isExpanded": section.is_expanded,
                "total": float(section.section_total) if section.section_total else 0,
                "notes": section.notes,
                "items": [
                    {
                        "id": str(item.id),
                        "item_number": item.item_number,
                        "quantity": item.quantity,
                        "description": item.description,
                        "duration": item.duration,
                        "price": float(item.unit_price) if item.unit_price else 0,
                        "discount": float(item.discount) if item.discount else 0,
                        "subtotal": float(item.subtotal) if item.subtotal else 0,
                        "category": item.category,
                        "item_type": item.item_type,
                        "notes": item.notes
                    }
                    for item in line_items
                ]
            })
        
        # Get timeline
        timeline = db.query(ProposalTimeline).filter(
            ProposalTimeline.proposal_id == proposal.id
        ).order_by(ProposalTimeline.display_order).all()
        
        timeline_data = [
            {
                "id": str(event.id),
                "date": event.event_date.isoformat() if event.event_date else None,
                "startTime": event.start_time.isoformat() if event.start_time else None,
                "endTime": event.end_time.isoformat() if event.end_time else None,
                "title": event.title,
                "location": event.location,
                "setup": event.setup_tasks or [],
                "equipment": event.equipment_needed or [],
                "cost": float(event.cost) if event.cost else 0,
                "notes": event.notes
            }
            for event in timeline
        ]
        
        # Get labor schedule
        labor = db.query(ProposalLabor).filter(
            ProposalLabor.proposal_id == proposal.id
        ).order_by(ProposalLabor.display_order).all()
        
        labor_data = [
            {
                "id": str(task.id),
                "task_name": task.task_name,
                "quantity": task.quantity,
                "date": task.labor_date.isoformat() if task.labor_date else None,
                "start_time": task.start_time.isoformat() if task.start_time else None,
                "end_time": task.end_time.isoformat() if task.end_time else None,
                "regular_hours": float(task.regular_hours) if task.regular_hours else 0,
                "overtime_hours": float(task.overtime_hours) if task.overtime_hours else 0,
                "double_time_hours": float(task.double_time_hours) if task.double_time_hours else 0,
                "hourly_rate": float(task.hourly_rate) if task.hourly_rate else 0,
                "subtotal": float(task.subtotal) if task.subtotal else 0,
                "notes": task.notes
            }
            for task in labor
        ]
        
        # Get questions if any
        questions = db.query(ProposalQuestion).filter(
            ProposalQuestion.proposal_id == proposal.id
        ).all()
        
        questions_data = [
            {
                "id": str(q.id),
                "question_text": q.question_text,
                "status": q.status,
                "priority": q.priority,
                "asked_by_name": q.asked_by_name,
                "asked_by_email": q.asked_by_email,
                "asked_at": q.asked_at.isoformat() if q.asked_at else None,
                "answer_text": q.answer_text,
                "answered_by": q.answered_by,
                "answered_at": q.answered_at.isoformat() if q.answered_at else None
            }
            for q in questions
        ]
        
        return {
            "eventDetails": {
                "id": str(proposal.id),
                "jobNumber": proposal.job_number,
                "clientName": proposal.client_name,
                "clientEmail": proposal.client_email,
                "clientCompany": proposal.client_company,
                "clientContact": proposal.client_contact,
                "clientPhone": proposal.client_phone,
                "venue": proposal.venue_name,
                "eventLocation": proposal.event_location,
                "startDate": proposal.start_date.isoformat() if proposal.start_date else None,
                "endDate": proposal.end_date.isoformat() if proposal.end_date else None,
                "preparedBy": proposal.prepared_by,
                "salesperson": proposal.salesperson,
                "email": proposal.salesperson_email,
                "status": proposal.status,
                "version": proposal.version,
                "lastModified": proposal.updated_at.isoformat() if proposal.updated_at else None,
                "notes": proposal.notes,
                "internalNotes": proposal.internal_notes
            },
            "pricing": {
                "productSubtotal": float(proposal.product_subtotal) if proposal.product_subtotal else 0,
                "productDiscount": float(proposal.product_discount) if proposal.product_discount else 0,
                "productTotal": float(proposal.product_total) if proposal.product_total else 0,
                "laborTotal": float(proposal.labor_total) if proposal.labor_total else 0,
                "serviceCharge": float(proposal.service_charge) if proposal.service_charge else 0,
                "taxAmount": float(proposal.tax_amount) if proposal.tax_amount else 0,
                "totalCost": float(proposal.total_cost) if proposal.total_cost else 0
            },
            "sections": sections_data,
            "timeline": timeline_data,
            "labor": labor_data,
            "questions": questions_data,
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching proposal {proposal_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposal details: {str(e)}")

@router.get("/proposals/search/by-client")
async def search_proposals_by_client(
    client_email: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Search proposals by client email"""
    user = getattr(request.state, 'user', None)
    
    try:
        proposals = db.query(Proposal).filter(
            Proposal.client_email == client_email
        ).order_by(desc(Proposal.created_at)).all()
        
        return {
            "client_email": client_email,
            "proposals": [
                {
                    "id": str(p.id),
                    "job_number": p.job_number,
                    "client_name": p.client_name,
                    "venue": p.venue_name,
                    "product_subtotal": float(p.product_subtotal) if p.product_subtotal else 0,
                    "labor_total": float(p.labor_total) if p.labor_total else 0,
                    "total_cost": float(p.total_cost) if p.total_cost else 0,
                    "status": p.status,
                    "start_date": p.start_date.isoformat() if p.start_date else None,
                    "end_date": p.end_date.isoformat() if p.end_date else None
                }
                for p in proposals
            ],
            "total_count": len(proposals),
            "user": user
        }
    except Exception as e:
        logger.error(f"Error searching proposals for {client_email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search proposals: {str(e)}")

@router.get("/proposals/search/by-job-number")
async def search_by_job_number(
    job_number: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Search proposal by job number"""
    user = getattr(request.state, 'user', None)
    
    try:
        proposal = db.query(Proposal).filter(
            Proposal.job_number == job_number
        ).first()
        
        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal with job number {job_number} not found")
        
        return {
            "id": str(proposal.id),
            "job_number": proposal.job_number,
            "client_name": proposal.client_name,
            "client_email": proposal.client_email,
            "product_subtotal": float(proposal.product_subtotal) if proposal.product_subtotal else 0,
            "labor_total": float(proposal.labor_total) if proposal.labor_total else 0,
            "total_cost": float(proposal.total_cost) if proposal.total_cost else 0,
            "status": proposal.status,
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching for job number {job_number}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search by job number: {str(e)}")