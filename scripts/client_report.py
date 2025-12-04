#!/usr/bin/env python3
"""
Client Report Generator
-----------------------
This script generates a comprehensive report for a specific client,
showing all proposals, line items, labor, timeline, and questions.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings


def print_header(title, width=120, char="="):
    """Print a formatted header."""
    print("\n" + char * width)
    print(f"{title}")
    print(char * width)


def format_currency(value):
    """Format a value as currency."""
    if value is None:
        return "$0.00"
    return f"${float(value):,.2f}"


def find_client_proposals(engine, search_term):
    """Find all proposals for a client by name, email, or job number."""
    query = text("""
        SELECT DISTINCT
            id,
            job_number,
            client_name,
            client_email,
            client_company,
            client_contact,
            client_phone
        FROM proposals
        WHERE
            LOWER(client_name) LIKE LOWER(:search)
            OR LOWER(client_email) LIKE LOWER(:search)
            OR LOWER(job_number) LIKE LOWER(:search)
            OR LOWER(client_company) LIKE LOWER(:search)
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"search": f"%{search_term}%"})
        return result.fetchall()


def get_proposal_full_details(engine, proposal_id):
    """Get complete details for a proposal."""

    # Get proposal info
    proposal_query = text("SELECT * FROM proposals WHERE id = :id")

    with engine.connect() as conn:
        result = conn.execute(proposal_query, {"id": proposal_id})
        proposal = result.fetchone()

        if not proposal:
            return None

        proposal_dict = dict(zip(result.keys(), proposal))

        # Get sections
        sections_query = text("""
            SELECT * FROM proposal_sections
            WHERE proposal_id = :proposal_id
            ORDER BY display_order
        """)
        result = conn.execute(sections_query, {"proposal_id": proposal_id})
        sections = [dict(zip(result.keys(), row)) for row in result.fetchall()]

        # Get line items for each section
        for section in sections:
            items_query = text("""
                SELECT * FROM proposal_line_items
                WHERE section_id = :section_id
                ORDER BY display_order
            """)
            result = conn.execute(items_query, {"section_id": section['id']})
            section['items'] = [dict(zip(result.keys(), row)) for row in result.fetchall()]

        # Get all line items (including those not in sections)
        all_items_query = text("""
            SELECT * FROM proposal_line_items
            WHERE proposal_id = :proposal_id
            ORDER BY display_order
        """)
        result = conn.execute(all_items_query, {"proposal_id": proposal_id})
        all_items = [dict(zip(result.keys(), row)) for row in result.fetchall()]

        # Get timeline events
        timeline_query = text("""
            SELECT * FROM proposal_timeline
            WHERE proposal_id = :proposal_id
            ORDER BY event_date, start_time
        """)
        result = conn.execute(timeline_query, {"proposal_id": proposal_id})
        timeline = [dict(zip(result.keys(), row)) for row in result.fetchall()]

        # Get labor items
        labor_query = text("""
            SELECT * FROM proposal_labor
            WHERE proposal_id = :proposal_id
            ORDER BY labor_date, start_time
        """)
        result = conn.execute(labor_query, {"proposal_id": proposal_id})
        labor = [dict(zip(result.keys(), row)) for row in result.fetchall()]

        # Get questions
        questions_query = text("""
            SELECT * FROM proposal_questions
            WHERE proposal_id = :proposal_id
            ORDER BY asked_at DESC
        """)
        result = conn.execute(questions_query, {"proposal_id": proposal_id})
        questions = [dict(zip(result.keys(), row)) for row in result.fetchall()]

        return {
            'proposal': proposal_dict,
            'sections': sections,
            'all_items': all_items,
            'timeline': timeline,
            'labor': labor,
            'questions': questions
        }


