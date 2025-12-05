#!/usr/bin/env python3
"""
Database Schema Explorer
------------------------
This script queries the database to display all tables and their columns with detailed information.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import reflection
from app.config import settings
import json


def get_database_info(engine):
    """Get basic database information."""
    with engine.connect() as conn:
        if 'postgresql' in str(engine.url):
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            db_size_result = conn.execute(text("SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database WHERE datname = current_database()"))
            db_info = db_size_result.fetchone()
            return {
                'type': 'PostgreSQL',
                'version': version,
                'database': db_info[0] if db_info else 'N/A',
                'size': db_info[1] if db_info else 'N/A'
            }
        else:
            return {
                'type': 'SQLite',
                'version': 'N/A',
                'database': str(engine.url.database),
                'size': 'N/A'
            }


def get_table_row_count(engine, table_name):
    """Get the number of rows in a table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            return result.scalar()
    except Exception as e:
        return f"Error: {str(e)}"


def get_foreign_keys(inspector, table_name):
    """Get foreign key information for a table."""
    try:
        fks = inspector.get_foreign_keys(table_name)
        return fks
    except Exception:
        return []


def get_indexes(inspector, table_name):
    """Get index information for a table."""
    try:
        indexes = inspector.get_indexes(table_name)
        return indexes
    except Exception:
        return []


def get_table_comment(inspector, table_name):
    """Get table comment if available."""
    try:
        return inspector.get_table_comment(table_name).get('text', '')
    except Exception:
        return ''


def explore_database(database_url=None):
    """Main function to explore database schema."""

    # Use provided URL or fall back to settings
    db_url = database_url or settings.DATABASE_URL

    print("=" * 100)
    print("DATABASE SCHEMA EXPLORER")
    print("=" * 100)
    print(f"\nConnecting to: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print()

    # Create engine and inspector
    engine = create_engine(db_url, echo=False)
    inspector = inspect(engine)

    # Get database info
    print("📊 DATABASE INFORMATION")
    print("-" * 100)
    db_info = get_database_info(engine)
    for key, value in db_info.items():
        print(f"  {key.capitalize()}: {value}")
    print()

    # Get all table names
    table_names = inspector.get_table_names()

    if not table_names:
        print("⚠️  No tables found in the database.")
        return

    print(f"📋 TABLES FOUND: {len(table_names)}")
    print("-" * 100)
    for i, table in enumerate(table_names, 1):
        print(f"  {i}. {table}")
    print()

    # Iterate through each table
    for table_name in sorted(table_names):
        print("=" * 100)
        print(f"📁 TABLE: {table_name}")
        print("=" * 100)

        # Get table comment
        comment = get_table_comment(inspector, table_name)
        if comment:
            print(f"Description: {comment}")
            print()

        # Get row count
        row_count = get_table_row_count(engine, table_name)
        print(f"Row Count: {row_count}")
        print()

        # Get columns
        columns = inspector.get_columns(table_name)
        print(f"🔹 COLUMNS ({len(columns)}):")
        print("-" * 100)

        # Print column headers
        print(f"{'#':<4} {'Column Name':<30} {'Type':<25} {'Nullable':<10} {'Default':<20} {'Primary Key':<12}")
        print("-" * 100)

        # Get primary keys
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get('constrained_columns', []) if pk_constraint else []

        # Print each column
        for i, col in enumerate(columns, 1):
            col_name = col['name']
            col_type = str(col['type'])
            nullable = 'Yes' if col['nullable'] else 'No'
            default = str(col['default'])[:20] if col['default'] else '-'
            is_pk = 'Yes' if col_name in primary_keys else 'No'

            print(f"{i:<4} {col_name:<30} {col_type:<25} {nullable:<10} {default:<20} {is_pk:<12}")

        print()

        # Get and display foreign keys
        foreign_keys = get_foreign_keys(inspector, table_name)
        if foreign_keys:
            print(f"🔗 FOREIGN KEYS ({len(foreign_keys)}):")
            print("-" * 100)
            for fk in foreign_keys:
                constrained_cols = ', '.join(fk['constrained_columns'])
                referred_table = fk['referred_table']
                referred_cols = ', '.join(fk['referred_columns'])
                print(f"  • {constrained_cols} → {referred_table}({referred_cols})")
            print()

        # Get and display indexes
        indexes = get_indexes(inspector, table_name)
        if indexes:
            print(f"🔍 INDEXES ({len(indexes)}):")
            print("-" * 100)
            for idx in indexes:
                idx_name = idx['name']
                idx_cols = ', '.join(idx['column_names'])
                unique = 'UNIQUE' if idx['unique'] else 'NON-UNIQUE'
                print(f"  • {idx_name}: ({idx_cols}) [{unique}]")
            print()

        print()

    # Summary
    print("=" * 100)
    print("📈 SUMMARY")
    print("=" * 100)
    print(f"Total Tables: {len(table_names)}")

    total_columns = sum(len(inspector.get_columns(table)) for table in table_names)
    print(f"Total Columns: {total_columns}")

    total_rows = sum(
        count for count in
        (get_table_row_count(engine, table) for table in table_names)
        if isinstance(count, int)
    )
    print(f"Total Rows: {total_rows}")
    print()

    # Export schema to JSON
    print("💾 Exporting schema to JSON...")
    schema_export = export_schema_to_json(inspector, engine, table_names)
    output_file = Path(__file__).parent / 'database_schema.json'
    with open(output_file, 'w') as f:
        json.dump(schema_export, f, indent=2, default=str)
    print(f"✅ Schema exported to: {output_file}")
    print()


def export_schema_to_json(inspector, engine, table_names):
    """Export the database schema to a JSON structure."""
    schema = {
        'database_info': get_database_info(engine),
        'tables': {}
    }

    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get('constrained_columns', []) if pk_constraint else []
        foreign_keys = get_foreign_keys(inspector, table_name)
        indexes = get_indexes(inspector, table_name)
        row_count = get_table_row_count(engine, table_name)

        schema['tables'][table_name] = {
            'row_count': row_count if isinstance(row_count, int) else 0,
            'comment': get_table_comment(inspector, table_name),
            'columns': [
                {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'default': str(col['default']) if col['default'] else None,
                    'primary_key': col['name'] in primary_keys
                }
                for col in columns
            ],
            'primary_keys': primary_keys,
            'foreign_keys': [
                {
                    'constrained_columns': fk['constrained_columns'],
                    'referred_table': fk['referred_table'],
                    'referred_columns': fk['referred_columns']
                }
                for fk in foreign_keys
            ],
            'indexes': [
                {
                    'name': idx['name'],
                    'columns': idx['column_names'],
                    'unique': idx['unique']
                }
                for idx in indexes
            ]
        }

    return schema


if __name__ == "__main__":
    try:
        # Check if custom database URL is provided as argument
        db_url = sys.argv[1] if len(sys.argv) > 1 else None
        explore_database(db_url)
    except Exception as e:
        print(f"❌ Error exploring database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
