# scripts/create_proposal_schema.py
"""
Create comprehensive proposal database schema based on Pinnacle Live SOW structure
Run this to set up all proposal-related tables in Supabase
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL Schema for Proposals
CREATE_PROPOSALS_SCHEMA = """
-- Proposals Table (Main proposal header information)
CREATE TABLE IF NOT EXISTS proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_number VARCHAR(50) UNIQUE NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255),
    client_company VARCHAR(255),
    client_contact VARCHAR(255),
    client_phone VARCHAR(50),
    
    -- Event details
    event_location VARCHAR(255),
    venue_name VARCHAR(255),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Proposal metadata
    prepared_by VARCHAR(255),
    salesperson VARCHAR(255),
    salesperson_email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'tentative', -- tentative, confirmed, cancelled
    version VARCHAR(20) DEFAULT '1.0',
    
    -- Pricing
    product_subtotal DECIMAL(10,2) DEFAULT 0,
    product_discount DECIMAL(10,2) DEFAULT 0,
    product_total DECIMAL(10,2) DEFAULT 0,
    labor_total DECIMAL(10,2) DEFAULT 0,
    service_charge DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_cost DECIMAL(10,2) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_modified_by VARCHAR(255),
    
    -- Additional fields
    notes TEXT,
    internal_notes TEXT,
    terms_accepted BOOLEAN DEFAULT FALSE,
    terms_accepted_at TIMESTAMP,
    terms_accepted_by VARCHAR(255)
);

-- Proposal Sections (Audio, Video, Lighting, etc.)
CREATE TABLE IF NOT EXISTS proposal_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    section_name VARCHAR(100) NOT NULL, -- 'Audio', 'Video', 'Lighting', etc.
    section_type VARCHAR(50), -- 'equipment', 'labor', 'services'
    display_order INTEGER DEFAULT 0,
    is_expanded BOOLEAN DEFAULT TRUE,
    section_total DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Line Items (Individual equipment/services)
CREATE TABLE IF NOT EXISTS proposal_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section_id UUID NOT NULL REFERENCES proposal_sections(id) ON DELETE CASCADE,
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    
    -- Item details
    item_number VARCHAR(50),
    description TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    duration VARCHAR(50), -- "1 Days", "3 Days"
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(10,2) NOT NULL,
    
    -- Categorization
    category VARCHAR(100), -- 'audio', 'video', 'lighting', etc.
    item_type VARCHAR(50), -- 'equipment', 'labor', 'service'
    
    -- Additional info
    notes TEXT,
    display_order INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Event Timeline/Schedule
CREATE TABLE IF NOT EXISTS proposal_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    
    -- Schedule details
    event_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    title VARCHAR(255) NOT NULL, -- "Load-in & Setup", "Event Day 1"
    location VARCHAR(255),
    
    -- Setup information
    setup_tasks TEXT[], -- Array of setup tasks
    equipment_needed TEXT[], -- Array of equipment categories
    
    -- Costs
    cost DECIMAL(10,2) DEFAULT 0,
    
    -- Order and metadata
    display_order INTEGER DEFAULT 0,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Labor Schedule
CREATE TABLE IF NOT EXISTS proposal_labor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    
    -- Labor details
    task_name VARCHAR(255) NOT NULL, -- "Set Technician", "Audio Operator"
    quantity INTEGER DEFAULT 1,
    labor_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Hours breakdown
    regular_hours DECIMAL(5,2) DEFAULT 0,
    overtime_hours DECIMAL(5,2) DEFAULT 0,
    double_time_hours DECIMAL(5,2) DEFAULT 0,
    
    -- Rates and totals
    hourly_rate DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    
    -- Additional info
    notes TEXT,
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Client Questions/Requests
CREATE TABLE IF NOT EXISTS proposal_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    line_item_id UUID REFERENCES proposal_line_items(id) ON DELETE SET NULL,
    
    -- Question details
    question_text TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, answered, resolved
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high
    
    -- User info
    asked_by_name VARCHAR(255),
    asked_by_email VARCHAR(255),
    asked_at TIMESTAMP DEFAULT NOW(),
    
    -- Response
    answer_text TEXT,
    answered_by VARCHAR(255),
    answered_at TIMESTAMP,
    
    -- Internal tracking
    internal_notes TEXT,
    requires_follow_up BOOLEAN DEFAULT FALSE
);

