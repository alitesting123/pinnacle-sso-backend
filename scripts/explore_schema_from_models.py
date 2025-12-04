#!/usr/bin/env python3
"""
Database Schema Explorer - From ORM Models
-------------------------------------------
This script explores database schema by reading SQLAlchemy ORM models.
Works even when the database is empty or not initialized.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import DeclarativeMeta
import json


def get_all_models():
    """Import all models from the app."""
    models = []

    # Import user models
    try:
        from app.models.users import Base as UsersBase, PreApprovedUser, User
        models.extend([PreApprovedUser, User])
        print(f"✓ Loaded user models from: app/models/users.py")
    except Exception as e:
        print(f"✗ Could not load user models: {e}")

    # Import proposal models
    try:
        from app.models.proposals import (
            Base as ProposalsBase,
            Proposal,
            ProposalSection,
            ProposalLineItem,
            ProposalTimeline,
            ProposalLabor,
            ProposalQuestion,
            SecureProposalLink,
            ProposalSession
        )
        models.extend([
            Proposal,
            ProposalSection,
            ProposalLineItem,
            ProposalTimeline,
            ProposalLabor,
            ProposalQuestion,
            SecureProposalLink,
            ProposalSession
        ])
        print(f"✓ Loaded proposal models from: app/models/proposals.py")
    except Exception as e:
        print(f"✗ Could not load proposal models: {e}")

    return models


def analyze_model(model_class):
    """Analyze a SQLAlchemy model and extract schema information."""

    # Get the table name
    table_name = model_class.__tablename__

    # Get the mapper for this model
    mapper = inspect(model_class)

    # Extract column information
    columns = []
    primary_keys = []

    for col in mapper.columns:
        col_info = {
            'name': col.name,
            'type': str(col.type),
            'nullable': col.nullable,
            'primary_key': col.primary_key,
            'foreign_key': bool(col.foreign_keys),
            'default': str(col.default.arg) if col.default and hasattr(col.default, 'arg') else None,
            'server_default': str(col.server_default.arg) if col.server_default and hasattr(col.server_default, 'arg') else None,
        }

        # Get foreign key information
        if col.foreign_keys:
            fk = list(col.foreign_keys)[0]
            col_info['references'] = f"{fk.column.table.name}.{fk.column.name}"

        columns.append(col_info)

        if col.primary_key:
            primary_keys.append(col.name)

    # Extract relationship information
    relationships = []
    for rel in mapper.relationships:
        rel_info = {
            'name': rel.key,
            'target': rel.entity.class_.__name__,
            'direction': rel.direction.name,
            'uselist': rel.uselist,
        }
        relationships.append(rel_info)

    return {
        'table_name': table_name,
        'columns': columns,
        'primary_keys': primary_keys,
        'relationships': relationships,
        'doc': model_class.__doc__
    }


def display_schema():
    """Display the database schema from ORM models."""

    print("=" * 100)
    print("DATABASE SCHEMA FROM ORM MODELS")
    print("=" * 100)
    print()

    # Get all models
    print("📦 Loading SQLAlchemy Models...")
    print("-" * 100)
    models = get_all_models()
    print()

    if not models:
        print("⚠️  No models found!")
        return

    print(f"📋 MODELS FOUND: {len(models)}")
    print("-" * 100)
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model.__tablename__} ({model.__name__})")
    print()
    print()

    # Analyze each model
    schema_data = {}

    for model in models:
        print("=" * 100)
        model_info = analyze_model(model)
        table_name = model_info['table_name']
        schema_data[table_name] = model_info

        print(f"📁 TABLE: {table_name}")
        print(f"   Model Class: {model.__name__}")
        if model_info['doc']:
            print(f"   Description: {model_info['doc'].strip()}")
        print("=" * 100)
        print()

        # Display columns
        columns = model_info['columns']
        print(f"🔹 COLUMNS ({len(columns)}):")
        print("-" * 100)
        print(f"{'#':<4} {'Column Name':<30} {'Type':<30} {'Null':<6} {'PK':<4} {'FK':<4} {'Default':<20}")
        print("-" * 100)

        for i, col in enumerate(columns, 1):
            col_name = col['name']
            col_type = col['type'][:28] if len(col['type']) <= 30 else col['type'][:27] + "..."
            nullable = 'Yes' if col['nullable'] else 'No'
            is_pk = 'Yes' if col['primary_key'] else '-'
            is_fk = 'Yes' if col['foreign_key'] else '-'
            default = (col['default'] or col['server_default'] or '-')[:20]

            print(f"{i:<4} {col_name:<30} {col_type:<30} {nullable:<6} {is_pk:<4} {is_fk:<4} {default:<20}")

            # Show foreign key reference
            if 'references' in col:
                print(f"     → References: {col['references']}")

        print()

        # Display primary keys
        if model_info['primary_keys']:
            print(f"🔑 PRIMARY KEY(S): {', '.join(model_info['primary_keys'])}")
            print()

        # Display relationships
        if model_info['relationships']:
            print(f"🔗 RELATIONSHIPS ({len(model_info['relationships'])}):")
            print("-" * 100)
            for rel in model_info['relationships']:
                direction = rel['direction']
                target = rel['target']
                name = rel['name']
                rel_type = "One-to-Many" if rel['uselist'] else "Many-to-One"
                print(f"  • {name}: {rel_type} → {target} [{direction}]")
            print()

        print()

    # Summary
    print("=" * 100)
    print("📈 SUMMARY")
    print("=" * 100)
    print(f"Total Tables: {len(schema_data)}")

    total_columns = sum(len(info['columns']) for info in schema_data.values())
    print(f"Total Columns: {total_columns}")

    total_relationships = sum(len(info['relationships']) for info in schema_data.values())
    print(f"Total Relationships: {total_relationships}")
    print()

    # Export to JSON
    print("💾 Exporting schema to JSON...")
    output_file = Path(__file__).parent / 'database_schema_from_models.json'
    with open(output_file, 'w') as f:
        json.dump(schema_data, f, indent=2, default=str)
    print(f"✅ Schema exported to: {output_file}")
    print()

    # Also display a simplified table reference
    print("=" * 100)
    print("📊 TABLE RELATIONSHIP DIAGRAM")
    print("=" * 100)
    print()

    print("USER TABLES:")
    print("  • pre_approved_users - Pre-approved users managed by admin")
    print("  • active_users - Active user sessions")
    print()

    print("PROPOSAL TABLES:")
    print("  • proposals (parent)")
    print("    ├── proposal_sections")
    print("    │   └── proposal_line_items")
    print("    ├── proposal_timeline")
    print("    ├── proposal_labor")
    print("    ├── proposal_questions")
    print("    ├── proposal_temp_links")
    print("    └── proposal_sessions")
    print()


if __name__ == "__main__":
    try:
        display_schema()
    except Exception as e:
        print(f"❌ Error exploring schema: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
