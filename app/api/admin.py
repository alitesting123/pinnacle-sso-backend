from fastapi import APIRouter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/admin/health")
async def admin_health():
    return {
        "status": "admin endpoints working",
        "timestamp": datetime.utcnow().isoformat()
    }