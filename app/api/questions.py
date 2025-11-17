# app/api/questions.py
"""Questions API endpoints for proposal equipment questions"""

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.proposals import ProposalQuestion, Proposal
from app.services.rag_service import get_rag_service
from pydantic import BaseModel
from typing import Optional, Dict, Any
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

class AIAnswerRequest(BaseModel):
    use_rag: Optional[bool] = True
    auto_save: Optional[bool] = False

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

# ============================================================================
# SHARED HANDLER FUNCTION
# ============================================================================
async def _get_proposal_questions_handler(
    proposal_id: str,
    request: Request,
    db: Session,
    status: Optional[str] = None
):
    """Shared handler for getting proposal questions"""
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

# ============================================================================
# GET QUESTIONS ROUTES (WITH AND WITHOUT TRAILING SLASH)
# ============================================================================

@router.get("/proposals/{proposal_id}/questions")
async def get_proposal_questions(
    proposal_id: str,
    request: Request,
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """Get all questions for a proposal (without trailing slash)"""
    return await _get_proposal_questions_handler(proposal_id, request, db, status)

@router.get("/proposals/{proposal_id}/questions/")
async def get_proposal_questions_trailing_slash(
    proposal_id: str,
    request: Request,
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """Get all questions for a proposal (with trailing slash)"""
    return await _get_proposal_questions_handler(proposal_id, request, db, status)

# ============================================================================
# SHARED HANDLER FOR CREATING QUESTIONS
# ============================================================================
async def _create_question_handler(
    proposal_id: str,
    question_data: CreateQuestionRequest,
    request: Request,
    db: Session
):
    """Shared handler for creating questions"""
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

# ============================================================================
# CREATE QUESTION ROUTES (WITH AND WITHOUT TRAILING SLASH)
# ============================================================================

@router.post("/proposals/{proposal_id}/questions")
async def create_question(
    proposal_id: str,
    question_data: CreateQuestionRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new equipment question (without trailing slash)"""
    return await _create_question_handler(proposal_id, question_data, request, db)

@router.post("/proposals/{proposal_id}/questions/")
async def create_question_trailing_slash(
    proposal_id: str,
    question_data: CreateQuestionRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new equipment question (with trailing slash)"""
    return await _create_question_handler(proposal_id, question_data, request, db)

# ============================================================================
# ANSWER QUESTION ROUTE
# ============================================================================

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

# ============================================================================
# AI-POWERED AUTO-ANSWER ROUTES
# ============================================================================

@router.post("/questions/{question_id}/ai-answer")
async def ai_answer_question(
    question_id: str,
    ai_request: AIAnswerRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Generate an AI-powered answer for a question using RAG

    This endpoint uses Claude AI with Retrieval-Augmented Generation to:
    1. Determine if the question is simple or complex
    2. For simple questions: Answer directly with AI
    3. For complex questions: Retrieve relevant proposal context and generate informed answer

    Parameters:
    - use_rag: Whether to use RAG (default: True). If False, uses simple LLM answering
    - auto_save: If True, automatically saves the AI-generated answer to the database
    """
    user = getattr(request.state, 'user', None)

    try:
        logger.info(f"Generating AI answer for question: {question_id}")

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

        # Get the associated proposal
        proposal = db.query(Proposal).filter(
            Proposal.id == question.proposal_id
        ).first()

        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal for question {question_id} not found")

        # Get RAG service
        rag_service = get_rag_service()

        # Generate answer
        result = await rag_service.answer_question(
            question=question.question_text,
            proposal=proposal,
            db=db,
            use_rag=ai_request.use_rag
        )

        # If auto_save is enabled, save the answer
        if ai_request.auto_save and result.get('answer'):
            question.answer_text = result['answer']
            question.status = 'answered'
            question.answered_by = f"AI Assistant ({user.get('full_name') if user else 'System'})"
            question.answered_at = datetime.utcnow()

            db.commit()
            db.refresh(question)
            logger.info(f"Auto-saved AI answer for question {question_id}")

        # Return comprehensive response
        response_data = {
            "question_id": str(question.id),
            "question": question.question_text,
            "ai_answer": result.get('answer'),
            "method": result.get('method'),
            "confidence": result.get('confidence'),
            "sources": result.get('sources', []),
            "reasoning": result.get('reasoning'),
            "auto_saved": ai_request.auto_save,
            "current_status": question.status,
            "answered_by": question.answered_by,
            "answered_at": question.answered_at.isoformat() if question.answered_at else None
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI answer for question {question_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate AI answer: {str(e)}")


@router.post("/proposals/{proposal_id}/questions/ask-ai")
async def ask_ai_about_proposal(
    proposal_id: str,
    question_data: Dict[str, Any],
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Ask a question about a proposal and get an immediate AI answer without creating a question record

    This is useful for interactive Q&A where you want immediate answers without saving every question.

    Request body:
    {
        "question": "What is the total cost?",
        "use_rag": true  // optional, default true
    }
    """
    try:
        question_text = question_data.get('question')
        if not question_text:
            raise HTTPException(status_code=400, detail="Question text is required")

        use_rag = question_data.get('use_rag', True)

        logger.info(f"AI question for proposal {proposal_id}: {question_text}")

        # Get proposal
        proposal = get_proposal_by_id_or_job_number(db, proposal_id)

        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")

        # Get RAG service
        rag_service = get_rag_service()

        # Generate answer
        result = await rag_service.answer_question(
            question=question_text,
            proposal=proposal,
            db=db,
            use_rag=use_rag
        )

        # Return response
        response_data = {
            "proposal_id": str(proposal.id),
            "job_number": proposal.job_number,
            "question": question_text,
            "answer": result.get('answer'),
            "method": result.get('method'),
            "confidence": result.get('confidence'),
            "sources": result.get('sources', []),
            "reasoning": result.get('reasoning')
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error with AI question for proposal {proposal_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process AI question: {str(e)}")


@router.delete("/proposals/{proposal_id}/rag-cache")
async def clear_proposal_rag_cache(
    proposal_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Clear the RAG vector store cache for a specific proposal

    Use this when a proposal has been updated and you want to reindex its content
    """
    try:
        # Verify proposal exists
        proposal = get_proposal_by_id_or_job_number(db, proposal_id)

        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")

        # Clear cache
        rag_service = get_rag_service()
        rag_service.clear_cache(str(proposal.id))

        logger.info(f"Cleared RAG cache for proposal {proposal_id}")

        return {
            "message": f"RAG cache cleared for proposal {proposal_id}",
            "proposal_id": str(proposal.id),
            "job_number": proposal.job_number
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing RAG cache for proposal {proposal_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear RAG cache: {str(e)}")