# app/models/proposals.py - Complete corrected file with ForeignKey constraints
from sqlalchemy import Column, String, Date, Time, Numeric, Integer, Boolean, DateTime, Text, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.users import Base  # Use the same Base from users.py
from datetime import datetime
import uuid

class Proposal(Base):
    """Main proposal/quote table"""
    __tablename__ = "proposals"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job information
    job_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Client information
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), index=True)
    client_company = Column(String(255))
    client_contact = Column(String(255))
    client_phone = Column(String(50))
    
    # Event details
    event_location = Column(String(255))
    venue_name = Column(String(255))
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # Proposal metadata
    prepared_by = Column(String(255))
    salesperson = Column(String(255))
    salesperson_email = Column(String(255))
    status = Column(String(50), default='tentative', index=True)
    version = Column(String(20), default='1.0')
    
    # Pricing breakdown
    product_subtotal = Column(Numeric(10, 2), default=0)
    product_discount = Column(Numeric(10, 2), default=0)
    product_total = Column(Numeric(10, 2), default=0)
    labor_total = Column(Numeric(10, 2), default=0)
    service_charge = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_cost = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_modified_by = Column(String(255))
    
    # Additional fields
    notes = Column(Text)
    internal_notes = Column(Text)
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime)
    terms_accepted_by = Column(String(255))
    
    # Relationships
    sections = relationship("ProposalSection", back_populates="proposal", cascade="all, delete-orphan")
    line_items = relationship("ProposalLineItem", back_populates="proposal", cascade="all, delete-orphan")
    timeline = relationship("ProposalTimeline", back_populates="proposal", cascade="all, delete-orphan")
    labor = relationship("ProposalLabor", back_populates="proposal", cascade="all, delete-orphan")
    questions = relationship("ProposalQuestion", back_populates="proposal", cascade="all, delete-orphan")


class ProposalSection(Base):
    """Proposal sections (Audio, Video, Lighting, etc.)"""
    __tablename__ = "proposal_sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('proposals.id'), nullable=False, index=True)
    
    section_name = Column(String(100), nullable=False)
    section_type = Column(String(50))
    display_order = Column(Integer, default=0)
    is_expanded = Column(Boolean, default=True)
    section_total = Column(Numeric(10, 2), default=0)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    proposal = relationship("Proposal", back_populates="sections")
    items = relationship("ProposalLineItem", back_populates="section", cascade="all, delete-orphan")


class ProposalLineItem(Base):
    """Individual line items (equipment, services)"""
    __tablename__ = "proposal_line_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey('proposal_sections.id'), nullable=False, index=True)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('proposals.id'), nullable=False, index=True)
    
    # Item details
    item_number = Column(String(50))
    description = Column(Text, nullable=False)
    quantity = Column(Integer, default=1)
    duration = Column(String(50))
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Categorization
    category = Column(String(100))
    item_type = Column(String(50))
    
    # Additional info
    notes = Column(Text)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    section = relationship("ProposalSection", back_populates="items")
    proposal = relationship("Proposal", back_populates="line_items")
    questions = relationship("ProposalQuestion", back_populates="line_item")


class ProposalTimeline(Base):
    """Event timeline and schedule"""
    __tablename__ = "proposal_timeline"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('proposals.id'), nullable=False, index=True)
    
    event_date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    title = Column(String(255), nullable=False)
    location = Column(String(255))
    
    setup_tasks = Column(ARRAY(Text))
    equipment_needed = Column(ARRAY(Text))
    
    cost = Column(Numeric(10, 2), default=0)
    display_order = Column(Integer, default=0)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    proposal = relationship("Proposal", back_populates="timeline")


class ProposalLabor(Base):
    """Labor schedule and costs"""
    __tablename__ = "proposal_labor"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('proposals.id'), nullable=False, index=True)
    
    task_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    labor_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    regular_hours = Column(Numeric(5, 2), default=0)
    overtime_hours = Column(Numeric(5, 2), default=0)
    double_time_hours = Column(Numeric(5, 2), default=0)
    
    hourly_rate = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    notes = Column(Text)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    proposal = relationship("Proposal", back_populates="labor")


class ProposalQuestion(Base):
    """Client questions about proposal items"""
    __tablename__ = "proposal_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('proposals.id'), nullable=False, index=True)
    line_item_id = Column(UUID(as_uuid=True), ForeignKey('proposal_line_items.id'))

    question_text = Column(Text, nullable=False)
    status = Column(String(50), default='pending')
    priority = Column(String(20), default='normal')

    asked_by_name = Column(String(255))
    asked_by_email = Column(String(255))
    asked_at = Column(DateTime, default=datetime.utcnow)

    answer_text = Column(Text)
    answered_by = Column(String(255))
    answered_at = Column(DateTime)
    ai_generated = Column(Boolean, default=False)  # Flag for AI-generated answers

    internal_notes = Column(Text)
    requires_follow_up = Column(Boolean, default=False)

    # Relationships
    proposal = relationship("Proposal", back_populates="questions")
    line_item = relationship("ProposalLineItem", back_populates="questions")


class SecureProposalLink(Base):
    """Temporary access links for clients"""
    __tablename__ = "proposal_temp_links"
    
    token = Column(String(255), primary_key=True)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('proposals.id'), nullable=False, index=True)
    
    user_email = Column(String(255), nullable=False, index=True)
    user_name = Column(String(255))
    company = Column(String(255))
    
    permissions = Column(JSONB, default={"permissions": ["view"]})
    expires_at = Column(DateTime, nullable=False)
    session_duration_minutes = Column(Integer, default=20)
    
    is_active = Column(Boolean, default=True, index=True)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255))
    
    revoked_at = Column(DateTime)
    revoked_by = Column(String(255))


class ProposalSession(Base):
    """Active client viewing sessions"""
    __tablename__ = "proposal_sessions"
    
    session_id = Column(String(255), primary_key=True)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('proposals.id'), nullable=False, index=True)
    temp_token = Column(String(255), ForeignKey('proposal_temp_links.token'))
    
    user_email = Column(String(255), nullable=False)
    user_name = Column(String(255))
    company = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    is_active = Column(Boolean, default=True, index=True)
    extension_count = Column(Integer, default=0)