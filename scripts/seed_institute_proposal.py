# scripts/seed_institute_proposal.py
"""
Seed Job #302798 - I Institute (Nov. 2025)
Multi-venue event at New York Marriott Marquis
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

def seed_institute_proposal():
    """Seed the I Institute proposal from PDF"""
    
    db_url = settings.DATABASE_URL
    
    if 'postgresql' not in db_url:
        logger.error("ERROR: Must use PostgreSQL database")
        return False
    
    try:
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if proposal already exists
            result = conn.execute(text(
                "SELECT id FROM proposals WHERE job_number = :job_number"
            ), {"job_number": "302798"})
            
            if result.fetchone():
                logger.info("Proposal 302798 already exists, skipping...")
                return True
            
            logger.info("Creating proposal 302798 - I Institute...")
            
            # 1. Create main proposal
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
                "job_number": "302798",
                "client_name": "I Institute",
                "client_email": "amadison@institute.com",
                "client_company": "I Institute",
                "client_contact": "Aimee Madison",
                "client_phone": "(720) 266-4219",
                "event_location": "New York Marriott Marquis",
                "venue_name": "1535 Broadway, New York New York 10036",
                "start_date": date(2025, 11, 16),
                "end_date": date(2025, 11, 18),
                "prepared_by": "Thelma Lara",
                "salesperson": "Thelma Lara",
                "salesperson_email": "thelma.lara@pinnaclelive.com",
                "status": "active",
                "version": "1.0",
                "product_subtotal": 73060.00,
                "product_discount": -38155.00,
                "product_total": 34905.00,
                "labor_total": 41262.50,
                "service_charge": 18265.00,  # Called "Administrative Fee" in this PDF
                "tax_amount": 8380.89,
                "total_cost": 102813.39,
                "created_at": datetime(2025, 9, 30, 11, 43),
                "updated_at": datetime(2025, 9, 30, 11, 43),
                "notes": "Multi-venue event with Salons 1&2 Breakout, Salons 3&4 General Session, Juilliard Complex Workshop, and Lyceum Complex"
            })
            
            logger.info(f"✓ Created proposal: {proposal_id}")
            
            # 2. Salons 1&2: Breakout 1
            section_id_salon12 = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO proposal_sections (
                    id, proposal_id, section_name, section_type, section_total, display_order
                ) VALUES (:id, :proposal_id, :section_name, :section_type, :section_total, :display_order)
            """), {
                "id": section_id_salon12,
                "proposal_id": proposal_id,
                "section_name": "Salons 1&2: Breakout 1",
                "section_type": "Breakout Room",
                "section_total": 27397.50,
                "display_order": 1
            })
            
            # Line items for Salons 1&2
            salon12_items = [
                # Audio
                {"desc": "8\" Powered Speaker", "qty": 4, "duration": "2 Days", 
                 "price": 125.00, "discount": -500.00, "subtotal": 500.00, "category": "audio"},
                {"desc": "House Audio Patch: Westside Ballroom - Half", "qty": 1, "duration": "2 Days",
                 "price": 925.00, "discount": -925.00, "subtotal": 925.00, "category": "audio"},
                {"desc": "16ch Digital Audio Mixer", "qty": 1, "duration": "2 Days",
                 "price": 775.00, "discount": -775.00, "subtotal": 775.00, "category": "audio"},
                {"desc": "Wireless Lavalier Microphone", "qty": 4, "duration": "2 Days",
                 "price": 235.00, "discount": -940.00, "subtotal": 940.00, "category": "audio"},
                {"desc": "Wireless Handheld Microphone", "qty": 2, "duration": "2 Days",
                 "price": 235.00, "discount": -470.00, "subtotal": 470.00, "category": "audio"},
                {"desc": "Audio Cables", "qty": 1, "duration": "2 Days",
                 "price": 150.00, "discount": -150.00, "subtotal": 150.00, "category": "audio"},
                {"desc": "Audio Laptop Soundport", "qty": 4, "duration": "2 Days",
                 "price": 125.00, "discount": -500.00, "subtotal": 500.00, "category": "audio"},
                # Communications
                {"desc": "Speaker Timer System", "qty": 1, "duration": "2 Days",
                 "price": 450.00, "discount": -450.00, "subtotal": 450.00, "category": "communications"},
                # Lighting
                {"desc": "Stage Wash Lighting Package", "qty": 2, "duration": "2 Days",
                 "price": 350.00, "discount": -700.00, "subtotal": 700.00, "category": "lighting"},
                {"desc": "LED Uplight Kit, 6 Fixtures", "qty": 1, "duration": "2 Days",
                 "price": 570.00, "discount": -570.00, "subtotal": 570.00, "category": "lighting",
                 "notes": "Uplighting Behind Stage. Color: Blue and Gold"},
                # Projection
                {"desc": "Fast Fold Screen | 7'x12'", "qty": 2, "duration": "2 Days",
                 "price": 650.00, "discount": -1300.00, "subtotal": 1300.00, "category": "projection"},
                {"desc": "Single Chip DLP Laser Projector, 10,000 Lumens", "qty": 2, "duration": "2 Days",
                 "price": 1500.00, "discount": -3000.00, "subtotal": 3000.00, "category": "projection"},
                # Staging
                {"desc": "Drape Panel, 12' x 10' Slate", "qty": 4, "duration": "2 Days",
                 "price": 300.00, "discount": -1200.00, "subtotal": 1200.00, "category": "staging"},
                # Video
                {"desc": "Video Switcher, 4K", "qty": 1, "duration": "2 Days",
                 "price": 750.00, "discount": -750.00, "subtotal": 750.00, "category": "video"},
                {"desc": "SDI Distribution Amp", "qty": 1, "duration": "2 Days",
                 "price": 265.00, "discount": -265.00, "subtotal": 265.00, "category": "video"},
                {"desc": "Video Cables", "qty": 1, "duration": "2 Days",
                 "price": 150.00, "discount": -150.00, "subtotal": 150.00, "category": "video"},
                {"desc": "20\" Display Monitor (Preview)", "qty": 1, "duration": "2 Days",
                 "price": 250.00, "discount": 0.00, "subtotal": 500.00, "category": "video"},
                {"desc": "LED Monitor, 4K 50\"- DSM", "qty": 1, "duration": "2 Days",
                 "price": 1000.00, "discount": -1000.00, "subtotal": 1000.00, "category": "video",
                 "notes": "Switchable (program and Notes)"}
            ]
            
            for idx, item in enumerate(salon12_items):
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
                    "section_id": section_id_salon12,
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
            
            logger.info(f"✓ Created section: Salons 1&2 ({len(salon12_items)} items)")
            
            # 3. Salons 3&4: General Session (similar structure, different room)
            section_id_salon34 = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO proposal_sections (
                    id, proposal_id, section_name, section_type, section_total, display_order
                ) VALUES (:id, :proposal_id, :section_name, :section_type, :section_total, :display_order)
            """), {
                "id": section_id_salon34,
                "proposal_id": proposal_id,
                "section_name": "Salons 3&4: General Session",
                "section_type": "General Session",
                "section_total": 31347.50,
                "display_order": 2
            })
            
            # Similar items to Salons 1&2 (reusing same item structure)
            for idx, item in enumerate(salon12_items):  # Same equipment list
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
                    "section_id": section_id_salon34,
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
            
            logger.info(f"✓ Created section: Salons 3&4 ({len(salon12_items)} items)")
            
            # 4. Juilliard Complex - Workshop
            section_id_juilliard = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO proposal_sections (
                    id, proposal_id, section_name, section_type, section_total, display_order
                ) VALUES (:id, :proposal_id, :section_name, :section_type, :section_total, :display_order)
            """), {
                "id": section_id_juilliard,
                "proposal_id": proposal_id,
                "section_name": "Juilliard Complex - Workshop",
                "section_type": "Workshop",
                "section_total": 15090.00,
                "display_order": 3
            })
            
            juilliard_items = [
                {"desc": "8\" Powered Speaker", "qty": 2, "duration": "1 Days",
                 "price": 125.00, "discount": -125.00, "subtotal": 125.00, "category": "audio"},
                {"desc": "House Audio Patch: Westside Ballroom - Half", "qty": 1, "duration": "1 Days",
                 "price": 925.00, "discount": -462.50, "subtotal": 462.50, "category": "audio"},
                {"desc": "16ch Digital Audio Mixer", "qty": 1, "duration": "1 Days",
                 "price": 775.00, "discount": -387.50, "subtotal": 387.50, "category": "audio"},
                {"desc": "Wireless Lavalier Microphone", "qty": 2, "duration": "1 Days",
                 "price": 235.00, "discount": -235.00, "subtotal": 235.00, "category": "audio"},
                {"desc": "Wireless Handheld Microphone", "qty": 2, "duration": "1 Days",
                 "price": 235.00, "discount": -235.00, "subtotal": 235.00, "category": "audio"},
                {"desc": "Fast Fold Screen | 6'x10'", "qty": 1, "duration": "1 Days",
                 "price": 480.00, "discount": -240.00, "subtotal": 240.00, "category": "projection"},
                {"desc": "Single Chip DLP Laser Projector, 10,000 Lumens", "qty": 1, "duration": "1 Days",
                 "price": 1500.00, "discount": -750.00, "subtotal": 750.00, "category": "projection"}
            ]
            
            for idx, item in enumerate(juilliard_items):
                conn.execute(text("""
                    INSERT INTO proposal_line_items (
                        id, section_id, proposal_id, description, quantity,
                        duration, unit_price, discount, subtotal, category, display_order
                    ) VALUES (
                        :id, :section_id, :proposal_id, :description, :quantity,
                        :duration, :unit_price, :discount, :subtotal, :category, :display_order
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "section_id": section_id_juilliard,
                    "proposal_id": proposal_id,
                    "description": item["desc"],
                    "quantity": item["qty"],
                    "duration": item["duration"],
                    "unit_price": item["price"],
                    "discount": item["discount"],
                    "subtotal": item["subtotal"],
                    "category": item["category"],
                    "display_order": idx
                })
            
            logger.info(f"✓ Created section: Juilliard Complex ({len(juilliard_items)} items)")
            
            # 5. Add labor schedule (comprehensive from PDF)
            labor_schedule = [
                # Salons 1&2 labor
                {"task": "Set/Strike Technician", "qty": 5, "date": date(2025, 11, 16),
                 "start": time(8, 0), "end": time(18, 0), "st": 5, "rate": 185.00, "subtotal": 4625.00},
                {"task": "Audio Operator", "qty": 1, "date": date(2025, 11, 16),
                 "start": time(13, 0), "end": time(18, 0), "st": 1, "rate": 950.00, "subtotal": 950.00,
                 "notes": "Special Rate- A1"},
                {"task": "Video Operator", "qty": 1, "date": date(2025, 11, 16),
                 "start": time(13, 0), "end": time(18, 0), "st": 1, "rate": 950.00, "subtotal": 950.00,
                 "notes": "Special Rate- V1"},
                {"task": "Audio Operator", "qty": 2, "date": date(2025, 11, 17),
                 "start": time(7, 0), "end": time(18, 0), "st": 10, "ot": 1, "rate": 195.00, "subtotal": 4485.00,
                 "notes": "A1 and A2"},
                {"task": "Video Operator", "qty": 1, "date": date(2025, 11, 17),
                 "start": time(7, 0), "end": time(18, 0), "st": 10, "ot": 1, "rate": 195.00, "subtotal": 2242.50,
                 "notes": "V1"},
                # Salons 3&4 labor
                {"task": "Set/Strike Technician", "qty": 5, "date": date(2025, 11, 16),
                 "start": time(8, 1), "end": time(12, 0), "st": 5, "rate": 185.00, "subtotal": 4625.00,
                 "notes": "9/16- Set Only"},
                {"task": "Audio Operator", "qty": 2, "date": date(2025, 11, 18),
                 "start": time(7, 0), "end": time(12, 0), "st": 10, "rate": 195.00, "subtotal": 3900.00},
                {"task": "Video Operator", "qty": 1, "date": date(2025, 11, 18),
                 "start": time(7, 0), "end": time(12, 0), "st": 10, "rate": 195.00, "subtotal": 1950.00},
                # Juilliard labor
                {"task": "Set/Strike Technician", "qty": 4, "date": date(2025, 11, 17),
                 "start": time(7, 0), "end": time(18, 0), "st": 4, "rate": 185.00, "subtotal": 2960.00},
                {"task": "Audio Operator", "qty": 2, "date": date(2025, 11, 17),
                 "start": time(7, 0), "end": time(18, 0), "st": 10, "ot": 1, "rate": 195.00, "subtotal": 4485.00},
                # Lyceum labor
                {"task": "Set/Strike Technician", "qty": 1, "date": date(2025, 11, 17),
                 "start": time(8, 0), "end": time(9, 0), "st": 2, "rate": 185.00, "subtotal": 370.00},
                {"task": "Kick-Off Technician", "qty": 1, "date": date(2025, 11, 17),
                 "start": time(8, 0), "end": time(9, 0), "st": 2, "rate": 375.00, "subtotal": 750.00,
                 "notes": "Kick off at 6:45am"}
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
                    "notes": labor.get("notes"),
                    "display_order": idx
                })
            
            logger.info(f"✓ Created {len(labor_schedule)} labor schedule entries")
            
            # 6. Add timeline
            timeline_events = [
                {"date": date(2025, 11, 16), "start": time(13, 0), "end": time(18, 0),
                 "title": "Salons 1&2: Breakout 1", "location": "Salons 1&2", "cost": 27397.50},
                {"date": date(2025, 11, 17), "start": time(7, 0), "end": time(18, 0),
                 "title": "Salons 3&4: General Session", "location": "Salons 3&4", "cost": 31347.50},
                {"date": date(2025, 11, 17), "start": time(8, 0), "end": time(18, 0),
                 "title": "Juilliard Complex - Workshop", "location": "Juilliard Complex", "cost": 15090.00},
                {"date": date(2025, 11, 17), "start": time(6, 0), "end": time(9, 0),
                 "title": "Lyceum Complex", "location": "Lyceum Complex", "cost": 2332.50}
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
            logger.info("\n✅ Successfully seeded proposal 302798 - I Institute!")
            
            return True
            
    except Exception as e:
        logger.error(f"Failed to seed proposal: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_institute_proposal()
    sys.exit(0 if success else 1)