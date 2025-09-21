# app/models/proposals.py
from sqlalchemy import Column, String, JSON, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CustomerProposal(Base):
    __tablename__ = "customer_proposals"
    
    id = Column(String, primary_key=True)
    customer_email = Column(String, nullable=False, index=True)
    proposal_data = Column(JSON, nullable=False)  # The actual proposal content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default="active")  # active, draft, archived
    created_by = Column(String)  # Who created this proposal

class SecureProposalLink(Base):
    __tablename__ = "secure_proposal_links"
    
    token = Column(String, primary_key=True)
    customer_proposal_id = Column(String, nullable=False)  # Links to customer_proposals.id
    user_email = Column(String, nullable=False)
    user_name = Column(String)
    company = Column(String)
    permissions = Column(JSON)  # ["view", "comment"]
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    revoked_at = Column(DateTime)