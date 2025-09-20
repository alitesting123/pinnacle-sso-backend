"""Admin API endpoints"""

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/admin/health")
async def admin_health(request: Request):
    """Admin health check"""
    user = getattr(request.state, 'user', None)
    return {
        "status": "admin endpoints working",
        "user": user
    }
