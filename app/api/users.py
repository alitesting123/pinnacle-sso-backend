"""Users API endpoints"""

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/users/me")
async def get_current_user(request: Request):
    """Get current user from SSO"""
    user = getattr(request.state, 'user', None)
    if not user:
        return {"error": "No user found in request"}
    return {"user": user}
