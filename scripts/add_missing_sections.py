#!/usr/bin/env python3
"""
Add Missing Sections and Line Items
------------------------------------
This script adds missing sections and line items to proposal 305342
to fix the pricing discrepancy.
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


# Missing sections data
MISSING_SECTIONS_DATA = [
    {
        "section_name": "General Session | Hudson Ballroom IV,V, VI",
        "section_type": "Networking",
        "display_order": 5,
        "section_total": "0.00",
        "items": [
            {
                "description": "MIS | Internet Access (5 Mbps Aggregate)",
                "quantity": 250,
                "duration": "1 Days",
                "unit_price": "0.00",
                "discount": "0.00",
                "subtotal": "0.00",
                "category": "networking",
                "notes": "Wifi is included in Hotel Contract. Password: AWS_WIFISPONSOR"
            }
        ]
    },
    {
        "section_name": "General Session | Hudson Ballroom IV,V, VI",
        "section_type": "Staging",
        "display_order": 6,
        "section_total": "4400.00",
        "items": [
            {
                "description": "Drape Panel, 16' x 10' Slate",
                "quantity": 6,
                "duration": "1 Days",
                "unit_price": "100.00",
                "discount": "0.00",
                "subtotal": "600.00",
                "category": "staging"
            },
            {
                "description": "Scenic Design",
                "quantity": 1,
                "duration": "1 Days",
                "unit_price": "3800.00",
                "discount": "0.00",
                "subtotal": "3800.00",
                "category": "staging",
                "notes": "If available as order was not confirmed by 9/8/25. 8 Upplight Panels - (4) 16'h x 3'w WHITE AV Drop Wall, complete with rental hardware and jacks [192 SQ. FT.] -LIMITED SEAMS (4) 14'h x 1'w WHITE AV Drop Wall, complete with rental hardware and jacks [56 SQ. FT.] -LIMITED SEAMS"
            }
        ]
    },
    {
        "section_name": "General Session | Hudson Ballroom IV,V, VI",
        "section_type": "Video",
        "display_order": 7,
        "section_total": "1287.75",
        "items": [
            {
                "description": "INACTIVE - Analog Way Pulse",
                "quantity": 1,
                "duration": "1 Days",
                "unit_price": "800.00",
                "discount": "-120.00",
                "subtotal": "680.00",
                "category": "video"
            },
            {
                "description": "Confidence Monitor",
                "quantity": 1,
                "duration": "1 Days",
                "unit_price": "715.00",
                "discount": "-107.25",
                "subtotal": "607.75",
                "category": "video"
            }
        ]
    },
    {
        "section_name": "Breakout | Holland",
        "section_type": "Breakout Room",
        "display_order": 8,
        "section_total": "2078.25",
        "items": [
            {"description": "8\" Powered Speaker", "quantity": 1, "duration": "1 Days", "unit_price": "155.00", "discount": "-23.25", "subtotal": "131.75", "category": "audio"},
            {"description": "H50 Wireless Microphone Handheld", "quantity": 4, "duration": "1 Days", "unit_price": "270.00", "discount": "-162.00", "subtotal": "918.00", "category": "audio", "notes": "Please place 1 Handheld on mic stand at podium."},
            {"description": "Microphone Table Stand, Black", "quantity": 1, "duration": "1 Days", "unit_price": "15.00", "discount": "-2.25", "subtotal": "12.75", "category": "audio"},
            {"description": "4ch Hybrid Audio Mixer", "quantity": 1, "duration": "1 Days", "unit_price": "115.00", "discount": "-17.25", "subtotal": "97.75", "category": "audio"},
            {"description": "Mono Audio Direct Box SW318", "quantity": 1, "duration": "1 Days", "unit_price": "60.00", "discount": "-9.00", "subtotal": "51.00", "category": "audio"},
            {"description": "Laptop | Standard", "quantity": 1, "duration": "1 Days", "unit_price": "270.00", "discount": "-40.50", "subtotal": "229.50", "category": "computer", "notes": "Client to operate laptop from podium."},
            {"description": "Meeting Room Package 8' Tripod Screen", "quantity": 1, "duration": "1 Days", "unit_price": "750.00", "discount": "-112.50", "subtotal": "637.50", "category": "projection"}
        ]
    },
    {
        "section_name": "Breakout | Liberty",
        "section_type": "Breakout Room",
        "display_order": 9,
        "section_total": "1377.00",
        "items": [
            {"description": "8\" Powered Speaker", "quantity": 1, "duration": "1 Days", "unit_price": "155.00", "discount": "-23.25", "subtotal": "131.75", "category": "audio"},
            {"description": "Wireless Microphone Receiver", "quantity": 1, "duration": "1 Days", "unit_price": "270.00", "discount": "-40.50", "subtotal": "229.50", "category": "audio", "notes": "Please place 1 Handheld on mic stand at podium."},
            {"description": "Mono Audio Direct Box SW318", "quantity": 1, "duration": "1 Days", "unit_price": "60.00", "discount": "-9.00", "subtotal": "51.00", "category": "audio"},
            {"description": "4ch Hybrid Audio Mixer", "quantity": 1, "duration": "1 Days", "unit_price": "115.00", "discount": "-17.25", "subtotal": "97.75", "category": "audio"},
            {"description": "Laptop | Standard", "quantity": 1, "duration": "1 Days", "unit_price": "270.00", "discount": "-40.50", "subtotal": "229.50", "category": "computer", "notes": "Presenter to operate podium"},
            {"description": "Meeting Room Package 8' Tripod Screen", "quantity": 1, "duration": "1 Days", "unit_price": "750.00", "discount": "-112.50", "subtotal": "637.50", "category": "projection"}
        ]
    },
    {
        "section_name": "Breakout | Palisades",
        "section_type": "Breakout Room",
        "display_order": 10,
        "section_total": "1836.00",
        "items": [
            {"description": "8\" Powered Speaker", "quantity": 1, "duration": "1 Days", "unit_price": "155.00", "discount": "-23.25", "subtotal": "131.75", "category": "audio"},
            {"description": "Wireless Microphone Receiver", "quantity": 2, "duration": "1 Days", "unit_price": "270.00", "discount": "-81.00", "subtotal": "459.00", "category": "audio", "notes": "Please place 1 on mic stand at podium."},
            {"description": "H50 Wireless Microphone Handheld", "quantity": 1, "duration": "1 Days", "unit_price": "270.00", "discount": "-40.50", "subtotal": "229.50", "category": "audio"},
            {"description": "Mono Audio Direct Box SW318", "quantity": 1, "duration": "1 Days", "unit_price": "60.00", "discount": "-9.00", "subtotal": "51.00", "category": "audio"},
            {"description": "4ch Hybrid Audio Mixer", "quantity": 1, "duration": "1 Days", "unit_price": "115.00", "discount": "-17.25", "subtotal": "97.75", "category": "audio"},
            {"description": "Laptop | Standard", "quantity": 1, "duration": "1 Days", "unit_price": "270.00", "discount": "-40.50", "subtotal": "229.50", "category": "computer", "notes": "Presenter to operate at podium"},
            {"description": "Meeting Room Package 8' Tripod Screen", "quantity": 1, "duration": "1 Days", "unit_price": "750.00", "discount": "-112.50", "subtotal": "637.50", "category": "projection"}
        ]
    },
    {
        "section_name": "Breakout | Hudson I, II",
        "section_type": "Breakout Room",
        "display_order": 11,
        "section_total": "1848.75",
        "items": [
            {"description": "8\" Powered Speaker", "quantity": 1, "duration": "1 Days", "unit_price": "155.00", "discount": "-23.25", "subtotal": "131.75", "category": "audio"},
            {"description": "Mono Audio Direct Box SW318", "quantity": 1, "duration": "1 Days", "unit_price": "60.00", "discount": "-9.00", "subtotal": "51.00", "category": "audio"},
            {"description": "H50 Wireless Microphone Handheld", "quantity": 3, "duration": "1 Days", "unit_price": "270.00", "discount": "-121.50", "subtotal": "688.50", "category": "audio", "notes": "Please place 1 on mic stand at podium. Client to provide and operate own laptop from podium."},
            {"description": "Microphone Table Stand, Black", "quantity": 1, "duration": "1 Days", "unit_price": "15.00", "discount": "-2.25", "subtotal": "12.75", "category": "audio"},
            {"description": "4ch Hybrid Audio Mixer", "quantity": 1, "duration": "1 Days", "unit_price": "115.00", "discount": "-17.25", "subtotal": "97.75", "category": "audio"},
            {"description": "Laptop | Standard", "quantity": 1, "duration": "1 Days", "unit_price": "270.00", "discount": "-40.50", "subtotal": "229.50", "category": "computer"},
            {"description": "Meeting Room Package 8' Tripod Screen", "quantity": 1, "duration": "1 Days", "unit_price": "750.00", "discount": "-112.50", "subtotal": "637.50", "category": "projection"}
        ]
    },
    {
        "section_name": "Exhibitor Booths | Manhattan & Prefunction",
        "section_type": "Exhibitor Space",
        "display_order": 12,
        "section_total": "1130.50",
        "items": [
            {"description": "Portable Powered Column Speaker", "quantity": 2, "duration": "1 Days", "unit_price": "180.00", "discount": "-54.00", "subtotal": "306.00", "category": "audio"},
            {"description": "H50 Wireless Microphone Handheld", "quantity": 1, "duration": "1 Days", "unit_price": "270.00", "discount": "-40.50", "subtotal": "229.50", "category": "audio"},
            {"description": "Mono Audio Direct Box SW318", "quantity": 1, "duration": "1 Days", "unit_price": "70.00", "discount": "-10.50", "subtotal": "59.50", "category": "audio"},
            {"description": "USB Power Strip", "quantity": 18, "duration": "1 Days", "unit_price": "35.00", "discount": "-94.50", "subtotal": "535.50", "category": "computer", "notes": "Power to exhibitor tables on outskirts of room. 1 for Registration Table in pre-function area."}
        ]
    },
    {
        "section_name": "Copy-Office | Boardroom",
        "section_type": "Video",
        "display_order": 13,
        "section_total": "756.50",
        "items": [
            {"description": "LED Monitor, 4K 65\"", "quantity": 1, "duration": "1 Days", "unit_price": "890.00", "discount": "-133.50", "subtotal": "756.50", "category": "video"}
        ]
    }
]


def add_missing_sections(engine, job_number, dry_run=True):
    """Add missing sections and line items to a proposal."""

    print("=" * 120)
    print("ADD MISSING SECTIONS AND LINE ITEMS")
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

    # Stats
    total_sections = len(MISSING_SECTIONS_DATA)
    total_items = sum(len(section['items']) for section in MISSING_SECTIONS_DATA)
    total_value = sum(float(section['section_total']) for section in MISSING_SECTIONS_DATA)

    print(f"📊 SUMMARY OF CHANGES:")
    print(f"   Sections to add: {total_sections}")
    print(f"   Line items to add: {total_items}")
    print(f"   Total value: ${total_value:,.2f}")
    print()

    # Display sections
    print("=" * 120)
    print("SECTIONS TO BE ADDED:")
    print("=" * 120)

    for idx, section_data in enumerate(MISSING_SECTIONS_DATA, 1):
        print(f"\n{idx}. {section_data['section_name']} ({section_data['section_type']})")
        print(f"   Section Total: ${float(section_data['section_total']):,.2f}")
        print(f"   Items: {len(section_data['items'])}")

        for item_idx, item in enumerate(section_data['items'], 1):
            print(f"      {item_idx}. {item['description'][:60]}")
            print(f"         Qty: {item['quantity']}, Price: ${float(item['unit_price']):,.2f}, "
                  f"Discount: ${float(item['discount']):,.2f}, Subtotal: ${float(item['subtotal']):,.2f}")

    print()

    if dry_run:
        print("=" * 120)
        print("⚠️  DRY RUN COMPLETE - Run with --execute to apply changes")
        print("=" * 120)
        return

    # Confirm before proceeding
    print("=" * 120)
    response = input("⚠️  Proceed with adding these sections? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled by user")
        return

    print()
    print("=" * 120)
    print("ADDING SECTIONS AND LINE ITEMS...")
    print("=" * 120)

    sections_added = 0
    items_added = 0

    with engine.begin() as conn:
        for section_data in MISSING_SECTIONS_DATA:
            # Generate section UUID
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
                    "display_order": section_data['display_order'],
                    "is_expanded": True,
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
                        "duration": item_data['duration'],
                        "unit_price": item_data['unit_price'],
                        "discount": item_data['discount'],
                        "subtotal": item_data['subtotal'],
                        "category": item_data['category'],
                        "item_type": item_data.get('item_type'),
                        "notes": item_data.get('notes'),
                        "display_order": item_idx,
                        "created_at": now,
                        "updated_at": now
                    }
                )
                items_added += 1

            print(f"   Added {len(section_data['items'])} line items")

    print()
    print("=" * 120)
    print("✅ SUCCESSFULLY ADDED:")
    print("=" * 120)
    print(f"   Sections: {sections_added}")
    print(f"   Line Items: {items_added}")
    print(f"   Total Value: ${total_value:,.2f}")
    print()

    # Verify
    print("=" * 120)
    print("VERIFICATION:")
    print("=" * 120)

    with engine.connect() as conn:
        # Count sections
        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_sections WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        section_count = result.scalar()

        # Count line items
        result = conn.execute(
            text("SELECT COUNT(*) FROM proposal_line_items WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        item_count = result.scalar()

        # Sum section totals
        result = conn.execute(
            text("SELECT SUM(section_total) FROM proposal_sections WHERE proposal_id = :id"),
            {"id": proposal_id}
        )
        section_total = result.scalar()

        print(f"   Total sections now: {section_count}")
        print(f"   Total line items now: {item_count}")
        print(f"   Total section value: ${float(section_total):,.2f}")
        print()

    print("=" * 120)
    print("✅ COMPLETE!")
    print("=" * 120)


def main():
    """Main function."""

    import argparse

    parser = argparse.ArgumentParser(description='Add missing sections to proposal 305342')
    parser.add_argument('job_number', nargs='?', default='305342', help='Job number (default: 305342)')
    parser.add_argument('--execute', action='store_true', help='Execute changes (default is dry-run)')
    parser.add_argument('--db-url', help='Custom database URL')

    args = parser.parse_args()

    # Use provided URL or fall back to settings
    db_url = args.db_url or settings.DATABASE_URL

    print(f"Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print()

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Add sections
    add_missing_sections(engine, args.job_number, dry_run=not args.execute)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
