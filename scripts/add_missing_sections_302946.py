#!/usr/bin/env python3
"""
Add Missing Sections and Line Items for Job #302946
----------------------------------------------------
This script adds missing sections, line items, timeline events, and labor
data to proposal 302946 to fix the data discrepancy.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import uuid as uuid_lib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings


# ============================================================================
# PASTE YOUR DATA HERE
# ============================================================================
# Replace this with your complete proposal data structure
# Format should be identical to the JSON structure you have

MISSING_SECTIONS_DATA = [
    # Example structure (REPLACE WITH YOUR ACTUAL DATA):
    # {
    #     "section_name": "Royal Ballroom 1 - Set Day",
    #     "section_type": "Audio",
    #     "display_order": 1,
    #     "section_total": "2156.25",
    #     "is_expanded": True,
    #     "notes": "",
    #     "items": [
    #         {
    #             "item_number": "1",
    #             "description": "16ch Digital Audio Mixer",
    #             "quantity": 1,
    #             "duration": "1 Days",
    #             "unit_price": "255.00",
    #             "discount": "0.00",
    #             "subtotal": "255.00",
    #             "category": "audio",
    #             "item_type": "equipment",
    #             "notes": ""
    #         },
    #         # ... more items
    #     ]
    # },
    # ... more sections
]

# Timeline events data
TIMELINE_DATA = [
    # Example structure (REPLACE WITH YOUR ACTUAL DATA):
    # {
    #     "event_date": "2024-03-15",
    #     "start_time": "08:00:00",
    #     "end_time": "17:00:00",
    #     "title": "Setup Day",
    #     "location": "Royal Ballroom 1",
    #     "cost": "0.00",
    #     "display_order": 1
    # },
    # ... more timeline events
]

# Labor data
LABOR_DATA = [
    # Example structure (REPLACE WITH YOUR ACTUAL DATA):
    # {
    #     "task_name": "Audio Technician",
    #     "quantity": 2,
    #     "labor_date": "2024-03-15",
    #     "start_time": "08:00:00",
    #     "end_time": "17:00:00",
    #     "regular_hours": "8.00",
    #     "overtime_hours": "0.00",
    #     "double_time_hours": "0.00",
    #     "hourly_rate": "45.00",
    #     "subtotal": "720.00",
    #     "notes": "",
    #     "display_order": 1
    # },
    # ... more labor items
]


def add_missing_data(engine, job_number, dry_run=True):
    """Add missing sections, line items, timeline, and labor to a proposal."""

    print("=" * 120)
    print("ADD MISSING DATA FOR JOB #302946")
    print("=" * 120)
    print()

    # Get proposal ID
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, job_number, client_name FROM proposals WHERE job_number = :job_number"),
            {"job_number": job_number}
        )
        proposal = result.fetchone()

        if not proposal:
            print(f"❌ Proposal {job_number} not found!")
            return

        proposal_id = str(proposal[0])
        print(f"✅ Found proposal: {proposal[1]} - {proposal[2]}")
        print(f"   Proposal ID: {proposal_id}")
        print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made to the database")
        print()

    # Calculate stats
    total_sections = len(MISSING_SECTIONS_DATA)
    total_items = sum(len(section['items']) for section in MISSING_SECTIONS_DATA)
    total_value = sum(float(section['section_total']) for section in MISSING_SECTIONS_DATA)
    total_timeline = len(TIMELINE_DATA)
    total_labor = len(LABOR_DATA)

    print(f"📊 DATA TO ADD:")
    print(f"   Sections: {total_sections}")
    print(f"   Line Items: {total_items}")
    print(f"   Timeline Events: {total_timeline}")
    print(f"   Labor Items: {total_labor}")
    print(f"   Total Section Value: ${total_value:,.2f}")
    print()

    # Get current state
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_sections WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        current_sections = result.scalar()

        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_line_items WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        current_items = result.scalar()

        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_timeline WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        current_timeline = result.scalar()

        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_labor WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        current_labor = result.scalar()

    print(f"📊 CURRENT DATABASE STATE:")
    print(f"   Sections: {current_sections}")
    print(f"   Line Items: {current_items}")
    print(f"   Timeline Events: {current_timeline}")
    print(f"   Labor Items: {current_labor}")
    print()

    print(f"📊 AFTER ADDING:")
    print(f"   Sections: {current_sections + total_sections}")
    print(f"   Line Items: {current_items + total_items}")
    print(f"   Timeline Events: {current_timeline + total_timeline}")
    print(f"   Labor Items: {current_labor + total_labor}")
    print()

    # Display preview of sections
    if total_sections > 0:
        print("=" * 120)
        print("SECTIONS TO BE ADDED:")
        print("=" * 120)

        for idx, section_data in enumerate(MISSING_SECTIONS_DATA, 1):
            print(f"\n{idx}. {section_data['section_name']} ({section_data['section_type']})")
            print(f"   Section Total: ${float(section_data['section_total']):,.2f}")
            print(f"   Items: {len(section_data['items'])}")

            # Show first 3 items
            for item_idx, item in enumerate(section_data['items'][:3], 1):
                print(f"      {item_idx}. {item['description'][:60]}")
                print(f"         Qty: {item['quantity']}, Price: ${float(item['unit_price']):,.2f}, "
                      f"Subtotal: ${float(item['subtotal']):,.2f}")

            if len(section_data['items']) > 3:
                print(f"      ... and {len(section_data['items']) - 3} more items")

        print()
    else:
        print("⚠️  WARNING: MISSING_SECTIONS_DATA is empty! Please paste your data into the script.")
        print()

    # Display preview of timeline
    if total_timeline > 0:
        print("=" * 120)
        print("TIMELINE EVENTS TO BE ADDED:")
        print("=" * 120)

        for idx, event in enumerate(TIMELINE_DATA[:5], 1):
            print(f"\n{idx}. {event['title']}")
            print(f"   Date: {event['event_date']}, Time: {event['start_time']} - {event['end_time']}")
            print(f"   Location: {event.get('location', 'N/A')}")

        if len(TIMELINE_DATA) > 5:
            print(f"\n... and {len(TIMELINE_DATA) - 5} more timeline events")

        print()

    # Display preview of labor
    if total_labor > 0:
        print("=" * 120)
        print("LABOR ITEMS TO BE ADDED:")
        print("=" * 120)

        for idx, labor in enumerate(LABOR_DATA[:5], 1):
            print(f"\n{idx}. {labor['task_name']}")
            print(f"   Date: {labor['labor_date']}, Qty: {labor['quantity']}")
            print(f"   Hours: {labor['regular_hours']} regular, {labor['overtime_hours']} OT")
            print(f"   Subtotal: ${float(labor['subtotal']):,.2f}")

        if len(LABOR_DATA) > 5:
            print(f"\n... and {len(LABOR_DATA) - 5} more labor items")

        print()

    if dry_run:
        print("=" * 120)
        print("⚠️  DRY RUN COMPLETE - Run with --execute to apply changes")
        print("=" * 120)
        return

    # Confirm before proceeding
    print("=" * 120)
    response = input("⚠️  Proceed with adding this data? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled by user")
        return

    print()
    print("=" * 120)
    print("ADDING DATA...")
    print("=" * 120)

    sections_added = 0
    items_added = 0
    timeline_added = 0
    labor_added = 0

    with engine.begin() as conn:
        # Add sections and line items
        for section_data in MISSING_SECTIONS_DATA:
            section_id = str(uuid_lib.uuid4())
            now = datetime.utcnow()

            # Insert section
            conn.execute(
                text("""
                    INSERT INTO proposal_sections (
                        id, proposal_id, section_name, section_type, display_order,
                        is_expanded, section_total, notes, created_at, updated_at
                    ) VALUES (
                        :id, :proposal_id, :section_name, :section_type, :display_order,
                        :is_expanded, :section_total, :notes, :created_at, :updated_at
                    )
                """),
                {
                    "id": section_id,
                    "proposal_id": proposal_id,
                    "section_name": section_data['section_name'],
                    "section_type": section_data['section_type'],
                    "display_order": section_data.get('display_order', 0),
                    "is_expanded": section_data.get('is_expanded', True),
                    "section_total": section_data['section_total'],
                    "notes": section_data.get('notes'),
                    "created_at": now,
                    "updated_at": now
                }
            )
            sections_added += 1
            print(f"✅ Added section: {section_data['section_name']}")

            # Insert line items
            for item_idx, item_data in enumerate(section_data['items']):
                item_id = str(uuid_lib.uuid4())

                conn.execute(
                    text("""
                        INSERT INTO proposal_line_items (
                            id, section_id, proposal_id, item_number, description,
                            quantity, duration, unit_price, discount, subtotal,
                            category, item_type, notes, display_order,
                            created_at, updated_at
                        ) VALUES (
                            :id, :section_id, :proposal_id, :item_number, :description,
                            :quantity, :duration, :unit_price, :discount, :subtotal,
                            :category, :item_type, :notes, :display_order,
                            :created_at, :updated_at
                        )
                    """),
                    {
                        "id": item_id,
                        "section_id": section_id,
                        "proposal_id": proposal_id,
                        "item_number": item_data.get('item_number'),
                        "description": item_data['description'],
                        "quantity": item_data['quantity'],
                        "duration": item_data.get('duration', '1 Days'),
                        "unit_price": item_data['unit_price'],
                        "discount": item_data.get('discount', '0.00'),
                        "subtotal": item_data['subtotal'],
                        "category": item_data.get('category'),
                        "item_type": item_data.get('item_type'),
                        "notes": item_data.get('notes'),
                        "display_order": item_idx,
                        "created_at": now,
                        "updated_at": now
                    }
                )
                items_added += 1

            print(f"   Added {len(section_data['items'])} line items")

        # Add timeline events
        if TIMELINE_DATA:
            print()
            print("Adding timeline events...")
            for timeline_data in TIMELINE_DATA:
                timeline_id = str(uuid_lib.uuid4())
                now = datetime.utcnow()

                conn.execute(
                    text("""
                        INSERT INTO proposal_timeline (
                            id, proposal_id, event_date, start_time, end_time,
                            title, location, cost, display_order, created_at
                        ) VALUES (
                            :id, :proposal_id, :event_date, :start_time, :end_time,
                            :title, :location, :cost, :display_order, :created_at
                        )
                    """),
                    {
                        "id": timeline_id,
                        "proposal_id": proposal_id,
                        "event_date": timeline_data['event_date'],
                        "start_time": timeline_data.get('start_time'),
                        "end_time": timeline_data.get('end_time'),
                        "title": timeline_data['title'],
                        "location": timeline_data.get('location'),
                        "cost": timeline_data.get('cost', '0.00'),
                        "display_order": timeline_data.get('display_order', 0),
                        "created_at": now
                    }
                )
                timeline_added += 1

            print(f"✅ Added {timeline_added} timeline events")

        # Add labor items
        if LABOR_DATA:
            print()
            print("Adding labor items...")
            for labor_data in LABOR_DATA:
                labor_id = str(uuid_lib.uuid4())
                now = datetime.utcnow()

                conn.execute(
                    text("""
                        INSERT INTO proposal_labor (
                            id, proposal_id, task_name, quantity, labor_date,
                            start_time, end_time, regular_hours, overtime_hours,
                            double_time_hours, hourly_rate, subtotal, notes,
                            display_order, created_at
                        ) VALUES (
                            :id, :proposal_id, :task_name, :quantity, :labor_date,
                            :start_time, :end_time, :regular_hours, :overtime_hours,
                            :double_time_hours, :hourly_rate, :subtotal, :notes,
                            :display_order, :created_at
                        )
                    """),
                    {
                        "id": labor_id,
                        "proposal_id": proposal_id,
                        "task_name": labor_data['task_name'],
                        "quantity": labor_data.get('quantity', 1),
                        "labor_date": labor_data['labor_date'],
                        "start_time": labor_data.get('start_time'),
                        "end_time": labor_data.get('end_time'),
                        "regular_hours": labor_data.get('regular_hours', '0.00'),
                        "overtime_hours": labor_data.get('overtime_hours', '0.00'),
                        "double_time_hours": labor_data.get('double_time_hours', '0.00'),
                        "hourly_rate": labor_data.get('hourly_rate', '0.00'),
                        "subtotal": labor_data.get('subtotal', '0.00'),
                        "notes": labor_data.get('notes'),
                        "display_order": labor_data.get('display_order', 0),
                        "created_at": now
                    }
                )
                labor_added += 1

            print(f"✅ Added {labor_added} labor items")

    print()
    print("=" * 120)
    print("✅ SUCCESSFULLY ADDED:")
    print("=" * 120)
    print(f"   Sections: {sections_added}")
    print(f"   Line Items: {items_added}")
    print(f"   Timeline Events: {timeline_added}")
    print(f"   Labor Items: {labor_added}")
    print(f"   Total Section Value: ${total_value:,.2f}")
    print()

    # Verification
    print("=" * 120)
    print("VERIFICATION:")
    print("=" * 120)

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_sections WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        section_count = result.scalar()

        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_line_items WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        item_count = result.scalar()

        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_timeline WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        timeline_count = result.scalar()

        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_labor WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        labor_count = result.scalar()

        result = conn.execute(
            text("SELECT SUM(section_total) FROM proposal_sections WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        section_total = result.scalar()

        print(f"   Total sections now: {section_count}")
        print(f"   Total line items now: {item_count}")
        print(f"   Total timeline events now: {timeline_count}")
        print(f"   Total labor items now: {labor_count}")
        print(f"   Total section value: ${float(section_total or 0):,.2f}")
        print()

    print("=" * 120)
    print("✅ COMPLETE!")
    print("=" * 120)


def main():
    """Main function."""

    import argparse

    parser = argparse.ArgumentParser(description='Add missing data to proposal 302946')
    parser.add_argument('job_number', nargs='?', default='302946', help='Job number (default: 302946)')
    parser.add_argument('--execute', action='store_true', help='Execute changes (default is dry-run)')
    parser.add_argument('--db-url', help='Custom database URL')

    args = parser.parse_args()

    # Use provided URL or fall back to settings
    db_url = args.db_url or settings.DATABASE_URL

    print(f"Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print()

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Add missing data
    add_missing_data(engine, args.job_number, dry_run=not args.execute)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