-- Temporary Access Links (for client viewing)
CREATE TABLE IF NOT EXISTS proposal_temp_links (
    token VARCHAR(255) PRIMARY KEY,
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    
    -- User details
    user_email VARCHAR(255) NOT NULL,
    user_name VARCHAR(255),
    company VARCHAR(255),
    
    -- Access control
    permissions JSONB DEFAULT '["view"]'::jsonb,
    expires_at TIMESTAMP NOT NULL,
    session_duration_minutes INTEGER DEFAULT 20,
    
    -- Usage tracking
    is_active BOOLEAN DEFAULT TRUE,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),
    
    -- Revocation
    revoked_at TIMESTAMP,
    revoked_by VARCHAR(255)
);

-- Active Client Sessions
CREATE TABLE IF NOT EXISTS proposal_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    temp_token VARCHAR(255) REFERENCES proposal_temp_links(token),
    
    -- Session details
    user_email VARCHAR(255) NOT NULL,
    user_name VARCHAR(255),
    company VARCHAR(255),
    
    -- Timing
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    last_accessed TIMESTAMP DEFAULT NOW(),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    extension_count INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_proposals_job_number ON proposals(job_number);
CREATE INDEX IF NOT EXISTS idx_proposals_client_email ON proposals(client_email);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_dates ON proposals(start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_sections_proposal ON proposal_sections(proposal_id);
CREATE INDEX IF NOT EXISTS idx_line_items_proposal ON proposal_line_items(proposal_id);
CREATE INDEX IF NOT EXISTS idx_line_items_section ON proposal_line_items(section_id);
CREATE INDEX IF NOT EXISTS idx_timeline_proposal ON proposal_timeline(proposal_id);
CREATE INDEX IF NOT EXISTS idx_labor_proposal ON proposal_labor(proposal_id);
CREATE INDEX IF NOT EXISTS idx_questions_proposal ON proposal_questions(proposal_id);

CREATE INDEX IF NOT EXISTS idx_temp_links_proposal ON proposal_temp_links(proposal_id);
CREATE INDEX IF NOT EXISTS idx_temp_links_email ON proposal_temp_links(user_email);
CREATE INDEX IF NOT EXISTS idx_temp_links_active ON proposal_temp_links(is_active, expires_at);

CREATE INDEX IF NOT EXISTS idx_sessions_proposal ON proposal_sessions(proposal_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON proposal_sessions(is_active, expires_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
DROP TRIGGER IF EXISTS update_proposals_updated_at ON proposals;
CREATE TRIGGER update_proposals_updated_at
    BEFORE UPDATE ON proposals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sections_updated_at ON proposal_sections;
CREATE TRIGGER update_sections_updated_at
    BEFORE UPDATE ON proposal_sections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_line_items_updated_at ON proposal_line_items;
CREATE TRIGGER update_line_items_updated_at
    BEFORE UPDATE ON proposal_line_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""

def create_proposal_schema():
    """Execute the schema creation"""
    
    db_url = settings.DATABASE_URL
    
    if 'postgresql' not in db_url:
        logger.error("ERROR: Must use PostgreSQL database for this schema")
        logger.error("Update your .env file with DATABASE_URL from Supabase")
        return False
    
    try:
        logger.info("Connecting to database...")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            logger.info("Creating proposal schema...")
            
            # Execute the schema creation
            conn.execute(text(CREATE_PROPOSALS_SCHEMA))
            conn.commit()
            
            logger.info("✅ Proposal schema created successfully!")
            
            # Verify tables were created
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'proposal%'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            logger.info(f"\nCreated tables:")
            for table in tables:
                logger.info(f"  ✓ {table}")
            
            return True
            
    except Exception as e:
        logger.error(f"Failed to create schema: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_proposal_schema()
    sys.exit(0 if success else 1)