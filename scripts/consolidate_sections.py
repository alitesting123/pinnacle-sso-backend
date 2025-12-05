#!/usr/bin/env python3
"""
Consolidate Duplicate Sections
-------------------------------
This script merges multiple sections with the same name into ONE section,
using the category field to organize equipment types.

Example: 7 "General Session | Hudson Ballroom IV,V, VI" sections
         → 1 "General Session | Hudson Ballroom IV,V, VI" section
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings


def find_duplicate_sections(engine, job_number):
    """Find sections with duplicate names in a proposal."""

    query = text("""
        SELECT
            p.id as proposal_id,
            p.job_number,
            p.client_name,
            ps.section_name,
            COUNT(*) as section_count,
            SUM(ps.section_total) as total_value,
            STRING_AGG(DISTINCT ps.section_type, ', ') as section_types
        FROM proposals p
        JOIN proposal_sections ps ON p.id = ps.proposal_id
        WHERE p.job_number = :job_number
        GROUP BY p.id, p.job_number, p.client_name, ps.section_name
        HAVING COUNT(*) > 1
        ORDER BY section_name
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"job_number": job_number})
        return result.fetchall()


def get_sections_to_merge(engine, proposal_id, section_name):
    """Get all sections with the same name."""

    query = text("""
        SELECT
            id,
            section_name,
            section_type,
            display_order,
            section_total,
            created_at
        FROM proposal_sections
        WHERE proposal_id = :proposal_id
        AND section_name = :section_name
        ORDER BY display_order, created_at
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "proposal_id": proposal_id,
            "section_name": section_name
        })
        return result.fetchall()


def get_line_items_for_section(engine, section_id):
    """Get all line items for a section."""

    query = text("""
        SELECT
            id,
            description,
            quantity,
            category,
            subtotal
        FROM proposal_line_items
        WHERE section_id = :section_id
        ORDER BY display_order
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"section_id": section_id})
        return result.fetchall()


def consolidate_sections(engine, job_number, dry_run=True):
    """Consolidate duplicate sections into single sections."""

    print("=" * 120)
    print("CONSOLIDATE DUPLICATE SECTIONS")
    print("=" * 120)
    print()

    # Get proposal
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

    # Find duplicate sections
    duplicates = find_duplicate_sections(engine, job_number)

    if not duplicates:
        print("✅ No duplicate sections found - all sections have unique names!")
        return

    print(f"📊 FOUND {len(duplicates)} SECTION NAME(S) WITH DUPLICATES:")
    print("-" * 120)

    for dup in duplicates:
        section_name = dup[3]
        count = dup[4]
        total_value = dup[5]
        types = dup[6]

        print(f"\n  Section: {section_name}")
        print(f"  Duplicates: {count} sections")
        print(f"  Types: {types}")
        print(f"  Combined Total: ${float(total_value):,.2f}")

    print()

    # Process each duplicate set
    for dup in duplicates:
        proposal_id = str(dup[0])
        section_name = dup[3]

        print("=" * 120)
        print(f"CONSOLIDATING: {section_name}")
        print("=" * 120)

        # Get all sections with this name
        sections = get_sections_to_merge(engine, proposal_id, section_name)

        print(f"\nFound {len(sections)} sections to merge:")
        print("-" * 120)

        all_items = []
        total_value = 0

        for idx, section in enumerate(sections, 1):
            section_id = str(section[0])
            section_type = section[2]
            section_total = float(section[4] or 0)

            # Get line items
            items = get_line_items_for_section(engine, section_id)

            print(f"\n  {idx}. Section ID: {section_id[:8]}...")
            print(f"     Type: {section_type}")
            print(f"     Total: ${section_total:,.2f}")
            print(f"     Items: {len(items)}")

            for item in items:
                item_id = str(item[0])
                description = item[1]
                quantity = item[2]
                category = item[3]
                subtotal = float(item[4] or 0)

                print(f"        - {description[:50]} (Qty: {quantity}, Cat: {category}, ${subtotal:,.2f})")

                all_items.append({
                    'id': item_id,
                    'section_id': section_id,
                    'section_type': section_type,
                    'description': description,
                    'category': category,
                    'subtotal': subtotal
                })

                total_value += subtotal

        print()
        print("-" * 120)
        print(f"CONSOLIDATED RESULT:")
        print(f"  Total Items: {len(all_items)}")
        print(f"  Total Value: ${total_value:,.2f}")
        print()

        if dry_run:
            print("⚠️  DRY RUN - Would perform the following:")
            print(f"  1. Keep first section (ID: {str(sections[0][0])[:8]}...)")
            print(f"  2. Move {len(all_items)} items to first section")
            print(f"  3. Update section total to ${total_value:,.2f}")
            print(f"  4. Delete {len(sections) - 1} duplicate sections")
            print()
        else:
            # Perform consolidation
            print("🔄 CONSOLIDATING...")

            with engine.begin() as conn:
                # Keep the first section (lowest display_order)
                primary_section_id = str(sections[0][0])
                primary_section_type = sections[0][2]

                print(f"\n  ✅ Keeping section: {primary_section_id[:8]}... (Type: {primary_section_type})")

                # Move all items to primary section and ensure category is set
                items_moved = 0
                for item in all_items:
                    if item['section_id'] != primary_section_id:
                        # Move item to primary section
                        conn.execute(
                            text("""
                                UPDATE proposal_line_items
                                SET section_id = :new_section_id,
                                    category = COALESCE(NULLIF(category, ''), :category),
                                    updated_at = :updated_at
                                WHERE id = :item_id
                            """),
                            {
                                "new_section_id": primary_section_id,
                                "category": item['section_type'].lower() if item['section_type'] else item['category'],
                                "updated_at": datetime.utcnow(),
                                "item_id": item['id']
                            }
                        )
                        items_moved += 1

                print(f"  ✅ Moved {items_moved} items to primary section")

                # Update primary section total
                conn.execute(
                    text("""
                        UPDATE proposal_sections
                        SET section_total = :total,
                            section_type = :section_type,
                            updated_at = :updated_at
                        WHERE id = :section_id
                    """),
                    {
                        "total": total_value,
                        "section_type": "Multiple",  # Since it contains multiple types
                        "updated_at": datetime.utcnow(),
                        "section_id": primary_section_id
                    }
                )

                print(f"  ✅ Updated section total to ${total_value:,.2f}")

                # Delete duplicate sections
                sections_to_delete = [str(s[0]) for s in sections[1:]]

                if sections_to_delete:
                    for section_id in sections_to_delete:
                        conn.execute(
                            text("DELETE FROM proposal_sections WHERE id = :id"),
                            {"id": section_id}
                        )

                    print(f"  ✅ Deleted {len(sections_to_delete)} duplicate sections")

            print()
            print("  ✅ CONSOLIDATION COMPLETE!")
            print()

    if dry_run:
        print()
        print("=" * 120)
        print("⚠️  DRY RUN COMPLETE - Run with --execute to apply changes")
        print("=" * 120)
    else:
        # Verification
        print()
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

            # Check for remaining duplicates
            remaining_dups = find_duplicate_sections(engine, job_number)

            print(f"   Total sections now: {section_count}")
            print(f"   Total line items: {item_count}")
            print(f"   Remaining duplicates: {len(remaining_dups)}")
            print()

        print("=" * 120)
        print("✅ COMPLETE!")
        print("=" * 120)


def main():
    """Main function."""

    import argparse

    parser = argparse.ArgumentParser(description='Consolidate duplicate sections in a proposal')
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

    # Consolidate sections
    consolidate_sections(engine, args.job_number, dry_run=not args.execute)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
