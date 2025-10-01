# scripts/seed_proposals_from_pdf.py
"""
Seed database with actual proposal data from Pinnacle Live SOW PDF
This creates a realistic proposal that matches the PDF structure
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from datetime import datetime, date, time
import logging
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_pinnacle_proposal():
    """Seed the User Conference proposal from the PDF"""
    
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
            ), {"job_number": "305342"})
            
            if result.fetchone():
                logger.info("Proposal 305342 already exists, skipping...")
                return True
            
            logger.info("Creating proposal 305342...")
            
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
                    created_at, updated_at
                ) VALUES (
                    :id, :job_number, :client_name, :client_email, :client_company,
                    :client_contact, :client_phone,
                    :event_location, :venue_name, :start_date, :end_date,
                    :prepared_by, :salesperson, :salesperson_email,
                    :status, :version,
                    :product_subtotal, :product_discount, :product_total,
                    :labor_total, :service_charge, :tax_amount, :total_cost,
                    :created_at, :updated_at
                )
            """), {
                "id": proposal_id,
                "job_number": "305342",
                "client_name": "User Conference option 2",
                "client_email": "shanondoah.nicholson@company.com",
                "client_company": None,
                "client_contact": "Shanandoah Nicholson",
                "client_phone": "+1 416 816 0104",
                "event_location": "Hyatt Regency Jersey City",
                "venue_name": "2 Exchange Place, Jersey City New Jersey 07302",
                "start_date": date(2025, 9, 30),
                "end_date": date(2025, 9, 30),
                "prepared_by": "Emily Feazel",
                "salesperson": "Emily Feazel",
                "salesperson_email": "emily.feazel@pinnaclelive.com",
                "status": "tentative",
                "version": "1.0",
                "product_subtotal": 26560.00,
                "product_discount": -3324.00,
                "product_total": 23236.00,
                "labor_total": 17960.00,
                "service_charge": 11434.80,
                "tax_amount": 2296.95,
                "total_cost": 54927.75,
                "created_at": datetime(2025, 9, 30, 11, 42),
                "updated_at": datetime(2025, 9, 30, 11, 42)
            })
            
            logger.info(f"✓ Created proposal: {proposal_id}")
            
            # 2. Create sections and line items
            sections_data = [
                {
                    "name": "Office | Boardroom",
                    "type": "Video",
                    "items": [
                        {"desc": "LED Monitor, 4K 65\"", "qty": 1, "duration": "1 Days", 
                         "price": 890.00, "discount": -133.50, "subtotal": 756.50, "category": "video"}
                    ]
                },
                {
                    "name": "General Session | Hudson Ballroom IV,V, VI",
                    "type": "Audio",
                    "items": [
                        {"desc": "16ch Digital Audio Mixer", "qty": 1, "duration": "1 Days",
                         "price": 300.00, "discount": -45.00, "subtotal": 255.00, "category": "audio",
                         "notes": "Line out to client's videographer who will record the meeting."},
                        {"desc": "12\" Powered Speaker", "qty": 2, "duration": "1 Days",
                         "price": 145.00, "discount": -43.50, "subtotal": 246.50, "category": "audio"},
                        {"desc": "8\" Powered Speaker", "qty": 2, "duration": "1 Days",
                         "price": 155.00, "discount": -46.50, "subtotal": 263.50, "category": "audio"},
                        {"desc": "Wireless Lavalier Microphone Capsule", "qty": 8, "duration": "1 Days",
                         "price": 270.00, "discount": -324.00, "subtotal": 1836.00, "category": "audio"},
                        {"desc": "H50 Wireless Microphone Handheld", "qty": 1, "duration": "1 Days",
                         "price": 270.00, "discount": -40.50, "subtotal": 229.50, "category": "audio",
                         "notes": "Please place on mic stand at podium."},
                        {"desc": "Microphone Table Stand, Black", "qty": 1, "duration": "1 Days",
                         "price": 15.00, "discount": -2.25, "subtotal": 12.75, "category": "audio"},
                        {"desc": "Mono Audio Direct Box SW318", "qty": 1, "duration": "1 Days",
                         "price": 60.00, "discount": -9.00, "subtotal": 51.00, "category": "audio"}
                    ]
                },
                {
                    "name": "General Session | Hudson Ballroom IV,V, VI",
                    "type": "Computer",
                    "items": [
                        {"desc": "Laptop | Standard", "qty": 1, "duration": "1 Days",
                         "price": 270.00, "discount": -40.50, "subtotal": 229.50, "category": "computer"}
                    ]
                },
                {
                    "name": "General Session | Hudson Ballroom IV,V, VI",
                    "type": "Lighting",
                    "items": [
                        {"desc": "LED Uplight", "qty": 12, "duration": "1 Days",
                         "price": 105.00, "discount": -189.00, "subtotal": 1071.00, "category": "lighting"}
                    ]
                },
                {
                    "name": "General Session | Hudson Ballroom IV,V, VI",
                    "type": "Projection",
                    "items": [
                        {"desc": "Fast Fold Screen and Projector Package | 6'9\" x 12'", "qty": 2, 
                         "duration": "1 Days", "price": 2100.00, "discount": -630.00, 
                         "subtotal": 3570.00, "category": "projection", "notes": "12k projector"}
                    ]
                }
            ]
            
            for section_data in sections_data:
                section_id = str(uuid.uuid4())
                section_total = sum(item["subtotal"] for item in section_data["items"])
                
                conn.execute(text("""
                    INSERT INTO proposal_sections (
                        id, proposal_id, section_name, section_type, section_total
                    ) VALUES (:id, :proposal_id, :section_name, :section_type, :section_total)
                """), {
                    "id": section_id,
                    "proposal_id": proposal_id,
                    "section_name": section_data["name"],
                    "section_type": section_data["type"],
                    "section_total": section_total
                })
                
                # Add line items
                for idx, item in enumerate(section_data["items"]):
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
                        "section_id": section_id,
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
                
                logger.info(f"✓ Created section: {section_data['name']} ({len(section_data['items'])} items)")
            
            # 3. Add labor schedule
            labor_schedule = [
                {"task": "Set Technician", "qty": 6, "date": date(2025, 9, 29),
                 "start": time(5, 0), "end": time(12, 0), "st": 7, "rate": 140.00, "subtotal": 5880.00,
                 "notes": "Room to be set for rehearsal only. Set may be completed after rehearsal."},
                {"task": "Strike Technician", "qty": 4, "date": date(2025, 9, 30),
                 "start": time(16, 0), "end": time(21, 0), "st": 6, "rate": 140.00, "subtotal": 3360.00},
                {"task": "Video Operator", "qty": 1, "date": date(2025, 9, 30),
                 "start": time(7, 30), "end": time(15, 30), "st": 8, "rate": 180.00, "subtotal": 1440.00,
                 "notes": "General Session"},
                {"task": "Audio Operator", "qty": 1, "date": date(2025, 9, 30),
                 "start": time(7, 30), "end": time(15, 30), "st": 8, "rate": 180.00, "subtotal": 1440.00,
                 "notes": "General Session"},
                {"task": "Set Technician", "qty": 2, "date": date(2025, 9, 29),
                 "start": time(9, 0), "end": time(13, 0), "st": 4, "rate": 140.00, "subtotal": 1120.00,
                 "notes": "Scenic Design Set"},
                {"task": "Strike Technician", "qty": 2, "date": date(2025, 9, 30),
                 "start": time(17, 0), "end": time(21, 0), "st": 4, "rate": 140.00, "subtotal": 1120.00,
                 "notes": "Scenic Design Strike"},
                {"task": "Video Operator", "qty": 1, "date": date(2025, 9, 29),
                 "start": time(12, 0), "end": time(18, 0), "st": 6, "rate": 180.00, "subtotal": 1080.00,
                 "notes": "Rehearsal"},
                {"task": "Audio Operator", "qty": 1, "date": date(2025, 9, 29),
                 "start": time(12, 0), "end": time(18, 0), "st": 6, "rate": 180.00, "subtotal": 1080.00,
                 "notes": "Rehearsal"},
                {"task": "Support Technician", "qty": 2, "date": date(2025, 9, 30),
                 "start": time(10, 0), "end": time(14, 0), "st": 4, "rate": 180.00, "subtotal": 1440.00,
                 "notes": "Floating techs for breakouts."}
            ]
            
            for idx, labor in enumerate(labor_schedule):
                conn.execute(text("""
                    INSERT INTO proposal_labor (
                        id, proposal_id, task_name, quantity, labor_date,
                        start_time, end_time, regular_hours, hourly_rate, subtotal,
                        notes, display_order
                    ) VALUES (
                        :id, :proposal_id, :task_name, :quantity, :labor_date,
                        :start_time, :end_time, :regular_hours, :hourly_rate, :subtotal,
                        :notes, :display_order
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
                    "hourly_rate": labor["rate"],
                    "subtotal": labor["subtotal"],
                    "notes": labor.get("notes"),
                    "display_order": idx
                })
            
            logger.info(f"✓ Created {len(labor_schedule)} labor schedule entries")
            
            # 4. Add timeline events
            timeline_events = [
                {"date": date(2025, 9, 29), "start": time(8, 0), "end": time(23, 59),
                 "title": "Rehearsal Setup", "location": "Office | Boardroom", "cost": 756.50},
                {"date": date(2025, 9, 30), "start": time(8, 0), "end": time(0, 0),
                 "title": "Main Event", "location": "General Session | Hudson Ballroom IV,V, VI", 
                 "cost": 13452.50}
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
            logger.info("\n✅ Successfully seeded proposal 305342!")
            
            return True
            
    except Exception as e:
        logger.error(f"Failed to seed proposal: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_pinnacle_proposal()
    sys.exit(0 if success else 1)