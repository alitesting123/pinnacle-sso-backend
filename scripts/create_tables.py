# scripts/create_tables.py
"""Create database tables"""

from app.database import engine, init_database
from app.models.users import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
        
        # Print table info
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Created tables: {tables}")
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()