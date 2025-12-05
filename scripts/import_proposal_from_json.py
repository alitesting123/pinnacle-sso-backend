#!/usr/bin/env python3
"""
Import Missing Proposal Data from JSON
---------------------------------------
This script imports missing sections, line items, timeline, and labor
data from a JSON file for a specific proposal.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import uuid as uuid_lib
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings


def load_json_file(filepath):
    """Load JSON data from file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return None


def import_proposal_data(engine, json_data, job_number, dry_run=True):
    """Import proposal data from JSON."""

    print("=" * 120)
    print("IMPORT PROPOSAL DATA FROM JSON")
    print("=" * 120)
    print()

    # Find proposal in JSON
    proposal_data = None
    for prop in json_data.get('proposals', []):
        if prop['proposal']['job_number'] == job_number:
            proposal_data = prop
            break

    if not proposal_data:
        print(f"❌ Proposal {job_number} not found in JSON!")
        return

    # Get proposal from database
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, job_number, client_name FROM proposals WHERE job_number = :job_number"),
            {"job_number": job_number}
        )
        db_proposal = result.fetchone()

        if not db_proposal:
            print(f"❌ Proposal {job_number} not found in database!")
            return

        proposal_id = str(db_proposal[0])
        print(f"✅ Found proposal: {db_proposal[1]} - {db_proposal[2]}")
        print(f"   Proposal ID: {proposal_id}")
        print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made to the database")
        print()

    # Analyze what needs to be imported
    sections_to_import = proposal_data.get('sections', [])
    timeline_to_import = proposal_data.get('timeline', [])
    labor_to_import = proposal_data.get('labor', [])

    # Count line items
    total_line_items = 0
    for section in sections_to_import:
        total_line_items += len(section.get('items', []))

    print(f"📊 DATA TO IMPORT:")
    print(f"   Sections: {len(sections_to_import)}")
    print(f"   Line Items: {total_line_items}")
    print(f"   Timeline Events: {len(timeline_to_import)}")
    print(f"   Labor Items: {len(labor_to_import)}")
    print()

    # Check current database state
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

    sections_to_add = len(sections_to_import) - current_sections
    items_to_add = total_line_items - current_items
    timeline_to_add = len(timeline_to_import) - current_timeline
    labor_to_add = len(labor_to_import) - current_labor

    print(f"📊 TO BE ADDED:")
    print(f"   Sections: {sections_to_add}")
    print(f"   Line Items: {items_to_add}")
    print(f"   Timeline Events: {timeline_to_add}")
    print(f"   Labor Items: {labor_to_add}")
    print()

    if dry_run:
        # Display sections that will be added
        print("=" * 120)
        print("SECTIONS TO BE IMPORTED:")
        print("=" * 120)

        for idx, section in enumerate(sections_to_import, 1):
            section_name = section.get('section_name', 'Unknown')
            section_type = section.get('section_type', 'Unknown')
            section_total = section.get('section_total', '0.00')
            num_items = len(section.get('items', []))

            print(f"\n  {idx}. {section_name}")
            print(f"      Type: {section_type}")
            print(f"      Total: ${float(section_total):,.2f}")
            print(f"      Items: {num_items}")

        print()
        print("=" * 120)
        print("⚠️  DRY RUN COMPLETE - Run with --execute to apply changes")
        print("=" * 120)
        return

    # Confirm before proceeding
    print("=" * 120)
    response = input("⚠️  Proceed with importing this data? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled by user")
        return

    print()
    print("=" * 120)
    print("IMPORTING DATA...")
    print("=" * 120)

    sections_added = 0
    items_added = 0
    timeline_added = 0
    labor_added = 0

    with engine.begin() as conn:
        # Import sections and line items
        for section_data in sections_to_import:
            section_name = section_data.get('section_name')

            # Check if section already exists
            result = conn.execute(
                text("""
                    SELECT id FROM proposal_sections
                    WHERE proposal_id = :proposal_id
                    AND section_name = :section_name
                """),
                {
                    "proposal_id": proposal_id,
                    "section_name": section_name
                }
            )
            existing_section = result.fetchone()

            if existing_section:
                print(f"⏭️  Section already exists: {section_name}")
                section_id = str(existing_section[0])
            else:
                # Insert new section
                section_id = str(uuid_lib.uuid4())
                now = datetime.utcnow()

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
                        "section_name": section_data.get('section_name'),
                        "section_type": section_data.get('section_type'),
                        "display_order": section_data.get('display_order', 0),
                        "is_expanded": section_data.get('is_expanded', True),
                        "section_total": section_data.get('section_total', '0.00'),
                        "notes": section_data.get('notes'),
                        "created_at": now,
                        "updated_at": now
                    }
                )
                sections_added += 1
                print(f"✅ Added section: {section_data.get('section_name')}")

            # Import line items for this section
            items = section_data.get('items', [])
            for item_data in items:
                # Check if item already exists (by description)
                result = conn.execute(
                    text("""
                        SELECT id FROM proposal_line_items
                        WHERE section_id = :section_id
                        AND description = :description
                    """),
                    {
                        "section_id": section_id,
                        "description": item_data.get('description')
                    }
                )
                if result.fetchone():
                    continue  # Skip if already exists

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
                        "description": item_data.get('description'),
                        "quantity": item_data.get('quantity', 1),
                        "duration": item_data.get('duration', '1 Days'),
                        "unit_price": item_data.get('unit_price', '0.00'),
                        "discount": item_data.get('discount', '0.00'),
                        "subtotal": item_data.get('subtotal', '0.00'),
                        "category": item_data.get('category'),
                        "item_type": item_data.get('item_type'),
                        "notes": item_data.get('notes'),
                        "display_order": 0,
                        "created_at": now,
                        "updated_at": now
                    }
                )
                items_added += 1

            if items:
                print(f"   Added {len(items)} line items")

        # Import timeline events
        print()
        print("Importing timeline events...")
        for timeline_data in timeline_to_import:
            # Check if already exists
            result = conn.execute(
                text("""
                    SELECT id FROM proposal_timeline
                    WHERE proposal_id = :proposal_id
                    AND title = :title
                    AND event_date = :event_date
                """),
                {
                    "proposal_id": proposal_id,
                    "title": timeline_data.get('title'),
                    "event_date": timeline_data.get('event_date')
                }
            )
            if result.fetchone():
                continue

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
                    "event_date": timeline_data.get('event_date'),
                    "start_time": timeline_data.get('start_time'),
                    "end_time": timeline_data.get('end_time'),
                    "title": timeline_data.get('title'),
                    "location": timeline_data.get('location'),
                    "cost": timeline_data.get('cost', '0.00'),
                    "display_order": timeline_data.get('display_order', 0),
                    "created_at": now
                }
            )
            timeline_added += 1

        print(f"✅ Added {timeline_added} timeline events")

        # Import labor items
        print()
        print("Importing labor items...")
        for labor_data in labor_to_import:
            # Check if already exists
            result = conn.execute(
                text("""
                    SELECT id FROM proposal_labor
                    WHERE proposal_id = :proposal_id
                    AND task_name = :task_name
                    AND labor_date = :labor_date
                """),
                {
                    "proposal_id": proposal_id,
                    "task_name": labor_data.get('task_name'),
                    "labor_date": labor_data.get('labor_date')
                }
            )
            if result.fetchone():
                continue

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
                    "task_name": labor_data.get('task_name'),
                    "quantity": labor_data.get('quantity', 1),
                    "labor_date": labor_data.get('labor_date'),
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
    print("✅ SUCCESSFULLY IMPORTED:")
    print("=" * 120)
    print(f"   Sections: {sections_added}")
    print(f"   Line Items: {items_added}")
    print(f"   Timeline Events: {timeline_added}")
    print(f"   Labor Items: {labor_added}")
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

        print(f"   Total sections now: {section_count}")
        print(f"   Total line items now: {item_count}")
        print(f"   Total timeline events now: {timeline_count}")
        print(f"   Total labor items now: {labor_count}")
        print()

    print("=" * 120)
    print("✅ COMPLETE!")
    print("=" * 120)


def main():
    """Main function."""

    import argparse

    parser = argparse.ArgumentParser(description='Import proposal data from JSON file')
    parser.add_argument('json_file', help='Path to JSON file with proposal data')
    parser.add_argument('job_number', nargs='?', default='302946', help='Job number to import (default: 302946)')
    parser.add_argument('--execute', action='store_true', help='Execute import (default is dry-run)')
    parser.add_argument('--db-url', help='Custom database URL')

    args = parser.parse_args()

    # Load JSON
    json_data = load_json_file(args.json_file)
    if not json_data:
        sys.exit(1)

    # Use provided URL or fall back to settings
    db_url = args.db_url or settings.DATABASE_URL

    print(f"Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print()

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Import data
    import_proposal_data(engine, json_data, args.job_number, dry_run=not args.execute)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
