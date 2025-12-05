#!/usr/bin/env python3
"""
Database Data Explorer
----------------------
This script queries and displays actual data stored in the database tables.
Shows all records including client information, proposals, and related data.
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


def print_header(title, width=120):
    """Print a formatted header."""
    print("\n" + "=" * width)
    print(f"📊 {title}")
    print("=" * width)


def print_subheader(title, width=120):
    """Print a formatted subheader."""
    print("\n" + "-" * width)
    print(f"🔹 {title}")
    print("-" * width)


def format_value(value, max_length=50):
    """Format a value for display, truncating if too long."""
    if value is None:
        return "NULL"

    str_value = str(value)

    # Handle UUIDs
    if len(str_value) == 36 and str_value.count('-') == 4:
        return str_value[:8] + "..."

    # Truncate long strings
    if len(str_value) > max_length:
        return str_value[:max_length-3] + "..."

    return str_value


def query_table_data(engine, table_name, limit=None):
    """Query all data from a table."""
    try:
        with engine.connect() as conn:
            if limit:
                result = conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT {limit}'))
            else:
                result = conn.execute(text(f'SELECT * FROM "{table_name}"'))

            rows = result.fetchall()
            columns = result.keys()

            return columns, rows
    except Exception as e:
        print(f"Error querying {table_name}: {e}")
        return None, None


def display_table_data(engine, table_name, max_rows=100):
    """Display all data from a table."""
    print_header(f"TABLE: {table_name}")

    columns, rows = query_table_data(engine, table_name)

    if columns is None or rows is None:
        print("❌ Could not retrieve data")
        return

    print(f"Total Rows: {len(rows)}")

    if len(rows) == 0:
        print("⚠️  No data in this table")
        return

    # Display data
    print()

    # Limit number of rows displayed
    display_rows = rows[:max_rows] if len(rows) > max_rows else rows

    for idx, row in enumerate(display_rows, 1):
        print(f"\n📄 Record {idx}:")
        print("-" * 120)

        # Convert row to dict
        row_dict = dict(zip(columns, row))

        # Display each column
        for col_name, value in row_dict.items():
            formatted_value = format_value(value, max_length=80)
            print(f"  {col_name:.<30} {formatted_value}")

    if len(rows) > max_rows:
        print(f"\n... and {len(rows) - max_rows} more records (showing first {max_rows})")


def display_proposals_summary(engine):
    """Display a summary of all proposals."""
    print_header("PROPOSALS SUMMARY")

    query = text("""
        SELECT
            job_number,
            client_name,
            client_email,
            client_company,
            event_location,
            venue_name,
            start_date,
            end_date,
            status,
            total_cost,
            created_at
        FROM proposals
        ORDER BY created_at DESC
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
            columns = result.keys()

            if len(rows) == 0:
                print("⚠️  No proposals found")
                return

            print(f"Total Proposals: {len(rows)}\n")

            for idx, row in enumerate(rows, 1):
                row_dict = dict(zip(columns, row))
                print(f"\n{'='*120}")
                print(f"PROPOSAL #{idx}: {row_dict['job_number']}")
                print(f"{'='*120}")
                print(f"  Client: {row_dict['client_name']}")
                print(f"  Company: {row_dict['client_company'] or 'N/A'}")
                print(f"  Email: {row_dict['client_email'] or 'N/A'}")
                print(f"  Event: {row_dict['event_location'] or 'N/A'}")
                print(f"  Venue: {row_dict['venue_name'] or 'N/A'}")
                print(f"  Dates: {row_dict['start_date']} to {row_dict['end_date']}")
                print(f"  Status: {row_dict['status']}")
                print(f"  Total Cost: ${row_dict['total_cost']:,.2f}" if row_dict['total_cost'] else "  Total Cost: N/A")
                print(f"  Created: {row_dict['created_at']}")

    except Exception as e:
        print(f"❌ Error: {e}")


