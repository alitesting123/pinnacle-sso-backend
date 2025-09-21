# scripts/seed_sample_users.py
"""Seed sample pre-approved users for testing"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.users import PreApprovedUser
from datetime import datetime
import uuid

def seed_sample_users():
    """Add sample pre-approved users"""
    
    db = SessionLocal()
    
    sample_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "admin@company.com",
            "full_name": "System Administrator",
            "company": "Your Company",
            "department": "IT",
            "roles": ["admin", "manager", "user"],
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "manager@company.com",
            "full_name": "Event Manager",
            "company": "Your Company",
            "department": "Events",
            "roles": ["manager", "user"],
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "user@company.com",
            "full_name": "Regular User",
            "company": "Your Company",
            "department": "Sales",
            "roles": ["user"],
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "client@customer.com",
            "full_name": "Client User",
            "company": "Customer Corp",
            "department": "Marketing",
            "roles": ["user"],
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    for user_data in sample_users:
        # Check if user already exists
        existing = db.query(PreApprovedUser).filter(
            PreApprovedUser.email == user_data["email"]
        ).first()
        
        if not existing:
            user = PreApprovedUser(**user_data)
            db.add(user)
            print(f"Added pre-approved user: {user_data['email']}")
        else:
            print(f"User already exists: {user_data['email']}")
    
    db.commit()
    db.close()
    print("Sample users seeded successfully")

if __name__ == "__main__":
    seed_sample_users()