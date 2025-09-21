# scripts/seed_proposals.py (create new file)
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.proposals import CustomerProposal
from datetime import datetime
import uuid
import json

def seed_sample_proposals():
    """Add sample customer proposals"""
    
    db = SessionLocal()
    
    sample_proposals = [
        {
            "id": str(uuid.uuid4()),
            "customer_email": "admin@company.com",
            "proposal_data": {
                "eventDetails": {
                    "jobNumber": "306780",
                    "clientName": "Internal Systems Upgrade",
                    "venue": "Company Headquarters - Main Conference Room",
                    "totalCost": 95000
                },
                "sections": [],  # Your actual proposal structure
                "totalCost": 95000
            },
            "status": "active",
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "customer_email": "client@customer.com", 
            "proposal_data": {
                "eventDetails": {
                    "jobNumber": "306781",
                    "clientName": "Customer Corp Annual Meeting",
                    "venue": "Grand Ballroom - Luxury Hotel",
                    "totalCost": 120000
                },
                "sections": [],  # Your actual proposal structure
                "totalCost": 120000
            },
            "status": "active",
            "created_by": "system"
        }
    ]
    
    for proposal_data in sample_proposals:
        # Check if proposal already exists
        existing = db.query(CustomerProposal).filter(
            CustomerProposal.customer_email == proposal_data["customer_email"]
        ).first()
        
        if not existing:
            proposal = CustomerProposal(**proposal_data)
            db.add(proposal)
            print(f"Added proposal for: {proposal_data['customer_email']}")
        else:
            print(f"Proposal already exists for: {proposal_data['customer_email']}")
    
    db.commit()
    db.close()
    print("Sample proposals seeded successfully")

if __name__ == "__main__":
    seed_sample_proposals()