def display_client_report(engine, search_term):
    """Display comprehensive client report."""

    print_header(f"🔍 SEARCHING FOR CLIENT: {search_term}", char="=")

    # Find client proposals
    proposals = find_client_proposals(engine, search_term)

    if not proposals:
        print(f"\n❌ No client found matching: {search_term}")
        return

    # Get unique client info (from first proposal)
    client = proposals[0]

    print_header("👤 CLIENT INFORMATION", char="=")
    print(f"\n  Client Name: {client[2]}")
    print(f"  Company: {client[4] or 'N/A'}")
    print(f"  Contact Person: {client[5] or 'N/A'}")
    print(f"  Email: {client[3] or 'N/A'}")
    print(f"  Phone: {client[6] or 'N/A'}")
    print(f"\n  Total Proposals: {len(proposals)}")

    # Process each proposal
    for idx, prop in enumerate(proposals, 1):
        proposal_id = prop[0]
        job_number = prop[1]

        print_header(f"📋 PROPOSAL #{idx}: {job_number}", char="=")

        details = get_proposal_full_details(engine, proposal_id)

        if not details:
            print("  ❌ Could not retrieve proposal details")
            continue

        proposal = details['proposal']

        # Basic Proposal Info
        print_header("📊 PROPOSAL DETAILS", char="-")
        print(f"\n  Job Number: {proposal['job_number']}")
        print(f"  Status: {proposal['status']}")
        print(f"  Version: {proposal['version']}")
        print(f"\n  Event Location: {proposal['event_location'] or 'N/A'}")
        print(f"  Venue: {proposal['venue_name'] or 'N/A'}")
        print(f"  Event Dates: {proposal['start_date']} to {proposal['end_date']}")
        print(f"\n  Prepared By: {proposal['prepared_by'] or 'N/A'}")
        print(f"  Salesperson: {proposal['salesperson']} ({proposal['salesperson_email']})")
        print(f"  Created: {proposal['created_at']}")
        print(f"  Last Updated: {proposal['updated_at']}")

        if proposal['notes']:
            print(f"\n  Notes: {proposal['notes']}")

        # Pricing Summary
        print_header("💰 PRICING BREAKDOWN", char="-")
        print(f"\n  Product Subtotal: {format_currency(proposal['product_subtotal'])}")
        print(f"  Product Discount: {format_currency(proposal['product_discount'])}")
        print(f"  Product Total:    {format_currency(proposal['product_total'])}")
        print(f"\n  Labor Total:      {format_currency(proposal['labor_total'])}")
        print(f"  Service Charge:   {format_currency(proposal['service_charge'])}")
        print(f"  Tax Amount:       {format_currency(proposal['tax_amount'])}")
        print(f"\n  {'─' * 50}")
        print(f"  TOTAL COST:       {format_currency(proposal['total_cost'])}")
        print(f"  {'─' * 50}")

        # Sections and Line Items
        sections = details['sections']
        if sections:
            print_header(f"📦 SECTIONS & LINE ITEMS ({len(sections)} sections)", char="-")

            total_items = 0
            total_quantity = 0

            for section in sections:
                items = section['items']
                section_total = sum(item['subtotal'] for item in items if item['subtotal'])
                section_qty = sum(item['quantity'] for item in items if item['quantity'])

                print(f"\n  📁 {section['section_name']}")
                print(f"     Type: {section['section_type'] or 'N/A'}")
                print(f"     Section Total: {format_currency(section['section_total'])}")
                print(f"     Items: {len(items)}")

                if items:
                    print(f"\n     {'Item':<50} {'Qty':<6} {'Unit Price':<12} {'Discount':<12} {'Subtotal':<12}")
                    print(f"     {'-' * 100}")

                    for item in items:
                        desc = item['description'][:47] + "..." if len(item['description']) > 50 else item['description']
                        qty = item['quantity'] or 1
                        unit_price = format_currency(item['unit_price'])
                        discount = format_currency(item['discount'])
                        subtotal = format_currency(item['subtotal'])

                        print(f"     {desc:<50} {qty:<6} {unit_price:<12} {discount:<12} {subtotal:<12}")

                        if item['notes']:
                            print(f"         Note: {item['notes'][:80]}")

                    print(f"     {'-' * 100}")
                    print(f"     Section Items Total: {format_currency(section_total)}")
                    print(f"     Total Quantity: {section_qty}")

                total_items += len(items)
                total_quantity += section_qty

            print(f"\n  {'=' * 100}")
            print(f"  TOTAL LINE ITEMS: {total_items}")
            print(f"  TOTAL QUANTITY: {total_quantity}")
            print(f"  {'=' * 100}")

        # Check for orphaned line items (not in any section)
        all_items = details['all_items']
        items_in_sections = sum(len(s['items']) for s in sections)

        if len(all_items) > items_in_sections:
            orphaned_items = len(all_items) - items_in_sections
            print(f"\n  ⚠️  WARNING: {orphaned_items} line items not assigned to any section")

            # Find orphaned items
            section_item_ids = set()
            for section in sections:
                for item in section['items']:
                    section_item_ids.add(item['id'])

            print(f"\n  📋 ORPHANED LINE ITEMS:")
            for item in all_items:
                if item['id'] not in section_item_ids:
                    print(f"     - {item['description'][:70]}")
                    print(f"       Qty: {item['quantity']}, Price: {format_currency(item['unit_price'])}, Subtotal: {format_currency(item['subtotal'])}")

        # Timeline Events
        timeline = details['timeline']
        if timeline:
            print_header(f"📅 TIMELINE EVENTS ({len(timeline)} events)", char="-")

            for event in timeline:
                print(f"\n  📌 {event['title']}")
                print(f"     Date: {event['event_date']}")
                if event['start_time'] and event['end_time']:
                    print(f"     Time: {event['start_time']} - {event['end_time']}")
                if event['location']:
                    print(f"     Location: {event['location']}")
                if event['cost']:
                    print(f"     Cost: {format_currency(event['cost'])}")
                if event['notes']:
                    print(f"     Notes: {event['notes'][:80]}")

        # Labor Items
        labor = details['labor']
        if labor:
            print_header(f"👷 LABOR SCHEDULE ({len(labor)} items)", char="-")

            labor_total = sum(item['subtotal'] for item in labor if item['subtotal'])
            total_hours = sum(
                (item['regular_hours'] or 0) +
                (item['overtime_hours'] or 0) +
                (item['double_time_hours'] or 0)
                for item in labor
            )

            print(f"\n  Total Labor Items: {len(labor)}")
            print(f"  Total Hours: {total_hours}")
            print(f"  Total Labor Cost: {format_currency(labor_total)}")

            print(f"\n  {'Task':<40} {'Date':<12} {'Time':<15} {'Hours':<15} {'Rate':<12} {'Subtotal':<12}")
            print(f"  {'-' * 110}")

            for item in labor:
                task = item['task_name'][:37] + "..." if len(item['task_name']) > 40 else item['task_name']
                date = str(item['labor_date'])
                time_range = f"{item['start_time']}-{item['end_time']}" if item['start_time'] else "N/A"

                hours_parts = []
                if item['regular_hours']:
                    hours_parts.append(f"R:{item['regular_hours']}")
                if item['overtime_hours']:
                    hours_parts.append(f"OT:{item['overtime_hours']}")
                if item['double_time_hours']:
                    hours_parts.append(f"DT:{item['double_time_hours']}")
                hours = " ".join(hours_parts) or "N/A"

                rate = format_currency(item['hourly_rate'])
                subtotal = format_currency(item['subtotal'])

                print(f"  {task:<40} {date:<12} {time_range:<15} {hours:<15} {rate:<12} {subtotal:<12}")

        # Questions
        questions = details['questions']
        if questions:
            print_header(f"❓ CLIENT QUESTIONS ({len(questions)} questions)", char="-")

            pending = sum(1 for q in questions if q['status'] == 'pending')
            answered = sum(1 for q in questions if q['status'] == 'answered')
            ai_generated = sum(1 for q in questions if q.get('ai_generated'))

            print(f"\n  Total Questions: {len(questions)}")
            print(f"  Pending: {pending}")
            print(f"  Answered: {answered}")
            print(f"  AI-Generated Answers: {ai_generated}")

            for i, q in enumerate(questions, 1):
                status_icon = "✅" if q['status'] == 'answered' else "⏳"
                ai_icon = "🤖" if q.get('ai_generated') else ""

                print(f"\n  {status_icon} Question #{i}: {ai_icon}")
                print(f"     Q: {q['question_text'][:100]}")
                print(f"     Status: {q['status']} | Priority: {q['priority']}")
                print(f"     Asked by: {q['asked_by_name'] or 'Anonymous'} ({q['asked_by_email'] or 'N/A'})")
                print(f"     Asked at: {q['asked_at']}")

                if q['answer_text']:
                    print(f"     A: {q['answer_text'][:150]}")
                    if len(q['answer_text']) > 150:
                        print(f"        ... (answer truncated)")
                    print(f"     Answered by: {q['answered_by'] or 'Unknown'}")
                    print(f"     Answered at: {q['answered_at']}")

                if q['requires_follow_up']:
                    print(f"     ⚠️  Requires follow-up")

        print("\n" + "=" * 120 + "\n")


