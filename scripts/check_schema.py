#!/usr/bin/env python3
"""Quick script to check the proposal_sections table schema"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from app.config import settings

def main():
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)

    print("=" * 80)
    print("PROPOSAL_SECTIONS TABLE SCHEMA")
    print("=" * 80)

    columns = inspector.get_columns('proposal_sections')

    print("\nColumns:")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col.get('default') else ""
        print(f"  - {col['name']}: {col['type']} {nullable}{default}")

    print("\n" + "=" * 80)

    # Also check an existing section
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM proposal_sections
            WHERE proposal_id = 'cd8849f5-c572-48fa-ad37-d10b298056db'
            LIMIT 1
        """))

        if result.rowcount > 0:
            print("SAMPLE SECTION DATA:")
            print("=" * 80)
            row = result.fetchone()
            for key, value in zip(result.keys(), row):
                print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
