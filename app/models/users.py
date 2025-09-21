# app/models/users.py
from sqlalchemy import Column, String, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PreApprovedUser(Base):
    """Read-only table managed by admin interface"""
    __tablename__ = "pre_approved_users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    company = Column(String)
    department = Column(String)
    roles = Column(JSON)  # ["user", "admin", "manager"]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    
    # Optional: Updated by your app after first login
    cognito_user_id = Column(String, unique=True, nullable=True)
    last_login = Column(DateTime)

class User(Base):
    """Active user sessions created by your app"""
    __tablename__ = "active_users"
    
    user_id = Column(String, primary_key=True)  # Cognito sub
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    company = Column(String)
    department = Column(String)
    roles = Column(JSON)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    pre_approved_id = Column(String)  # Links to pre_approved_users.id