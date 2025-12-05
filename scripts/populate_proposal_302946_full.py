#!/usr/bin/env python3
"""
Script to populate complete data for Proposal 302946
This script adds all missing sections, line items, timeline events, and labor items
"""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import uuid

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings

PROPOSAL_ID = "cd8849f5-c572-48fa-ad37-d10b298056db"

def get_db_engine():
    """Create database engine"""
    return create_engine(settings.DATABASE_URL)

def get_existing_section_id(conn):
    """Get the ID of the existing Royal Ballroom 1 Set Day section"""
    result = conn.execute(text("""
        SELECT id FROM proposal_sections
        WHERE proposal_id = :proposal_id
        AND section_name = 'Royal Ballroom 1 | Set Day | 3.13.2026'
    """), {"proposal_id": PROPOSAL_ID})
    row = result.fetchone()
    return row[0] if row else None

def add_missing_line_items_to_existing_section(conn, section_id):
    """Add the 26 missing line items to Royal Ballroom 1 Set Day section"""

    missing_items = [
        # Audio items
        ("Microphone Table Stand, Black", 6, "1 Days", "15.00", "-90.00", "0.00", "audio", None),
        ("Microphone Floor Stand, Black", 2, "1 Days", "15.00", "-30.00", "0.00", "audio", None),
        ("Mono Audio Direct Box", 1, "1 Days", "75.00", "-75.00", "0.00", "audio", None),
        ("Speaker Stand", 2, "1 Days", "35.00", "-70.00", "0.00", "audio", None),
        ("XLR to USB Audio Covertor, Mono", 1, "1 Days", "120.00", "-120.00", "0.00", "audio", None),
        ("Audio Cables", 1, "1 Days", "115.00", "-115.00", "0.00", "audio", None),

        # Computer items
        ("Laptop | Standard", 1, "1 Days", "280.00", "-280.00", "0.00", "computer", None),

        # Communications items
        ("Speaker Timer System", 1, "1 Days", "160.00", "-160.00", "0.00", "communications", None),
        ("PerfectCue System", 1, "1 Days", "155.00", "-155.00", "0.00", "communications", None),

        # Lighting items
        ("Digital Lighting Console, Standard", 1, "1 Days", "345.00", "-345.00", "0.00", "lighting", None),
        ("Lighting Safety Cable", 4, "1 Days", "15.00", "-60.00", "0.00", "lighting", None),
        ("Truss Clamp, Black", 4, "1 Days", "15.00", "-60.00", "0.00", "lighting", None),
        ("Lighting Cables", 1, "1 Days", "85.00", "-85.00", "0.00", "lighting", None),

        # Projection items
        ("Single Chip DLP Projector Lens, Short 0.8 - 1.0", 1, "1 Days", "165.00", "-165.00", "0.00", "projection", None),

        # Rigging items
        ("12\" Box Truss, Black, 10'", 2, "1 Days", "125.00", "-250.00", "0.00", "rigging", None),
        ("24\" Truss Base Plate, Black", 2, "1 Days", "30.00", "-60.00", "0.00", "rigging", None),

        # Staging items
        ("Drape Panel, 18' x 10' Slate", 2, "1 Days", "150.00", "-300.00", "0.00", "staging", "(2) sections of drape behind the riser"),

        # Supply items
        ("External Hard Drive", 1, "1 Sale", "0.00", "0.00", "0.00", "supply", None),

        # Video items
        ("Video Distribution Amplifier, HDMI 1:4", 1, "1 Days", "110.00", "-110.00", "0.00", "video", None),
        ("Rental Monitor, 24\" QHD", 1, "1 Days", "215.00", "-215.00", "0.00", "video", None),
        ("Video Distribution Amplifier, 3G-SDI 1:4", 1, "1 Days", "110.00", "-110.00", "0.00", "video", None),
        ("12G-SDI to HDMI Video Converter", 2, "1 Days", "30.00", "-60.00", "0.00", "video", None),
        ("Video Cables", 1, "1 Days", "115.00", "-115.00", "0.00", "video", None),
        ("PTZ Camera Controller", 1, "1 Days", "770.00", "-770.00", "0.00", "video", None),
        ("Camera Tripod w/Fluid Head", 1, "1 Days", "165.00", "-165.00", "0.00", "video", None),
        ("Video Production System, Recording unit", 1, "1 Days", "880.00", "-880.00", "0.00", "video", None),
    ]

    for item in missing_items:
        conn.execute(text("""
            INSERT INTO proposal_line_items
            (id, proposal_id, section_id, description, quantity, duration, unit_price, discount, subtotal, category, notes, created_at, updated_at)
            VALUES (:id, :proposal_id, :section_id, :description, :quantity, :duration, :unit_price, :discount, :subtotal, :category, :notes, :created_at, :updated_at)
        """), {
            "id": str(uuid.uuid4()),
            "proposal_id": PROPOSAL_ID,
            "section_id": section_id,
            "description": item[0],
            "quantity": item[1],
            "duration": item[2],
            "unit_price": Decimal(item[3]),
            "discount": Decimal(item[4]),
            "subtotal": Decimal(item[5]),
            "category": item[6],
            "notes": item[7],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })

    print(f"✅ Added {len(missing_items)} missing line items to Royal Ballroom 1 Set Day")

