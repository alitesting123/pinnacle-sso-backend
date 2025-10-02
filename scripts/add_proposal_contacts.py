# scripts/add_proposal_contacts.py
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.users import PreApprovedUser
from datetime import datetime
import uuid

def add_contacts():
    db = SessionLocal()
    
    users = [
        # Contact for proposal 302798 (I Institute)
        {
            "id": str(uuid.uuid4()),
            "email": "amadison@iinstitute.com",
            "full_name": "Aimee Madison",
            "company": "I Institute",
            "department": "Events",
            "roles": ["client"],
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        # Contact for proposal 305342 (User Conference)
        {
            "id": str(uuid.uuid4()),
            "email": "shanondoah.nicholson@HRJC.com",
            "full_name": "Shanandoah Nicholson",
            "company": "User Conference Client",
            "department": "Events",
            "roles": ["client"],
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        # Additional test userr
    ]
    
    added_count = 0
    existing_count = 0
    
    for user_data in users:
        existing = db.query(PreApprovedUser).filter(
            PreApprovedUser.email == user_data["email"]
        ).first()
        
        if not existing:
            user = PreApprovedUser(**user_data)
            db.add(user)
            print(f"✓ Added: {user_data['full_name']} ({user_data['email']})")
            added_count += 1
        else:
            print(f"- Already exists: {user_data['email']}")
            existing_count += 1
    
    db.commit()
    db.close()
    print(f"\n✅ Summary: Added {added_count} new users, {existing_count} already existed")

if __name__ == "__main__":
    add_contacts()