def export_client_report_json(engine, search_term):
    """Export client report to JSON file."""
    proposals = find_client_proposals(engine, search_term)

    if not proposals:
        return None

    client_data = {
        'client_info': {
            'name': proposals[0][2],
            'email': proposals[0][3],
            'company': proposals[0][4],
            'contact': proposals[0][5],
            'phone': proposals[0][6]
        },
        'proposals': []
    }

    for prop in proposals:
        proposal_id = prop[0]
        details = get_proposal_full_details(engine, proposal_id)

        if details:
            # Convert datetime objects to strings for JSON serialization
            proposal_data = details['proposal'].copy()
            for key, value in proposal_data.items():
                if isinstance(value, datetime):
                    proposal_data[key] = value.isoformat()
                elif value is None:
                    proposal_data[key] = None
                else:
                    proposal_data[key] = str(value)

            client_data['proposals'].append({
                'proposal': proposal_data,
                'sections_count': len(details['sections']),
                'line_items_count': len(details['all_items']),
                'timeline_events_count': len(details['timeline']),
                'labor_items_count': len(details['labor']),
                'questions_count': len(details['questions']),
                'sections': details['sections'],
                'line_items': details['all_items'],
                'timeline': details['timeline'],
                'labor': details['labor'],
                'questions': details['questions']
            })

    # Save to file
    output_dir = Path(__file__).parent / 'client_reports'
    output_dir.mkdir(exist_ok=True)

    safe_name = search_term.replace(' ', '_').replace('/', '_')
    output_file = output_dir / f"client_report_{safe_name}.json"

    with open(output_file, 'w') as f:
        json.dump(client_data, f, indent=2, default=str)

    return output_file


