# app/api/admin_read.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import PreApprovedUser, User
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ApprovedUserResponse(BaseModel):
    id: str
    email: str
    full_name: str = None
    company: str = None
    department: str = None
    roles: List[str]
    is_active: bool
    created_at: datetime = None
    has_logged_in: bool
    last_login: datetime = None

class UserStatsResponse(BaseModel):
    total_approved: int
    total_logged_in: int
    active_sessions: int

@router.get("/admin/approved-users", response_model=List[ApprovedUserResponse])
async def list_approved_users(db: Session = Depends(get_db)):
    """Read-only list of approved users"""
    users = db.query(PreApprovedUser).filter(
        PreApprovedUser.is_active == True
    ).all()
    
    return [
        ApprovedUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company=user.company,
            department=user.department,
            roles=user.roles or [],
            is_active=user.is_active,
            created_at=user.created_at,
            has_logged_in=bool(user.cognito_user_id),
            last_login=user.last_login
        )
        for user in users
    ]

@router.get("/admin/user-stats", response_model=UserStatsResponse)
async def get_user_stats(db: Session = Depends(get_db)):
    """Get user statistics"""
    total_approved = db.query(PreApprovedUser).filter(
        PreApprovedUser.is_active == True
    ).count()
    
    total_logged_in = db.query(PreApprovedUser).filter(
        PreApprovedUser.cognito_user_id.isnot(None)
    ).count()
    
    active_sessions = db.query(User).filter(
        User.is_active == True
    ).count()
    
    return UserStatsResponse(
        total_approved=total_approved,
        total_logged_in=total_logged_in,
        active_sessions=active_sessions
    )