"""Questions API endpoints"""

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/questions")
async def get_questions(request: Request):
    """Get equipment questions"""
    user = getattr(request.state, 'user', None)
    return {
        "questions": [
            {
                "id": "q-001",
                "question": "Sample equipment question?",
                "status": "pending",
                "asked_by": user.get("full_name") if user else "Unknown"
            }
        ],
        "user": user
    }

@router.post("/questions")
async def create_question(request: Request):
    """Create new question"""
    user = getattr(request.state, 'user', None)
    return {
        "message": "Question created",
        "user": user
    }