def display_proposal_details(engine, job_number):
    """Display detailed information for a specific proposal."""
    print_header(f"DETAILED VIEW: Proposal {job_number}")

    # Get proposal info
    query = text("SELECT * FROM proposals WHERE job_number = :job_number")

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"job_number": job_number})
            proposal = result.fetchone()

            if not proposal:
                print(f"❌ Proposal {job_number} not found")
                return

            columns = result.keys()
            proposal_dict = dict(zip(columns, proposal))
            proposal_id = proposal_dict['id']

            # Display proposal details
            print_subheader("PROPOSAL INFORMATION")
            for key, value in proposal_dict.items():
                if key != 'id':
                    print(f"  {key:.<35} {format_value(value, 80)}")

            # Get sections
            sections_query = text("""
                SELECT * FROM proposal_sections
                WHERE proposal_id = :proposal_id
                ORDER BY display_order
            """)
            result = conn.execute(sections_query, {"proposal_id": proposal_id})
            sections = result.fetchall()

            if sections:
                print_subheader(f"SECTIONS ({len(sections)})")
                for section in sections:
                    section_dict = dict(zip(result.keys(), section))
                    print(f"\n  Section: {section_dict['section_name']}")
                    print(f"    Type: {section_dict['section_type'] or 'N/A'}")
                    print(f"    Total: ${section_dict['section_total']:,.2f}" if section_dict['section_total'] else "    Total: N/A")

            # Get line items count
            items_query = text("""
                SELECT COUNT(*) as count, SUM(subtotal) as total
                FROM proposal_line_items
                WHERE proposal_id = :proposal_id
            """)
            result = conn.execute(items_query, {"proposal_id": proposal_id})
            items_stats = result.fetchone()

            print_subheader(f"LINE ITEMS ({items_stats[0]})")
            print(f"  Total Items: {items_stats[0]}")
            print(f"  Items Total: ${items_stats[1]:,.2f}" if items_stats[1] else "  Items Total: $0.00")

            # Get timeline count
            timeline_query = text("""
                SELECT COUNT(*) as count
                FROM proposal_timeline
                WHERE proposal_id = :proposal_id
            """)
            result = conn.execute(timeline_query, {"proposal_id": proposal_id})
            timeline_count = result.fetchone()[0]

            print_subheader(f"TIMELINE EVENTS ({timeline_count})")

            # Get labor count
            labor_query = text("""
                SELECT COUNT(*) as count, SUM(subtotal) as total
                FROM proposal_labor
                WHERE proposal_id = :proposal_id
            """)
            result = conn.execute(labor_query, {"proposal_id": proposal_id})
            labor_stats = result.fetchone()

            print_subheader(f"LABOR ITEMS ({labor_stats[0]})")
            print(f"  Total Labor Items: {labor_stats[0]}")
            print(f"  Labor Total: ${labor_stats[1]:,.2f}" if labor_stats[1] else "  Labor Total: $0.00")

            # Get questions
            questions_query = text("""
                SELECT * FROM proposal_questions
                WHERE proposal_id = :proposal_id
                ORDER BY asked_at DESC
            """)
            result = conn.execute(questions_query, {"proposal_id": proposal_id})
            questions = result.fetchall()

            if questions:
                print_subheader(f"QUESTIONS ({len(questions)})")
                for q in questions:
                    q_dict = dict(zip(result.keys(), q))
                    print(f"\n  Q: {q_dict['question_text'][:100]}")
                    print(f"     Status: {q_dict['status']} | Priority: {q_dict['priority']}")
                    print(f"     Asked by: {q_dict['asked_by_name'] or 'Unknown'} ({q_dict['asked_by_email'] or 'N/A'})")
                    if q_dict['answer_text']:
                        print(f"     A: {q_dict['answer_text'][:100]}")
                        print(f"     Answered by: {q_dict['answered_by'] or 'Unknown'}")
                        print(f"     AI Generated: {'Yes' if q_dict.get('ai_generated') else 'No'}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def display_clients_list(engine):
    """Display list of all unique clients."""
    print_header("CLIENTS LIST")

    query = text("""
        SELECT DISTINCT
            client_name,
            client_email,
            client_company,
            client_contact,
            client_phone,
            COUNT(*) as proposal_count
        FROM proposals
        GROUP BY client_name, client_email, client_company, client_contact, client_phone
        ORDER BY client_name
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            clients = result.fetchall()

            if len(clients) == 0:
                print("⚠️  No clients found")
                return

            print(f"Total Unique Clients: {len(clients)}\n")

            for idx, client in enumerate(clients, 1):
                print(f"\n{'='*120}")
                print(f"CLIENT #{idx}")
                print(f"{'='*120}")
                print(f"  Name: {client[0]}")
                print(f"  Company: {client[2] or 'N/A'}")
                print(f"  Email: {client[1] or 'N/A'}")
                print(f"  Contact: {client[3] or 'N/A'}")
                print(f"  Phone: {client[4] or 'N/A'}")
                print(f"  Number of Proposals: {client[5]}")

    except Exception as e:
        print(f"❌ Error: {e}")


def export_data_to_json(engine):
    """Export all data to JSON files."""
    print_header("EXPORTING DATA TO JSON")

    tables = [
        'pre_approved_users',
        'active_users',
        'proposals',
        'proposal_sections',
        'proposal_line_items',
        'proposal_timeline',
        'proposal_labor',
        'proposal_questions',
        'proposal_temp_links',
        'proposal_sessions'
    ]

    output_dir = Path(__file__).parent / 'data_exports'
    output_dir.mkdir(exist_ok=True)

    for table in tables:
        columns, rows = query_table_data(engine, table)

        if columns and rows:
            data = []
            for row in rows:
                row_dict = {}
                for col, value in zip(columns, row):
                    # Convert special types to strings for JSON serialization
                    if value is None:
                        row_dict[col] = None
                    elif isinstance(value, (datetime,)):
                        row_dict[col] = value.isoformat()
                    else:
                        row_dict[col] = str(value) if not isinstance(value, (int, float, bool)) else value
                data.append(row_dict)

            output_file = output_dir / f"{table}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            print(f"✅ Exported {len(data)} records from {table} to {output_file}")
        else:
            print(f"⚠️  No data to export from {table}")

    print(f"\n📁 All data exported to: {output_dir}")


def main(database_url=None):
    """Main function."""
    print("=" * 120)
    print("DATABASE DATA EXPLORER")
    print("=" * 120)
    print(f"\nConnecting to database...\n")

    # Use provided URL or fall back to settings
    db_url = database_url or settings.DATABASE_URL
    print(f"Database: {db_url.split('@')[-1] if '@' in db_url else db_url}\n")

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Display clients list
    display_clients_list(engine)

    # Display proposals summary
    display_proposals_summary(engine)

    # Get all job numbers
    with engine.connect() as conn:
        result = conn.execute(text("SELECT job_number FROM proposals ORDER BY created_at"))
        job_numbers = [row[0] for row in result.fetchall()]

    # Display detailed view for each proposal
    for job_number in job_numbers:
        display_proposal_details(engine, job_number)

    # Display users
    print_header("PRE-APPROVED USERS")
    columns, rows = query_table_data(engine, 'pre_approved_users')
    if columns and rows and len(rows) > 0:
        for idx, row in enumerate(rows, 1):
            row_dict = dict(zip(columns, row))
            print(f"\n📄 User {idx}:")
            print("-" * 120)
            for key, value in row_dict.items():
                print(f"  {key:.<30} {format_value(value, 80)}")
    else:
        print("⚠️  No pre-approved users")

    print_header("ACTIVE USERS")
    columns, rows = query_table_data(engine, 'active_users')
    if columns and rows and len(rows) > 0:
        for idx, row in enumerate(rows, 1):
            row_dict = dict(zip(columns, row))
            print(f"\n📄 User {idx}:")
            print("-" * 120)
            for key, value in row_dict.items():
                print(f"  {key:.<30} {format_value(value, 80)}")
    else:
        print("⚠️  No active users")

    # Export data
    export_data_to_json(engine)

    print("\n" + "=" * 120)
    print("✅ DATA EXPLORATION COMPLETE")
    print("=" * 120)


if __name__ == "__main__":
    try:
        # Check if custom database URL is provided as argument
        db_url = sys.argv[1] if len(sys.argv) > 1 else None
        main(db_url)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
