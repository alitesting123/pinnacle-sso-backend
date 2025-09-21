# scripts/create_proposal_tables.py (create new file)
from app.database import engine
from app.models.proposals import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_proposal_tables():
    """Create proposal-related database tables"""
    try:
        logger.info("Creating proposal tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Proposal tables created successfully")
        
        # Print table info
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        proposal_tables = [t for t in tables if 'proposal' in t]
        logger.info(f"Created proposal tables: {proposal_tables}")
        
    except Exception as e:
        logger.error(f"Failed to create proposal tables: {e}")
        raise

if __name__ == "__main__":
    create_proposal_tables()