def main(search_term=None, database_url=None):
    """Main function."""

    if not search_term:
        print("Usage: python client_report.py <client_name_or_email_or_job_number> [database_url]")
        print("\nExamples:")
        print("  python client_report.py 'User Conference'")
        print("  python client_report.py '305342'")
        print("  python client_report.py 'shanondoah.nicholson@company.com'")
        sys.exit(1)

    # Use provided URL or fall back to settings
    db_url = database_url or settings.DATABASE_URL

    print("=" * 120)
    print("CLIENT REPORT GENERATOR")
    print("=" * 120)
    print(f"\nDatabase: {db_url.split('@')[-1] if '@' in db_url else db_url}")

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Display report
    display_client_report(engine, search_term)

    # Export to JSON
    print_header("💾 EXPORTING TO JSON", char="=")
    output_file = export_client_report_json(engine, search_term)

    if output_file:
        print(f"\n✅ Client report exported to: {output_file}\n")
    else:
        print(f"\n❌ Could not export client report\n")

    print("=" * 120)
    print("✅ REPORT COMPLETE")
    print("=" * 120)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client_report.py <client_name_or_email_or_job_number> [database_url]")
        print("\nExamples:")
        print("  python client_report.py 'User Conference'")
        print("  python client_report.py '305342'")
        print("  python client_report.py 'shanondoah.nicholson@company.com'")
        sys.exit(1)

    search = sys.argv[1]
    db_url = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        main(search, db_url)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
