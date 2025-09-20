"""Proposals API endpoints"""

from fastapi import APIRouter, Request
from typing import List

router = APIRouter()

@router.get("/proposals")
async def get_proposals(request: Request):
    """Get user's proposals"""
    user = getattr(request.state, 'user', None)
    return {
        "proposals": [
            {
                "id": "prop-001",
                "client_name": "Sample Client",
                "event_location": "Sample Venue",
                "total_cost": 25000,
                "status": "tentative"
            }
        ],
        "user": user,
        "message": "Proposals endpoint working"
    }

@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str, request: Request):
    """Get specific proposal"""
    user = getattr(request.state, 'user', None)
    return {
        "proposal_id": proposal_id,
        "user": user,
        "client_name": "Sample Client",
        "total_cost": 25000,
        "message": "Individual proposal endpoint working"
    }
