# app/services/user_service.py
from sqlalchemy.orm import Session
from app.models.users import User, PreApprovedUser
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserValidationError(Exception):
    """Raised when user is not authorized"""
    pass

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def validate_and_get_user(self, cognito_data: dict) -> User:
        """Check if user is pre-approved, then get or create session record"""
        
        email = cognito_data.get("email")
        cognito_user_id = cognito_data.get("user_id")
        
        if not email:
            raise UserValidationError("No email found in token")
        
        # Check pre-approved users table (read-only)
        pre_approved = self.db.query(PreApprovedUser).filter(
            PreApprovedUser.email == email,
            PreApprovedUser.is_active == True
        ).first()
        
        if not pre_approved:
            logger.warning(f"Unauthorized login attempt: {email}")
            raise UserValidationError(f"User {email} is not authorized to access this system")
        
        # Check if active session exists
        user = self.db.query(User).filter(
            User.user_id == cognito_user_id
        ).first()
        
        if user:
            # Update existing session
            user.last_login = datetime.utcnow()
            # Sync any updated info from pre-approved record
            user.full_name = pre_approved.full_name or user.full_name
            user.company = pre_approved.company or user.company
            user.department = pre_approved.department or user.department
            user.roles = pre_approved.roles or user.roles
            self.db.commit()
            logger.info(f"Updated session for user: {email}")
            return user
        
        # Create new session from pre-approved data
        user = User(
            user_id=cognito_user_id,
            email=pre_approved.email,
            full_name=pre_approved.full_name or cognito_data.get("full_name", ""),
            company=pre_approved.company,
            department=pre_approved.department,
            roles=pre_approved.roles or ["user"],
            is_active=True,
            last_login=datetime.utcnow(),
            pre_approved_id=pre_approved.id
        )
        
        # Optional: Update pre-approved record with Cognito ID for tracking
        if not pre_approved.cognito_user_id:
            pre_approved.cognito_user_id = cognito_user_id
            pre_approved.last_login = datetime.utcnow()
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created session for pre-approved user: {email}")
        return user
    
    def is_user_approved(self, email: str) -> bool:
        """Simple check if user is in approved list"""
        return self.db.query(PreApprovedUser).filter(
            PreApprovedUser.email == email,
            PreApprovedUser.is_active == True
        ).first() is not None
    
    def get_user_by_email(self, email: str) -> User:
        """Get active user by email"""
        return self.db.query(User).filter(
            User.email == email,
            User.is_active == True
        ).first()
    
    def deactivate_user_session(self, user_id: str) -> bool:
        """Deactivate user session"""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False