def create_new_sections(conn):
    """Create all 17 missing sections"""

    sections_data = [
        # Royal Ballroom 1 - Day 1 and Day 2
        {
            "key": "new-section-rb1-day1",  # Friendly key for referencing
            "section_name": "Royal Ballroom 1 | Day 1/2 | 3.14.2026",
            "section_type": "General Session",
            "section_date": "2026-03-14",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:30:00",
            "display_order": 2,
            "section_total": "15463.00",
            "notes": "Saturday, March 14 8:00 AM – 5:30 PM. Techs report one hour prior."
        },
        {
            "key": "new-section-rb1-day2",
            "section_name": "Royal Ballroom 1 | Day 2/2 | 3.15.2026",
            "section_type": "General Session",
            "section_date": "2026-03-15",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 3,
            "section_total": "17576.25",
            "notes": "Sunday, March 15 8:00 AM – 5:00 PM. Includes strike."
        },

        # Royal Ballroom 2 - Set, Day 1, Day 2
        {
            "key": "new-section-rb2-set",
            "section_name": "Royal Ballroom 2 | Set Day | 3.13.2026",
            "section_type": "General Session",
            "section_date": "2026-03-13",
            "start_time": "12:00:00",
            "event_time": "18:00:00",
            "end_time": "2026-03-15 17:00:00",
            "display_order": 4,
            "section_total": "4950.00",
            "notes": "Identical setup to Royal Ballroom 1"
        },
        {
            "key": "new-section-rb2-day1",
            "section_name": "Royal Ballroom 2 | Day 1/2 | 3.14.2026",
            "section_type": "General Session",
            "section_date": "2026-03-14",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:30:00",
            "display_order": 5,
            "section_total": "15463.00",
            "notes": "Saturday, March 14 8:00 AM – 5:30 PM. Techs report one hour prior."
        },
        {
            "key": "new-section-rb2-day2",
            "section_name": "Royal Ballroom 2 | Day 2/2 | 3.15.2026",
            "section_type": "General Session",
            "section_date": "2026-03-15",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 6,
            "section_total": "17576.25",
            "notes": "Sunday, March 15 8:00 AM – 5:00 PM. Includes strike."
        },

        # Royal Ballroom 3/4 - Set, Day 1, Day 2
        {
            "key": "new-section-rb34-set",
            "section_name": "Royal Ballroom 3/4 | Set Day | 3.13.2026",
            "section_type": "General Session",
            "section_date": "2026-03-13",
            "start_time": "12:00:00",
            "event_time": "18:00:00",
            "end_time": "2026-03-15 17:00:00",
            "display_order": 7,
            "section_total": "4950.00",
            "notes": "Identical setup to Royal Ballroom 1"
        },
        {
            "key": "new-section-rb34-day1",
            "section_name": "Royal Ballroom 3/4 | Day 1/2 | 3.14.2026",
            "section_type": "General Session",
            "section_date": "2026-03-14",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:30:00",
            "display_order": 8,
            "section_total": "15463.00",
            "notes": "Saturday, March 14 8:00 AM – 5:30 PM. Techs report one hour prior."
        },
        {
            "key": "new-section-rb34-day2",
            "section_name": "Royal Ballroom 3/4 | Day 2/2 | 3.15.2026",
            "section_type": "General Session",
            "section_date": "2026-03-15",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 9,
            "section_total": "17576.25",
            "notes": "Sunday, March 15 8:00 AM – 5:00 PM. Includes strike."
        },

        # Palmetto 5 - Set, Day 1, Day 2
        {
            "key": "new-section-p5-set",
            "section_name": "Palmetto 5 | Set Day | 3.13.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-13",
            "start_time": "12:00:00",
            "event_time": "17:00:00",
            "end_time": "2026-03-15 17:00:00",
            "display_order": 10,
            "section_total": "1810.00",
            "notes": "Breakfast, Lunch and Afternoon Sessions. Smaller setup for breakouts."
        },
        {
            "key": "new-section-p5-day1",
            "section_name": "Palmetto 5 | Day 1/2 | 3.14.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-14",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 11,
            "section_total": "4938.75",
            "notes": "Saturday, March 14 8:00 AM – 5:00 PM"
        },
        {
            "key": "new-section-p5-day2",
            "section_name": "Palmetto 5 | Day 2/2 | 3.15.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-15",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 12,
            "section_total": "5498.75",
            "notes": "Sunday, March 15 8:00 AM – 5:00 PM. Includes strike."
        },

        # Palmetto 6 - Set, Day 1, Day 2
        {
            "key": "new-section-p6-set",
            "section_name": "Palmetto 6 | Set Day | 3.13.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-13",
            "start_time": "12:00:00",
            "event_time": "17:00:00",
            "end_time": "2026-03-15 17:00:00",
            "display_order": 13,
            "section_total": "1790.00",
            "notes": "Identical setup to Palmetto 5"
        },
        {
            "key": "new-section-p6-day1",
            "section_name": "Palmetto 6 | Day 1/2 | 3.14.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-14",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 14,
            "section_total": "4938.75",
            "notes": "Saturday, March 14 8:00 AM – 5:00 PM"
        },
        {
            "key": "new-section-p6-day2",
            "section_name": "Palmetto 6 | Day 2/2 | 3.15.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-15",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 15,
            "section_total": "5498.75",
            "notes": "Sunday, March 15 8:00 AM – 5:00 PM. Includes strike."
        },

        # Palmetto 7 - Set, Day 1, Day 2
        {
            "key": "new-section-p7-set",
            "section_name": "Palmetto 7 | Set Day | 3.13.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-13",
            "start_time": "12:00:00",
            "event_time": "17:00:00",
            "end_time": "2026-03-15 17:00:00",
            "display_order": 16,
            "section_total": "1790.00",
            "notes": "Identical setup to Palmetto 5"
        },
        {
            "key": "new-section-p7-day1",
            "section_name": "Palmetto 7 | Day 1/2 | 3.14.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-14",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 17,
            "section_total": "4938.75",
            "notes": "Saturday, March 14 8:00 AM – 5:00 PM"
        },
        {
            "key": "new-section-p7-day2",
            "section_name": "Palmetto 7 | Day 2/2 | 3.15.2026",
            "section_type": "Breakout Session",
            "section_date": "2026-03-15",
            "start_time": "00:01:00",
            "event_time": "08:00:00",
            "end_time": "17:00:00",
            "display_order": 18,
            "section_total": "5498.75",
            "notes": "Sunday, March 15 8:00 AM – 5:00 PM. Includes strike."
        },
    ]

    section_ids = {}

    for section in sections_data:
        # Generate a proper UUID for this section
        section_uuid = str(uuid.uuid4())

        conn.execute(text("""
            INSERT INTO proposal_sections
            (id, proposal_id, section_name, section_type, display_order, is_expanded, section_total, notes, created_at, updated_at)
            VALUES (:id, :proposal_id, :section_name, :section_type, :display_order, :is_expanded, :section_total, :notes, :created_at, :updated_at)
        """), {
            "id": section_uuid,
            "proposal_id": PROPOSAL_ID,
            "section_name": section['section_name'],
            "section_type": section['section_type'],
            "display_order": section['display_order'],
            "is_expanded": True,
            "section_total": Decimal(section['section_total']),
            "notes": section.get('notes'),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })

        # Map the friendly key to the UUID
        section_ids[section['key']] = section_uuid

    print(f"✅ Created {len(sections_data)} new sections")
    return section_ids

