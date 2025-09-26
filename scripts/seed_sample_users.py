# scripts/seed_sample_users.py
"""Seed realistic pre-approved users for testing"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.users import PreApprovedUser
from datetime import datetime, timedelta
import uuid

def seed_sample_users():
    """Add realistic pre-approved users"""
    
    db = SessionLocal()
    
    sample_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "lisa.chen@microsoft.com",
            "full_name": "Lisa Chen",
            "company": "Microsoft Corporation",
            "department": "Corporate Events",
            "roles": ["client"],
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(days=15)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "michael.rodriguez@apple.com",
            "full_name": "Michael Rodriguez",
            "company": "Apple Inc.",
            "department": "Marketing",
            "roles": ["client", "vip"],
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(days=12)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "sarah.martinez@pinnaclelive.com",
            "full_name": "Sarah Martinez",
            "company": "Pinnacle Live",
            "department": "Sales",
            "roles": ["admin", "manager", "user"],
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(days=30)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "test.client@example.com",
            "full_name": "Test Client",
            "company": "Example Corp",
            "department": "Events",
            "roles": ["client"],
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(days=1)
        }
    ]
    
    added_count = 0
    existing_count = 0
    
    for user_data in sample_users:
        existing = db.query(PreApprovedUser).filter(
            PreApprovedUser.email == user_data["email"]
        ).first()
        
        if not existing:
            user = PreApprovedUser(**user_data)
            db.add(user)
            print(f"Added: {user_data['full_name']} ({user_data['email']})")
            added_count += 1
        else:
            print(f"Exists: {user_data['email']}")
            existing_count += 1
    
    db.commit()
    db.close()
    print(f"\nSummary: Added {added_count} new users, {existing_count} already existed")

if __name__ == "__main__":
    seed_sample_users()