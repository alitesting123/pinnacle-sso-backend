# scripts/test_connection.py
import sys
from pathlib import Path
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test Supabase connection"""
    
    # Check for DATABASE_URL in environment first
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        # Try loading from config
        from app.config import settings
        db_url = settings.DATABASE_URL
    
    logger.info(f"DATABASE_URL source: {'Environment Variable' if os.getenv('DATABASE_URL') else 'Config File'}")
    logger.info(f"Database type: {'PostgreSQL' if 'postgresql' in db_url else 'SQLite'}")
    logger.info(f"Connection string: {db_url[:40]}...")
    
    if 'postgresql' not in db_url:
        logger.error("\nERROR: Still using SQLite!")
        logger.error("DATABASE_URL is not set correctly")
        logger.error(f"\nFull path: {db_url}")
        return False
    
    try:
        logger.info("\nTesting connection to Supabase...")
        
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            
            logger.info(f"\nSUCCESS! Connected to Supabase PostgreSQL")
            logger.info(f"Version: {version[:80]}...")
            
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            logger.info(f"Database: {db_name}")
            
            return True
            
    except Exception as e:
        logger.error(f"\nConnection failed!")
        logger.error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()