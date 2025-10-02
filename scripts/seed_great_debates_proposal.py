# scripts/seed_great_debates_proposal.py
"""
Seed Job #302946 - 3.26 Great Debates in Solid Tumors
Multi-room medical conference at JW Marriott Miami Turnberry Resort & Spa
March 13-15, 2026
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from datetime import datetime, date, time
import logging
import uuid

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_great_debates_proposal():
    """Seed the Great Debates in Solid Tumors medical conference proposal"""
    
    db_url = settings.DATABASE_URL
    
    if 'postgresql' not in db_url:
        logger.error("ERROR: Must use PostgreSQL database")
        return False
    
    try:
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            job_number = "302946"
            
            # Check if proposal already exists
            result = conn.execute(text(
                "SELECT id FROM proposals WHERE job_number = :job_number"
            ), {"job_number": job_number})
            
            if result.fetchone():
                logger.info(f"Proposal {job_number} already exists, skipping...")
                return True
            
            logger.info(f"Creating proposal {job_number}...")
            
            # 1. CREATE MAIN PROPOSAL
            proposal_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO proposals (
                    id, job_number, client_name, client_email, client_company,
                    client_contact, client_phone,
                    event_location, venue_name, start_date, end_date,
                    prepared_by, salesperson, salesperson_email,
                    status, version,
                    product_subtotal, product_discount, product_total,
                    labor_total, service_charge, tax_amount, total_cost,
                    created_at, updated_at, notes
                ) VALUES (
                    :id, :job_number, :client_name, :client_email, :client_company,
                    :client_contact, :client_phone,
                    :event_location, :venue_name, :start_date, :end_date,
                    :prepared_by, :salesperson, :salesperson_email,
                    :status, :version,
                    :product_subtotal, :product_discount, :product_total,
                    :labor_total, :service_charge, :tax_amount, :total_cost,
                    :created_at, :updated_at, :notes
                )
            """), {
                "id": proposal_id,
                "job_number": job_number,
                "client_name": "3.26 Great Debates in Solid Tumors",
                "client_email": "bnatale@company.com",
                "client_company": "HMP Education",
                "client_contact": "Briana Natale",
                "client_phone": "(609) 630-6116",
                "event_location": "JW Marriott Miami Turnberry Resort & Spa",
                "venue_name": "19999 West Country Club Drive, Aventura Florida 33180",
                "start_date": date(2026, 3, 13),
                "end_date": date(2026, 3, 15),
                "prepared_by": "Levi Sacks",
                "salesperson": "Levi Sacks",
                "salesperson_email": "levi.sacks@pinnaclelive.com",
                "status": "tentative",
                "version": "1.0",
                "product_subtotal": 249165.00,
                "product_discount": -98494.75,
                "product_total": 150670.25,
                "labor_total": 150670.25,  # Labor is included in product total
                "service_charge": 45485.70,
                "tax_amount": 13730.92,
                "total_cost": 209886.87,
                "created_at": datetime(2025, 9, 30, 11, 44),
                "updated_at": datetime(2025, 9, 30, 11, 44),
                "notes": "Multi-room medical conference with Royal Ballrooms 1, 2, 3/4 and Palmetto rooms 5, 6, 7. Preferred in-house client pricing with HMP Education Medical Slide Review coordination."
            })
            
            logger.info(f"✓ Created proposal: {proposal_id}")
            
            # 2. CREATE ROYAL BALLROOM 1 SECTION (Day 1 - Set Day)
            section_id_rb1 = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO proposal_sections (
                    id, proposal_id, section_name, section_type, section_total, display_order
                ) VALUES (:id, :proposal_id, :section_name, :section_type, :section_total, :display_order)
            """), {
                "id": section_id_rb1,
                "proposal_id": proposal_id,
                "section_name": "Royal Ballroom 1 | Set Day | 3.13.2026",
                "section_type": "General Session",
                "section_total": 4950.00,
                "display_order": 1
            })
            
            # Royal Ballroom 1 items (100% discounted equipment, only labor charged)
            rb1_items = [
                # Audio Equipment (all $0 after discount)
                {"desc": "16ch Digital Audio Mixer", "qty": 1, "duration": "1 Days", "price": 315.00, "discount": -315.00, "subtotal": 0.00, "category": "audio"},
                {"desc": "Digital Audio Snake Stage Box", "qty": 1, "duration": "1 Days", "price": 175.00, "discount": -175.00, "subtotal": 0.00, "category": "audio"},
                {"desc": "Wired Gooseneck Podium Microphone", "qty": 1, "duration": "1 Days", "price": 125.00, "discount": -125.00, "subtotal": 0.00, "category": "audio"},
                {"desc": "Wireless Microphone Receiver, Quad - (8) HH mics (6) with table stands for panel & (2) on stands in aisle for Q&A", "qty": 2, "duration": "1 Days", "price": 1125.00, "discount": -2250.00, "subtotal": 0.00, "category": "audio"},
                {"desc": "12\" Powered Speaker - On speaker stands flanking the screen and riser", "qty": 2, "duration": "1 Days", "price": 190.00, "discount": -380.00, "subtotal": 0.00, "category": "audio"},
                {"desc": "8\" Powered Speaker - Placed on riser acting as center fill", "qty": 2, "duration": "1 Days", "price": 160.00, "discount": -320.00, "subtotal": 0.00, "category": "audio"},
                {"desc": "Pinnacle Live Music - Music upbeat as walk in/walk out and during breaks", "qty": 1, "duration": "1 Days", "price": 195.00, "discount": -195.00, "subtotal": 0.00, "category": "audio"},
                # Video Equipment
                {"desc": "PTZ Camera", "qty": 1, "duration": "1 Days", "price": 770.00, "discount": -770.00, "subtotal": 0.00, "category": "video"},
                {"desc": "Video Switcher, 4K", "qty": 1, "duration": "1 Days", "price": 565.00, "discount": -565.00, "subtotal": 0.00, "category": "video"},
                {"desc": "Confidence Monitor", "qty": 1, "duration": "1 Days", "price": 780.00, "discount": -780.00, "subtotal": 0.00, "category": "video"},
                # Projection
                {"desc": "Fast Fold Screen | 9'x16' - Set to either the left or right of the riser", "qty": 1, "duration": "1 Days", "price": 655.00, "discount": -655.00, "subtotal": 0.00, "category": "projection"},
                {"desc": "Single Chip DLP Laser Projector, 12,000 Lumens", "qty": 1, "duration": "1 Days", "price": 2195.00, "discount": -2195.00, "subtotal": 0.00, "category": "projection"},
                # Lighting
                {"desc": "LED Uplight Kit, 6 Fixtures - On drape | color TBD", "qty": 1, "duration": "1 Days", "price": 615.00, "discount": -615.00, "subtotal": 0.00, "category": "lighting"},
                {"desc": "LED Ellipsoidal Lighting Fixture", "qty": 4, "duration": "1 Days", "price": 160.00, "discount": -640.00, "subtotal": 0.00, "category": "lighting"},
            ]
            
            for idx, item in enumerate(rb1_items):
                conn.execute(text("""
                    INSERT INTO proposal_line_items (
                        id, section_id, proposal_id, description, quantity,
                        duration, unit_price, discount, subtotal, category,
                        notes, display_order
                    ) VALUES (
                        :id, :section_id, :proposal_id, :description, :quantity,
                        :duration, :unit_price, :discount, :subtotal, :category,
                        :notes, :display_order
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "section_id": section_id_rb1,
                    "proposal_id": proposal_id,
                    "description": item["desc"],
                    "quantity": item["qty"],
                    "duration": item["duration"],
                    "unit_price": item["price"],
                    "discount": item["discount"],
                    "subtotal": item["subtotal"],
                    "category": item["category"],
                    "notes": item.get("notes"),
                    "display_order": idx
                })
            
            logger.info(f"✓ Created section: Royal Ballroom 1 Set Day ({len(rb1_items)} equipment items)")
            
            # 3. ADD COMPREHENSIVE LABOR SCHEDULE
            labor_schedule = [
                # Royal Ballroom 1 - Set Day 3/13
                {"task": "Set Technician | ST + 3 @ 5 Hours", "qty": 15, "date": date(2026, 3, 13), 
                 "start": time(12, 0), "end": time(18, 0), "st": 5, "rate": 140.00, "subtotal": 2100.00, "room": "Royal Ballroom 1"},
                {"task": "Audio Technician | Advanced ST + 1 @ 5 Hours", "qty": 5, "date": date(2026, 3, 13),
                 "start": time(12, 0), "end": time(18, 0), "st": 5, "rate": 190.00, "subtotal": 950.00, "room": "Royal Ballroom 1"},
                {"task": "Video Technician | Advanced ST + 1 @ 5 Hours", "qty": 5, "date": date(2026, 3, 13),
                 "start": time(12, 0), "end": time(18, 0), "st": 5, "rate": 190.00, "subtotal": 950.00, "room": "Royal Ballroom 1"},
                {"task": "Camera Operator | Advanced ST + 1 @ 5 Hours", "qty": 5, "date": date(2026, 3, 13),
                 "start": time(12, 0), "end": time(18, 0), "st": 5, "rate": 190.00, "subtotal": 950.00, "room": "Royal Ballroom 1"},
                
                # Royal Ballroom 1 - Days 1&2 (3/14-3/15)
                {"task": "Audio Technician | Advanced ST + 1 @ 10 Hours", "qty": 10, "date": date(2026, 3, 14),
                 "start": time(7, 0), "end": time(17, 30), "st": 10, "rate": 190.00, "subtotal": 1900.00, "room": "Royal Ballroom 1"},
                {"task": "Video Technician | Advanced ST + 1 @ 10 Hours", "qty": 10, "date": date(2026, 3, 14),
                 "start": time(7, 0), "end": time(17, 30), "st": 10, "rate": 190.00, "subtotal": 1900.00, "room": "Royal Ballroom 1"},
                {"task": "Camera Operator | Advanced ST + 1 @ 10 Hours", "qty": 10, "date": date(2026, 3, 14),
                 "start": time(7, 0), "end": time(17, 30), "st": 10, "rate": 190.00, "subtotal": 1900.00, "room": "Royal Ballroom 1"},
                
                # Royal Ballroom 1 - Day 2/2 (3/15) with strike
                {"task": "Strike Technician | ST + 4 @ 4 Hours", "qty": 16, "date": date(2026, 3, 15),
                 "start": time(17, 0), "end": time(21, 0), "st": 4, "rate": 140.00, "subtotal": 2240.00, "room": "Royal Ballroom 1"},
                
                # Palmetto 5 - MultiSource operators
                {"task": "MultiSource | Advanced ST + 1 @ 5 Hours", "qty": 5, "date": date(2026, 3, 13),
                 "start": time(12, 0), "end": time(17, 0), "st": 5, "rate": 190.00, "subtotal": 950.00, "room": "Palmetto 5"},
                {"task": "MultiSource | Advanced ST + 1 @ 10 Hours", "qty": 10, "date": date(2026, 3, 14),
                 "start": time(7, 0), "end": time(17, 0), "st": 10, "rate": 190.00, "subtotal": 1900.00, "room": "Palmetto 5"},
                {"task": "Strike Technician | ST + 2 @ 2 Hours", "qty": 4, "date": date(2026, 3, 15),
                 "start": time(17, 0), "end": time(19, 0), "st": 2, "rate": 140.00, "subtotal": 560.00, "room": "Palmetto 5"},
            ]
            
            for idx, labor in enumerate(labor_schedule):
                conn.execute(text("""
                    INSERT INTO proposal_labor (
                        id, proposal_id, task_name, quantity, labor_date,
                        start_time, end_time, regular_hours, overtime_hours,
                        hourly_rate, subtotal, notes, display_order
                    ) VALUES (
                        :id, :proposal_id, :task_name, :quantity, :labor_date,
                        :start_time, :end_time, :regular_hours, :overtime_hours,
                        :hourly_rate, :subtotal, :notes, :display_order
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "proposal_id": proposal_id,
                    "task_name": labor["task"],
                    "quantity": labor["qty"],
                    "labor_date": labor["date"],
                    "start_time": labor["start"],
                    "end_time": labor["end"],
                    "regular_hours": labor["st"],
                    "overtime_hours": labor.get("ot", 0),
                    "hourly_rate": labor["rate"],
                    "subtotal": labor["subtotal"],
                    "notes": labor.get("room"),
                    "display_order": idx
                })
            
            logger.info(f"✓ Created {len(labor_schedule)} labor schedule entries")
            
            # 4. ADD TIMELINE EVENTS
            timeline_events = [
                {"date": date(2026, 3, 13), "start": time(12, 0), "end": time(18, 0),
                 "title": "Setup Day - Royal Ballrooms & Palmetto Rooms", 
                 "location": "Multiple Venues", "cost": 4950.00},
                {"date": date(2026, 3, 14), "start": time(8, 0), "end": time(17, 30),
                 "title": "Day 1 - General Sessions & Breakouts", 
                 "location": "Royal Ballrooms 1, 2, 3/4 | Palmetto 5, 6, 7", "cost": 61802.50},
                {"date": date(2026, 3, 15), "start": time(8, 0), "end": time(17, 0),
                 "title": "Day 2 - Final Sessions & Strike", 
                 "location": "All Venues", "cost": 70075.00},
            ]
            
            for idx, event in enumerate(timeline_events):
                conn.execute(text("""
                    INSERT INTO proposal_timeline (
                        id, proposal_id, event_date, start_time, end_time,
                        title, location, cost, display_order
                    ) VALUES (
                        :id, :proposal_id, :event_date, :start_time, :end_time,
                        :title, :location, :cost, :display_order
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "proposal_id": proposal_id,
                    "event_date": event["date"],
                    "start_time": event["start"],
                    "end_time": event["end"],
                    "title": event["title"],
                    "location": event["location"],
                    "cost": event["cost"],
                    "display_order": idx
                })
            
            logger.info(f"✓ Created {len(timeline_events)} timeline events")
            
            conn.commit()
            logger.info("\n✅ Successfully seeded proposal 302946 - Great Debates in Solid Tumors!")
            logger.info(f"Total Cost: $209,886.87")
            logger.info(f"Product Total: $150,670.25 (after $98,494.75 discount)")
            logger.info(f"Service Charge: $45,485.70")
            logger.info(f"Tax: $13,730.92")
            
            return True
            
    except Exception as e:
        logger.error(f"Failed to seed proposal: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_great_debates_proposal()
    sys.exit(0 if success else 1)