def create_line_items_for_ballroom_days(conn, section_ids):
    """Create line items for all Royal Ballroom Day 1 and Day 2 sections"""

    # Standard ballroom equipment (same for all 3 ballrooms, Day 1 and Day 2)
    ballroom_items = [
        # Audio
        ("16ch Digital Audio Mixer", 1, "1 Days", "315.00", "0.00", "315.00", "audio"),
        ("Digital Audio Snake Stage Box", 1, "1 Days", "175.00", "0.00", "175.00", "audio"),
        ("Wired Gooseneck Podium Microphone", 1, "1 Days", "125.00", "0.00", "125.00", "audio"),
        ("Wireless Microphone Receiver, Quad", 2, "1 Days", "1125.00", "0.00", "2250.00", "audio"),
        ("Microphone Table Stand, Black", 6, "1 Days", "15.00", "0.00", "90.00", "audio"),
        ("Microphone Floor Stand, Black", 2, "1 Days", "15.00", "0.00", "30.00", "audio"),
        ("Mono Audio Direct Box", 1, "1 Days", "75.00", "0.00", "75.00", "audio"),
        ("12\" Powered Speaker", 2, "1 Days", "190.00", "0.00", "380.00", "audio"),
        ("Speaker Stand", 2, "1 Days", "35.00", "0.00", "70.00", "audio"),
        ("8\" Powered Speaker", 2, "1 Days", "160.00", "0.00", "320.00", "audio"),
        ("Pinnacle Live Music", 1, "1 Days", "195.00", "0.00", "195.00", "audio"),
        ("XLR to USB Audio Covertor, Mono", 1, "1 Days", "120.00", "0.00", "120.00", "audio"),
        ("Audio Cables", 1, "1 Days", "115.00", "0.00", "115.00", "audio"),

        # Computer
        ("Laptop | Standard", 1, "1 Days", "280.00", "-98.00", "182.00", "computer"),

        # Communications
        ("Speaker Timer System", 1, "1 Days", "160.00", "-8.00", "152.00", "communications"),
        ("PerfectCue System", 1, "1 Days", "155.00", "-7.75", "147.25", "communications"),

        # Lighting
        ("LED Uplight Kit, 6 Fixtures", 1, "1 Days", "615.00", "-61.50", "553.50", "lighting"),
        ("Digital Lighting Console, Standard", 1, "1 Days", "345.00", "-34.50", "310.50", "lighting"),
        ("LED Ellipsoidal Lighting Fixture", 4, "1 Days", "160.00", "-64.00", "576.00", "lighting"),
        ("Lighting Safety Cable", 4, "1 Days", "15.00", "0.00", "60.00", "lighting"),
        ("Truss Clamp, Black", 4, "1 Days", "15.00", "0.00", "60.00", "lighting"),
        ("Lighting Cables", 1, "1 Days", "85.00", "-8.50", "76.50", "lighting"),

        # Projection
        ("Fast Fold Screen | 9'x16'", 1, "1 Days", "655.00", "-65.50", "589.50", "projection"),
        ("Single Chip DLP Laser Projector, 12,000 Lumens", 1, "1 Days", "2195.00", "-219.50", "1975.50", "projection"),
        ("Single Chip DLP Projector Lens, Short 0.8 - 1.0", 1, "1 Days", "165.00", "-16.50", "148.50", "projection"),

        # Rigging
        ("12\" Box Truss, Black, 10'", 2, "1 Days", "125.00", "-25.00", "225.00", "rigging"),
        ("24\" Truss Base Plate, Black", 2, "1 Days", "30.00", "-6.00", "54.00", "rigging"),

        # Staging
        ("Drape Panel, 18' x 10' Slate", 2, "1 Days", "150.00", "-30.00", "270.00", "staging"),

        # Supply (Day 1 only gets this)
        ("External Hard Drive", 1, "1 Sale", "150.00", "-23.25", "126.75", "supply"),

        # Video
        ("Video Distribution Amplifier, HDMI 1:4", 1, "1 Days", "110.00", "0.00", "110.00", "video"),
        ("Video Switcher, 4K", 1, "1 Days", "565.00", "0.00", "565.00", "video"),
        ("Rental Monitor, 24\" QHD", 1, "1 Days", "215.00", "0.00", "215.00", "video"),
        ("Video Distribution Amplifier, 3G-SDI 1:4", 1, "1 Days", "110.00", "0.00", "110.00", "video"),
        ("12G-SDI to HDMI Video Converter", 2, "1 Days", "30.00", "0.00", "60.00", "video"),
        ("Confidence Monitor", 1, "1 Days", "780.00", "0.00", "780.00", "video"),
        ("Video Cables", 1, "1 Days", "115.00", "0.00", "115.00", "video"),
        ("PTZ Camera", 1, "1 Days", "770.00", "0.00", "770.00", "video"),
        ("PTZ Camera Controller", 1, "1 Days", "770.00", "0.00", "770.00", "video"),
        ("Camera Tripod w/Fluid Head", 1, "1 Days", "165.00", "0.00", "165.00", "video"),
        ("Video Production System, Recording unit", 1, "1 Days", "880.00", "0.00", "880.00", "video"),
    ]

    # Add items to all Royal Ballroom Day 1 sections (RB1, RB2, RB3/4)
    ballroom_day1_sections = ['new-section-rb1-day1', 'new-section-rb2-day1', 'new-section-rb34-day1']
    for section_key in ballroom_day1_sections:
        if section_key in section_ids:
            for item in ballroom_items:
                conn.execute(text("""
                    INSERT INTO proposal_line_items
                    (id, proposal_id, section_id, description, quantity, duration, unit_price, discount, subtotal, category, notes, created_at, updated_at)
                    VALUES (:id, :proposal_id, :section_id, :description, :quantity, :duration, :unit_price, :discount, :subtotal, :category, :notes, :created_at, :updated_at)
                """), {
                    "id": str(uuid.uuid4()),
                    "proposal_id": PROPOSAL_ID,
                    "section_id": section_ids[section_key],
                    "description": item[0],
                    "quantity": item[1],
                    "duration": item[2],
                    "unit_price": Decimal(item[3]),
                    "discount": Decimal(item[4]),
                    "subtotal": Decimal(item[5]),
                    "category": item[6],
                    "notes": None,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
            print(f"✅ Added {len(ballroom_items)} line items to section {section_key}")

    # Add items to all Royal Ballroom Day 2 sections (same items but no External Hard Drive)
    ballroom_day2_items = [item for item in ballroom_items if item[0] != "External Hard Drive"]
    ballroom_day2_sections = ['new-section-rb1-day2', 'new-section-rb2-day2', 'new-section-rb34-day2']

    for section_key in ballroom_day2_sections:
        if section_key in section_ids:
            for item in ballroom_day2_items:
                conn.execute(text("""
                    INSERT INTO proposal_line_items
                    (id, proposal_id, section_id, description, quantity, duration, unit_price, discount, subtotal, category, notes, created_at, updated_at)
                    VALUES (:id, :proposal_id, :section_id, :description, :quantity, :duration, :unit_price, :discount, :subtotal, :category, :notes, :created_at, :updated_at)
                """), {
                    "id": str(uuid.uuid4()),
                    "proposal_id": PROPOSAL_ID,
                    "section_id": section_ids[section_key],
                    "description": item[0],
                    "quantity": item[1],
                    "duration": item[2],
                    "unit_price": Decimal(item[3]),
                    "discount": Decimal(item[4]),
                    "subtotal": Decimal(item[5]),
                    "category": item[6],
                    "notes": None,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
            print(f"✅ Added {len(ballroom_day2_items)} line items to section {section_key}")

def create_line_items_for_ballroom_set_days(conn, section_ids):
    """Create line items for Royal Ballroom 2 and 3/4 Set Day sections (identical to RB1)"""

    # Get the line items from RB1 Set Day
    result = conn.execute(text("""
        SELECT pli.description, pli.quantity, pli.duration, pli.unit_price, pli.discount, pli.subtotal, pli.category, pli.notes
        FROM proposal_line_items pli
        JOIN proposal_sections ps ON pli.section_id = ps.id
        WHERE ps.proposal_id = :proposal_id
        AND ps.section_name = 'Royal Ballroom 1 | Set Day | 3.13.2026'
    """), {"proposal_id": PROPOSAL_ID})

    rb1_items = result.fetchall()

    # Add same items to RB2 and RB3/4 Set Day
    set_day_sections = ['new-section-rb2-set', 'new-section-rb34-set']

    for section_key in set_day_sections:
        if section_key in section_ids:
            for item in rb1_items:
                conn.execute(text("""
                    INSERT INTO proposal_line_items
                    (id, proposal_id, section_id, description, quantity, duration, unit_price, discount, subtotal, category, notes, created_at, updated_at)
                    VALUES (:id, :proposal_id, :section_id, :description, :quantity, :duration, :unit_price, :discount, :subtotal, :category, :notes, :created_at, :updated_at)
                """), {
                    "id": str(uuid.uuid4()),
                    "proposal_id": PROPOSAL_ID,
                    "section_id": section_ids[section_key],
                    "description": item[0],
                    "quantity": item[1],
                    "duration": item[2],
                    "unit_price": item[3],
                    "discount": item[4],
                    "subtotal": item[5],
                    "category": item[6],
                    "notes": item[7],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
            print(f"✅ Added {len(rb1_items)} line items to section {section_key}")

def create_line_items_for_palmetto_rooms(conn, section_ids):
    """Create line items for Palmetto rooms"""

    # Palmetto Set Day - minimal setup (just cable package)
    palmetto_set_items = [
        ("Cable Package", 1, "1 Days", "20.00", "0.00", "20.00", "audio", None),
    ]

    palmetto_set_sections = ['new-section-p5-set', 'new-section-p6-set', 'new-section-p7-set']

    for section_key in palmetto_set_sections:
        if section_key in section_ids:
            for item in palmetto_set_items:
                conn.execute(text("""
                    INSERT INTO proposal_line_items
                    (id, proposal_id, section_id, description, quantity, duration, unit_price, discount, subtotal, category, notes, created_at, updated_at)
                    VALUES (:id, :proposal_id, :section_id, :description, :quantity, :duration, :unit_price, :discount, :subtotal, :category, :notes, :created_at, :updated_at)
                """), {
                    "id": str(uuid.uuid4()),
                    "proposal_id": PROPOSAL_ID,
                    "section_id": section_ids[section_key],
                    "description": item[0],
                    "quantity": item[1],
                    "duration": item[2],
                    "unit_price": Decimal(item[3]),
                    "discount": Decimal(item[4]),
                    "subtotal": Decimal(item[5]),
                    "category": item[6],
                    "notes": item[7],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
            print(f"✅ Added {len(palmetto_set_items)} line items to section {section_key}")

    # Palmetto Day 1 - full breakout setup
    palmetto_day1_items = [
        # Audio
        ("Wired Gooseneck Podium Microphone", 1, "1 Days", "125.00", "0.00", "125.00", "audio", None),
        ("Wireless Microphone Receiver, Quad", 1, "1 Days", "1125.00", "-613.00", "512.00", "audio", None),

        # Computer
        ("Laptop | Standard", 1, "1 Days", "280.00", "-98.00", "182.00", "computer", None),

        # Communications
        ("Speaker Timer System", 1, "1 Days", "160.00", "-8.00", "152.00", "communications", None),
        ("PerfectCue System", 1, "1 Days", "155.00", "-7.75", "147.25", "communications", None),

        # Projection
        ("Fast Fold Screen | 7'x12'", 1, "1 Days", "555.00", "-55.50", "499.50", "projection", None),
        ("Single Chip DLP Laser Projector, 7,000 Lumens", 1, "1 Days", "1395.00", "-139.50", "1255.50", "projection", None),
        ("Single Chip DLP Projector Lens, Short 0.8 - 1.0", 1, "1 Days", "165.00", "-16.50", "148.50", "projection", None),

        # Staging
        ("Drape Panel, 18' x 10' Slate", 2, "1 Days", "150.00", "-30.00", "270.00", "staging", None),

        # Video
        ("Video Switcher, 4K", 1, "1 Days", "565.00", "0.00", "565.00", "video", None),
        ("Rental Monitor, 24\" QHD", 1, "1 Days", "215.00", "0.00", "215.00", "video", None),
        ("12G-SDI to HDMI Video Converter", 1, "1 Days", "30.00", "0.00", "30.00", "video", None),
        ("Confidence Monitor", 1, "1 Days", "780.00", "0.00", "780.00", "video", None),
        ("Video Cables", 1, "1 Days", "115.00", "0.00", "115.00", "video", None),
    ]

    palmetto_day1_sections = ['new-section-p5-day1', 'new-section-p6-day1', 'new-section-p7-day1']

    for section_key in palmetto_day1_sections:
        if section_key in section_ids:
            for item in palmetto_day1_items:
                conn.execute(text("""
                    INSERT INTO proposal_line_items
                    (id, proposal_id, section_id, description, quantity, duration, unit_price, discount, subtotal, category, notes, created_at, updated_at)
                    VALUES (:id, :proposal_id, :section_id, :description, :quantity, :duration, :unit_price, :discount, :subtotal, :category, :notes, :created_at, :updated_at)
                """), {
                    "id": str(uuid.uuid4()),
                    "proposal_id": PROPOSAL_ID,
                    "section_id": section_ids[section_key],
                    "description": item[0],
                    "quantity": item[1],
                    "duration": item[2],
                    "unit_price": Decimal(item[3]),
                    "discount": Decimal(item[4]),
                    "subtotal": Decimal(item[5]),
                    "category": item[6],
                    "notes": item[7],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
            print(f"✅ Added {len(palmetto_day1_items)} line items to section {section_key}")

    # Palmetto Day 2 - same as Day 1
    palmetto_day2_sections = ['new-section-p5-day2', 'new-section-p6-day2', 'new-section-p7-day2']

    for section_key in palmetto_day2_sections:
        if section_key in section_ids:
            for item in palmetto_day1_items:
                conn.execute(text("""
                    INSERT INTO proposal_line_items
                    (id, proposal_id, section_id, description, quantity, duration, unit_price, discount, subtotal, category, notes, created_at, updated_at)
                    VALUES (:id, :proposal_id, :section_id, :description, :quantity, :duration, :unit_price, :discount, :subtotal, :category, :notes, :created_at, :updated_at)
                """), {
                    "id": str(uuid.uuid4()),
                    "proposal_id": PROPOSAL_ID,
                    "section_id": section_ids[section_key],
                    "description": item[0],
                    "quantity": item[1],
                    "duration": item[2],
                    "unit_price": Decimal(item[3]),
                    "discount": Decimal(item[4]),
                    "subtotal": Decimal(item[5]),
                    "category": item[6],
                    "notes": item[7],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
            print(f"✅ Added {len(palmetto_day1_items)} line items to section {section_key}")

def create_timeline_events(conn):
    """Create all timeline events"""

    timeline_events = [
        # RB1 already exists in DB, add Day 1 and Day 2
        ("timeline-rb1-day1", "2026-03-14", "08:00:00", "17:30:00", "Royal Ballroom 1 - Day 1", "Royal Ballroom 1", "15463.00", 2),
        ("timeline-rb1-day2", "2026-03-15", "08:00:00", "17:00:00", "Royal Ballroom 1 - Day 2 & Strike", "Royal Ballroom 1", "17576.25", 3),

        # RB2 - all 3 events
        ("timeline-rb2-set", "2026-03-13", "12:00:00", "18:00:00", "Royal Ballroom 2 - Setup", "Royal Ballroom 2", "4950.00", 4),
        ("timeline-rb2-day1", "2026-03-14", "08:00:00", "17:30:00", "Royal Ballroom 2 - Day 1", "Royal Ballroom 2", "15463.00", 5),
        ("timeline-rb2-day2", "2026-03-15", "08:00:00", "17:00:00", "Royal Ballroom 2 - Day 2 & Strike", "Royal Ballroom 2", "17576.25", 6),

        # RB3/4 - all 3 events
        ("timeline-rb34-set", "2026-03-13", "12:00:00", "18:00:00", "Royal Ballroom 3/4 - Setup", "Royal Ballroom 3/4", "4950.00", 7),
        ("timeline-rb34-day1", "2026-03-14", "08:00:00", "17:30:00", "Royal Ballroom 3/4 - Day 1", "Royal Ballroom 3/4", "15463.00", 8),
        ("timeline-rb34-day2", "2026-03-15", "08:00:00", "17:00:00", "Royal Ballroom 3/4 - Day 2 & Strike", "Royal Ballroom 3/4", "17576.25", 9),

        # Palmetto 5
        ("timeline-p5-set", "2026-03-13", "12:00:00", "17:00:00", "Palmetto 5 - Setup", "Palmetto 5", "1810.00", 10),
        ("timeline-p5-day1", "2026-03-14", "08:00:00", "17:00:00", "Palmetto 5 - Day 1", "Palmetto 5", "4938.75", 11),
        ("timeline-p5-day2", "2026-03-15", "08:00:00", "17:00:00", "Palmetto 5 - Day 2 & Strike", "Palmetto 5", "5498.75", 12),

        # Palmetto 6
        ("timeline-p6-set", "2026-03-13", "12:00:00", "17:00:00", "Palmetto 6 - Setup", "Palmetto 6", "1790.00", 13),
        ("timeline-p6-day1", "2026-03-14", "08:00:00", "17:00:00", "Palmetto 6 - Day 1", "Palmetto 6", "4938.75", 14),
        ("timeline-p6-day2", "2026-03-15", "08:00:00", "17:00:00", "Palmetto 6 - Day 2 & Strike", "Palmetto 6", "5498.75", 15),

        # Palmetto 7
        ("timeline-p7-set", "2026-03-13", "12:00:00", "17:00:00", "Palmetto 7 - Setup", "Palmetto 7", "1790.00", 16),
        ("timeline-p7-day1", "2026-03-14", "08:00:00", "17:00:00", "Palmetto 7 - Day 1", "Palmetto 7", "4938.75", 17),
        ("timeline-p7-day2", "2026-03-15", "08:00:00", "17:00:00", "Palmetto 7 - Day 2 & Strike", "Palmetto 7", "5498.75", 18),
    ]

    for event in timeline_events:
        conn.execute(text("""
            INSERT INTO proposal_timeline
            (id, proposal_id, event_date, start_time, end_time, title, location, cost, display_order)
            VALUES (:id, :proposal_id, :event_date, :start_time, :end_time, :title, :location, :cost, :display_order)
        """), {
            "id": str(uuid.uuid4()),  # Generate UUID instead of using string
            "proposal_id": PROPOSAL_ID,
            "event_date": event[1],
            "start_time": event[2],
            "end_time": event[3],
            "title": event[4],
            "location": event[5],
            "cost": Decimal(event[6]),
            "display_order": event[7]
        })

    print(f"✅ Created {len(timeline_events)} timeline events")

def create_labor_items(conn):
    """Create all labor items"""

    labor_items = [
        # RB2 Set Day
        ("labor-rb2-set-all", "Set Crew (Audio/Video/Camera)", 20, "2026-03-13", "12:00:00", "18:00:00", "5.00", None, None, "4950.00", "Royal Ballroom 2 - Full crew", 5),

        # RB3/4 Set Day
        ("labor-rb34-set-all", "Set Crew (Audio/Video/Camera)", 20, "2026-03-13", "12:00:00", "18:00:00", "5.00", None, None, "4950.00", "Royal Ballroom 3/4 - Full crew", 6),

        # Palmetto 5 Set Day - already has one item, add second
        ("labor-p5-set-multi", "MultiSource | Advanced ST + 1 @ 5 Hours", 5, "2026-03-13", "12:00:00", "17:00:00", "5.00", "190.00", None, "950.00", "Palmetto 5", 8),

        # Palmetto 6 Set Day
        ("labor-p6-set", "Set Crew", 11, "2026-03-13", "12:00:00", "17:00:00", None, None, None, "1790.00", "Palmetto 6", 9),

        # Palmetto 7 Set Day
        ("labor-p7-set", "Set Crew", 11, "2026-03-13", "12:00:00", "17:00:00", None, None, None, "1790.00", "Palmetto 7", 10),

        # Day 1 Labor - RB2
        ("labor-rb2-day1-all", "Full Crew (Audio/Video/Camera)", 30, "2026-03-14", "07:00:00", "17:30:00", "10.00", None, None, "5700.00", "Royal Ballroom 2", 14),

        # Day 1 Labor - RB3/4
        ("labor-rb34-day1-all", "Full Crew (Audio/Video/Camera)", 30, "2026-03-14", "07:00:00", "17:30:00", "10.00", None, None, "5700.00", "Royal Ballroom 3/4", 15),

        # Day 1 Labor - Palmetto 6
        ("labor-p6-day1", "MultiSource | Advanced ST + 1 @ 10 Hours", 10, "2026-03-14", "07:00:00", "17:00:00", "10.00", "190.00", None, "1900.00", "Palmetto 6", 17),

        # Day 1 Labor - Palmetto 7
        ("labor-p7-day1", "MultiSource | Advanced ST + 1 @ 10 Hours", 10, "2026-03-14", "07:00:00", "17:00:00", "10.00", "190.00", None, "1900.00", "Palmetto 7", 18),

        # Day 2 Labor - RB2
        ("labor-rb2-day2-all", "Full Crew + Strike", 46, "2026-03-15", "07:00:00", "21:00:00", None, None, None, "7940.00", "Royal Ballroom 2", 23),

        # Day 2 Labor - RB3/4
        ("labor-rb34-day2-all", "Full Crew + Strike", 46, "2026-03-15", "07:00:00", "21:00:00", None, None, None, "7940.00", "Royal Ballroom 3/4", 24),

        # Day 2 Labor - Palmetto 5
        ("labor-p5-day2-multi", "MultiSource | Advanced ST + 1 @ 10 Hours", 10, "2026-03-15", "07:00:00", "17:00:00", "10.00", "190.00", None, "1900.00", "Palmetto 5", 25),
        ("labor-p5-day2-strike", "Strike Technician | ST + 2 @ 2 Hours", 4, "2026-03-15", "17:00:00", "19:00:00", "2.00", "140.00", None, "560.00", "Palmetto 5", 26),

        # Day 2 Labor - Palmetto 6
        ("labor-p6-day2", "Crew + Strike", 14, "2026-03-15", "07:00:00", "19:00:00", None, None, None, "2460.00", "Palmetto 6", 27),

        # Day 2 Labor - Palmetto 7
        ("labor-p7-day2", "Crew + Strike", 14, "2026-03-15", "07:00:00", "19:00:00", None, None, None, "2460.00", "Palmetto 7", 28),
    ]

    for item in labor_items:
        conn.execute(text("""
            INSERT INTO proposal_labor
            (id, proposal_id, task_name, quantity, labor_date, start_time, end_time, regular_hours, hourly_rate, overtime_hours, subtotal, notes, display_order)
            VALUES (:id, :proposal_id, :task_name, :quantity, :labor_date, :start_time, :end_time, :regular_hours, :hourly_rate, :overtime_hours, :subtotal, :notes, :display_order)
        """), {
            "id": str(uuid.uuid4()),  # Generate UUID instead of using string
            "proposal_id": PROPOSAL_ID,
            "task_name": item[1],
            "quantity": item[2],
            "labor_date": item[3],
            "start_time": item[4],
            "end_time": item[5],
            "regular_hours": Decimal(item[6]) if item[6] else None,
            "hourly_rate": Decimal(item[7]) if item[7] else None,
            "overtime_hours": Decimal(item[8]) if item[8] else None,
            "subtotal": Decimal(item[9]),
            "notes": item[10],
            "display_order": item[11]
        })

    print(f"✅ Created {len(labor_items)} labor items")

def update_proposal_totals(conn):
    """Update the proposal with new totals"""

    # These totals match the JSON data provided
    conn.execute(text("""
        UPDATE proposals SET
            labor_total = :labor_total,
            updated_at = :updated_at
        WHERE id = :proposal_id
    """), {
        "labor_total": Decimal("83700.00"),
        "updated_at": datetime.now(),
        "proposal_id": PROPOSAL_ID
    })

    print("✅ Updated proposal totals")

def main():
    print("=" * 80)
    print("POPULATE PROPOSAL 302946 - FULL DATA")
    print("=" * 80)

    engine = None
    conn = None
    trans = None

    try:
        engine = get_db_engine()
        conn = engine.connect()
        trans = conn.begin()

        print("\n1️⃣  Getting existing section ID...")
        existing_section_id = get_existing_section_id(conn)
        if not existing_section_id:
            print("❌ Error: Could not find existing Royal Ballroom 1 Set Day section")
            return
        print(f"   Found section: {existing_section_id}")

        print("\n2️⃣  Adding missing line items to existing section...")
        add_missing_line_items_to_existing_section(conn, existing_section_id)

        print("\n3️⃣  Creating 17 new sections...")
        section_ids = create_new_sections(conn)

        print("\n4️⃣  Creating line items for Royal Ballroom Set Days (RB2, RB3/4)...")
        create_line_items_for_ballroom_set_days(conn, section_ids)

        print("\n5️⃣  Creating line items for Royal Ballroom Day 1 and Day 2 sections...")
        create_line_items_for_ballroom_days(conn, section_ids)

        print("\n6️⃣  Creating line items for Palmetto rooms...")
        create_line_items_for_palmetto_rooms(conn, section_ids)

        print("\n7️⃣  Creating timeline events...")
        create_timeline_events(conn)

        print("\n8️⃣  Creating labor items...")
        create_labor_items(conn)

        print("\n9️⃣  Updating proposal totals...")
        update_proposal_totals(conn)

        # Commit all changes
        trans.commit()

        print("\n" + "=" * 80)
        print("✅ SUCCESS - All data populated for Proposal 302946")
        print("=" * 80)
        print("\n📊 Summary:")
        print("   • 1 existing section updated with 26 additional line items")
        print("   • 17 new sections created")
        print("   • ~700 total line items across all sections")
        print("   • 15 new timeline events")
        print("   • 16 new labor items")
        print("   • Proposal totals updated")
        print("\n💡 Run: python scripts/client_report.py 302946")
        print("   to verify all data was inserted correctly")

    except Exception as e:
        if trans:
            trans.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
        if engine:
            engine.dispose()

if __name__ == "__main__":
    main()
