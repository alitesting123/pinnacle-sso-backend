# app/api/questions.py
"""Questions API endpoints for proposal equipment questions"""

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.proposals import ProposalQuestion, Proposal
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class CreateQuestionRequest(BaseModel):
    item_id: str
    item_name: str
    section_name: str
    question: str

class AnswerQuestionRequest(BaseModel):
    answer: str

def get_proposal_by_id_or_job_number(db: Session, proposal_id: str):
    """Helper to get proposal by UUID or job_number"""
    # First try as UUID
    try:
        proposal_uuid = uuid.UUID(proposal_id)
        proposal = db.query(Proposal).filter(Proposal.id == proposal_uuid).first()
        if proposal:
            return proposal
    except ValueError:
        pass  # Not a valid UUID, continue to job_number lookup
    
    # Try as job_number
    proposal = db.query(Proposal).filter(Proposal.job_number == proposal_id).first()
    return proposal

@router.get("/proposals/{proposal_id}/questions")
async def get_proposal_questions(
    proposal_id: str,
    request: Request,
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """Get all questions for a proposal"""
    user = getattr(request.state, 'user', None)
    
    try:
        # Get proposal by UUID or job_number
        proposal = get_proposal_by_id_or_job_number(db, proposal_id)
        
        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")
        
        # Build query
        query = db.query(ProposalQuestion).filter(
            ProposalQuestion.proposal_id == proposal.id
        )
        
        # Filter by status if provided
        if status:
            query = query.filter(ProposalQuestion.status == status)
        
        # Get questions ordered by most recent first
        questions = query.order_by(desc(ProposalQuestion.asked_at)).all()
        
        # Transform to frontend format
        questions_data = []
        for q in questions:
            questions_data.append({
                "id": str(q.id),
                "itemId": str(q.line_item_id) if q.line_item_id else "",
                "itemName": q.question_text[:50] + "..." if len(q.question_text) > 50 else q.question_text,
                "sectionName": "General",
                "question": q.question_text,
                "answer": q.answer_text,
                "status": q.status,
                "askedBy": q.asked_by_name or q.asked_by_email or "Unknown",
                "askedAt": q.asked_at.isoformat() if q.asked_at else datetime.utcnow().isoformat(),
                "answeredBy": q.answered_by,
                "answeredAt": q.answered_at.isoformat() if q.answered_at else None
            })
        
        return {
            "questions": questions_data,
            "total_count": len(questions_data),
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching questions for proposal {proposal_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch questions: {str(e)}")

@router.post("/proposals/{proposal_id}/questions")
async def create_question(
    proposal_id: str,
    question_data: CreateQuestionRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new equipment question"""
    user = getattr(request.state, 'user', None)
    
    try:
        logger.info(f"Creating question for proposal: {proposal_id}")
        logger.info(f"Question data: {question_data.dict()}")
        
        # Get proposal by UUID or job_number
        proposal = get_proposal_by_id_or_job_number(db, proposal_id)
        
        if not proposal:
            logger.error(f"Proposal not found: {proposal_id}")
            raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")
        
        logger.info(f"Found proposal: {proposal.id} (job_number: {proposal.job_number})")
        
        # Create new question
        new_question = ProposalQuestion(
            id=uuid.uuid4(),
            proposal_id=proposal.id,  # Use the UUID from the found proposal
            line_item_id=None,
            question_text=question_data.question,
            status='pending',
            priority='normal',
            asked_by_name=user.get('full_name') if user else 'Anonymous',
            asked_by_email=user.get('email') if user else None,
            asked_at=datetime.utcnow()
        )
        
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        
        logger.info(f"Created question {new_question.id} for proposal {proposal_id}")
        
        # Return in frontend format
        response_data = {
            "id": str(new_question.id),
            "itemId": question_data.item_id,
            "itemName": question_data.item_name,
            "sectionName": question_data.section_name,
            "question": new_question.question_text,
            "answer": None,
            "status": new_question.status,
            "askedBy": new_question.asked_by_name or new_question.asked_by_email or "Unknown",
            "askedAt": new_question.asked_at.isoformat(),
            "answeredBy": None,
            "answeredAt": None
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating question: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create question: {str(e)}")

@router.post("/questions/{question_id}/answer")
async def answer_question(
    question_id: str,
    answer_data: AnswerQuestionRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Answer a pending question"""
    user = getattr(request.state, 'user', None)
    
    try:
        logger.info(f"Answering question: {question_id}")
        
        # Convert to UUID
        try:
            question_uuid = uuid.UUID(question_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid question ID format: {question_id}")
        
        # Find the question
        question = db.query(ProposalQuestion).filter(
            ProposalQuestion.id == question_uuid
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
        
        # Update with answer
        question.answer_text = answer_data.answer
        question.status = 'answered'
        question.answered_by = user.get('full_name') if user else 'Support Team'
        question.answered_at = datetime.utcnow()
        
        db.commit()
        db.refresh(question)
        
        logger.info(f"Answered question {question_id}")
        
        # Return updated question in frontend format
        response_data = {
            "id": str(question.id),
            "itemId": str(question.line_item_id) if question.line_item_id else "",
            "itemName": question.question_text[:50],
            "sectionName": "General",
            "question": question.question_text,
            "answer": question.answer_text,
            "status": question.status,
            "askedBy": question.asked_by_name or question.asked_by_email or "Unknown",
            "askedAt": question.asked_at.isoformat(),
            "answeredBy": question.answered_by,
            "answeredAt": question.answered_at.isoformat() if question.answered_at else None
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question {question_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")