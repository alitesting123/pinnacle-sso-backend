#!/usr/bin/env python3
"""
Create test proposal data for RAG testing
"""

import os
import sys
from datetime import date, time, datetime
from decimal import Decimal
import uuid

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.proposals import (
    Proposal, ProposalSection, ProposalLineItem,
    ProposalTimeline, ProposalLabor
)

def create_test_proposal(db):
    """Create a test proposal with comprehensive data for RAG testing"""

    print("Creating test proposal...")

    # Check if proposal already exists
    existing = db.query(Proposal).filter_by(job_number="JOB-2024-001").first()
    if existing:
        print(f"✓ Test proposal already exists: {existing.job_number}")
        return existing

    # Create proposal
    proposal = Proposal(
        id=uuid.uuid4(),
        job_number="JOB-2024-001",

        # Client info
        client_name="Acme Corporation",
        client_email="events@acme.com",
        client_company="Acme Corp",
        client_contact="John Smith",
        client_phone="555-0123",

        # Event details
        event_location="Grand Ballroom, Downtown Convention Center",
        venue_name="Downtown Convention Center",
        start_date=date(2024, 12, 15),
        end_date=date(2024, 12, 15),

        # Proposal metadata
        prepared_by="Jane Doe",
        salesperson="Mike Johnson",
        salesperson_email="mike@pinnaclelive.com",
        status="tentative",
        version="1.0",

        # Pricing
        product_subtotal=Decimal("15000.00"),
        product_discount=Decimal("1500.00"),
        product_total=Decimal("13500.00"),
        labor_total=Decimal("3500.00"),
        service_charge=Decimal("850.00"),
        tax_amount=Decimal("1785.00"),
        total_cost=Decimal("19635.00"),

        # Notes
        notes="Corporate event for 500 attendees. Full AV setup required including audio, video, and lighting systems.",
        internal_notes="Client is price-sensitive but values quality. Previous customer with good payment history."
    )

    db.add(proposal)
    db.flush()  # Get the ID

    print(f"✓ Created proposal: {proposal.job_number}")

    # Create Audio Section
    audio_section = ProposalSection(
        id=uuid.uuid4(),
        proposal_id=proposal.id,
        section_name="Audio",
        section_type="equipment",
        display_order=1,
        is_expanded=True,
        section_total=Decimal("8000.00"),
        notes="Professional audio system for main stage and breakout rooms"
    )
    db.add(audio_section)
    db.flush()

    # Audio line items
    audio_items = [
        {
            "description": "QSC KLA12 Line Array Speakers",
            "quantity": 8,
            "unit_price": Decimal("500.00"),
            "subtotal": Decimal("4000.00"),
            "notes": "Main PA system for ballroom coverage"
        },
        {
            "description": "Shure ULXD Wireless Microphone System",
            "quantity": 4,
            "unit_price": Decimal("250.00"),
            "subtotal": Decimal("1000.00"),
            "notes": "Handheld and lavalier options"
        },
        {
            "description": "Yamaha TF5 Digital Mixing Console",
            "quantity": 1,
            "unit_price": Decimal("1500.00"),
            "subtotal": Decimal("1500.00"),
            "notes": "32-channel digital mixer with scene recall"
        },
        {
            "description": "dbx DriveRack PA2 Speaker Management",
            "quantity": 1,
            "unit_price": Decimal("500.00"),
            "subtotal": Decimal("500.00"),
            "notes": "System optimization and protection"
        },
        {
            "description": "Audio Cables and Accessories Package",
            "quantity": 1,
            "unit_price": Decimal("1000.00"),
            "subtotal": Decimal("1000.00"),
            "notes": "XLR, power, and networking cables"
        }
    ]

    for item_data in audio_items:
        item = ProposalLineItem(
            id=uuid.uuid4(),
            section_id=audio_section.id,
            proposal_id=proposal.id,
            **item_data,
            category="Audio",
            item_type="rental"
        )
        db.add(item)

    # Create Video Section
    video_section = ProposalSection(
        id=uuid.uuid4(),
        proposal_id=proposal.id,
        section_name="Video",
        section_type="equipment",
        display_order=2,
        is_expanded=True,
        section_total=Decimal("6000.00"),
        notes="Video production and IMAG for main stage"
    )
    db.add(video_section)
    db.flush()

    # Video line items
    video_items = [
        {
            "description": "Sony PXW-Z280 4K Camera with Operator",
            "quantity": 2,
            "unit_price": Decimal("1500.00"),
            "subtotal": Decimal("3000.00"),
            "notes": "Main and backup camera positions"
        },
        {
            "description": "LED Video Wall 10ft x 6ft",
            "quantity": 1,
            "unit_price": Decimal("2000.00"),
            "subtotal": Decimal("2000.00"),
            "notes": "P3.9mm indoor LED, rear access"
        },
        {
            "description": "Video Switcher and Playback System",
            "quantity": 1,
            "unit_price": Decimal("1000.00"),
            "subtotal": Decimal("1000.00"),
            "notes": "Roland V-60HD with playback laptop"
        }
    ]

    for item_data in video_items:
        item = ProposalLineItem(
            id=uuid.uuid4(),
            section_id=video_section.id,
            proposal_id=proposal.id,
            **item_data,
            category="Video",
            item_type="rental"
        )
        db.add(item)

    # Create Lighting Section
    lighting_section = ProposalSection(
        id=uuid.uuid4(),
        proposal_id=proposal.id,
        section_name="Lighting",
        section_type="equipment",
        display_order=3,
        is_expanded=True,
        section_total=Decimal("2500.00"),
        notes="Stage and ambient lighting package"
    )
    db.add(lighting_section)
    db.flush()

    # Lighting line items
    lighting_items = [
        {
            "description": "Chauvet Rogue R2 Spot Moving Lights",
            "quantity": 6,
            "unit_price": Decimal("200.00"),
            "subtotal": Decimal("1200.00"),
            "notes": "Spot lighting for stage"
        },
        {
            "description": "Chroma-Q Color Force II LED Battens",
            "quantity": 4,
            "unit_price": Decimal("150.00"),
            "subtotal": Decimal("600.00"),
            "notes": "RGB color wash"
        },
        {
            "description": "Lighting Control Console (ETC Ion)",
            "quantity": 1,
            "unit_price": Decimal("500.00"),
            "subtotal": Decimal("500.00"),
            "notes": "Full lighting control with cue programming"
        },
        {
            "description": "Haze Machine",
            "quantity": 1,
            "unit_price": Decimal("200.00"),
            "subtotal": Decimal("200.00"),
            "notes": "For light beam effects"
        }
    ]

    for item_data in lighting_items:
        item = ProposalLineItem(
            id=uuid.uuid4(),
            section_id=lighting_section.id,
            proposal_id=proposal.id,
            **item_data,
            category="Lighting",
            item_type="rental"
        )
        db.add(item)

    # Create Timeline
    timeline_items = [
        {
            "event_date": date(2024, 12, 15),
            "start_time": time(8, 0),
            "end_time": time(12, 0),
            "title": "Load-in and Setup",
            "location": "Grand Ballroom",
            "setup_tasks": ["Unload trucks", "Stage build", "Audio setup", "Video setup", "Lighting rig"],
            "equipment_needed": ["Forklift", "Scissor lifts (2)", "Tools"],
            "cost": Decimal("1500.00"),
            "display_order": 1,
            "notes": "Early access required - confirm with venue"
        },
        {
            "event_date": date(2024, 12, 15),
            "start_time": time(13, 0),
            "end_time": time(14, 0),
            "title": "Sound Check and Rehearsal",
            "location": "Grand Ballroom",
            "setup_tasks": ["Test all systems", "Line check", "Run presentations"],
            "equipment_needed": ["All show equipment"],
            "cost": Decimal("500.00"),
            "display_order": 2
        },
        {
            "event_date": date(2024, 12, 15),
            "start_time": time(18, 0),
            "end_time": time(22, 0),
            "title": "Event - Main Program",
            "location": "Grand Ballroom",
            "setup_tasks": ["Monitor systems", "Run video playback", "Execute lighting cues"],
            "equipment_needed": ["All show equipment", "Show crew"],
            "cost": Decimal("1000.00"),
            "display_order": 3
        },
        {
            "event_date": date(2024, 12, 15),
            "start_time": time(22, 0),
            "end_time": time(2, 0),
            "title": "Strike and Load-out",
            "location": "Grand Ballroom",
            "setup_tasks": ["Pack equipment", "Clean venue", "Load trucks"],
            "equipment_needed": ["Forklift", "Road cases"],
            "cost": Decimal("500.00"),
            "display_order": 4,
            "notes": "Overtime rates apply after midnight"
        }
    ]

    for timeline_data in timeline_items:
        timeline = ProposalTimeline(
            id=uuid.uuid4(),
            proposal_id=proposal.id,
            **timeline_data
        )
        db.add(timeline)

    # Create Labor
    labor_items = [
        {
            "task_name": "Audio Engineer",
            "quantity": 1,
            "labor_date": date(2024, 12, 15),
            "start_time": time(8, 0),
            "end_time": time(23, 0),
            "regular_hours": Decimal("8.00"),
            "overtime_hours": Decimal("7.00"),
            "hourly_rate": Decimal("75.00"),
            "subtotal": Decimal("1125.00"),
            "display_order": 1
        },
        {
            "task_name": "Video Engineer",
            "quantity": 1,
            "labor_date": date(2024, 12, 15),
            "start_time": time(8, 0),
            "end_time": time(23, 0),
            "regular_hours": Decimal("8.00"),
            "overtime_hours": Decimal("7.00"),
            "hourly_rate": Decimal("75.00"),
            "subtotal": Decimal("1125.00"),
            "display_order": 2
        },
        {
            "task_name": "Lighting Designer",
            "quantity": 1,
            "labor_date": date(2024, 12, 15),
            "start_time": time(8, 0),
            "end_time": time(23, 0),
            "regular_hours": Decimal("8.00"),
            "overtime_hours": Decimal("7.00"),
            "hourly_rate": Decimal("75.00"),
            "subtotal": Decimal("1125.00"),
            "display_order": 3
        },
        {
            "task_name": "Stage Hands",
            "quantity": 2,
            "labor_date": date(2024, 12, 15),
            "start_time": time(8, 0),
            "end_time": time(2, 0),
            "regular_hours": Decimal("8.00"),
            "overtime_hours": Decimal("10.00"),
            "hourly_rate": Decimal("45.00"),
            "subtotal": Decimal("2025.00"),
            "display_order": 4,
            "notes": "2 crew members for load-in/out"
        }
    ]

    for labor_data in labor_items:
        labor = ProposalLabor(
            id=uuid.uuid4(),
            proposal_id=proposal.id,
            **labor_data
        )
        db.add(labor)

    db.commit()
    print("✓ Created complete test proposal with sections, items, timeline, and labor")

    return proposal


if __name__ == "__main__":
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        db_url = "postgresql://postgres.edygpoyhbcrkjmwvxaut:Thisiscool%402020@aws-1-us-east-2.pooler.supabase.com:6543/postgres"
        print(f"Using default database URL")

    print(f"Connecting to database...")

    try:
        # Create engine and session
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        # Create test data
        proposal = create_test_proposal(db)

        print("\n" + "=" * 60)
        print("Test Data Created Successfully!")
        print("=" * 60)
        print(f"\nProposal Details:")
        print(f"  Job Number: {proposal.job_number}")
        print(f"  Client: {proposal.client_name}")
        print(f"  Event Date: {proposal.start_date}")
        print(f"  Total Cost: ${proposal.total_cost}")
        print(f"\nYou can now test with:")
        print(f"  ./test_api_endpoints.sh")
        print(f"\nOr manually test:")
        print(f"  curl http://localhost:8000/api/v1/proposals/{proposal.job_number}/questions")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
