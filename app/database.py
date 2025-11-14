# app/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
import logging
import sys

logger = logging.getLogger(__name__)

# Create database engine
try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 10,
            # Add SSL config for PostgreSQL cloud providers if needed
            **({"sslmode": "require"} if "postgresql" in settings.DATABASE_URL and "sslmode" not in settings.DATABASE_URL else {})
        } if "postgresql" in settings.DATABASE_URL else {}
    )
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    logger.error("💡 Please check your DATABASE_URL in the .env file")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection():
    """Test database connection before initializing tables"""
    try:
        with engine.connect() as conn:
            # Simple query to test connection
            if "postgresql" in settings.DATABASE_URL:
                conn.execute(text("SELECT 1"))
            else:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error("")
        logger.error("=" * 80)
        logger.error("DATABASE CONNECTION ERROR - TROUBLESHOOTING GUIDE")
        logger.error("=" * 80)

        if "Tenant or user not found" in str(e):
            logger.error("🔍 Error: 'Tenant or user not found'")
            logger.error("")
            logger.error("This error typically occurs with cloud PostgreSQL providers (Neon, Supabase, etc.)")
            logger.error("")
            logger.error("Common causes:")
            logger.error("  1. Database credentials are incorrect")
            logger.error("  2. Database instance/project was deleted")
            logger.error("  3. Database URL format is incorrect")
            logger.error("  4. Your IP address is not allowed (check firewall settings)")
            logger.error("")
            logger.error("Solutions:")
            logger.error("  1. Verify your DATABASE_URL in the .env file")
            logger.error("  2. Check your database provider dashboard for correct credentials")
            logger.error("  3. For local development, consider using SQLite:")
            logger.error("     DATABASE_URL=sqlite:///./proposal_portal.db")
            logger.error("")
            logger.error("Expected PostgreSQL URL format:")
            logger.error("  postgresql://username:password@host:port/database?sslmode=require")
            logger.error("")
        else:
            logger.error(f"🔍 Error: {type(e).__name__}")
            logger.error("")
            logger.error("Common solutions:")
            logger.error("  1. Check if your database server is running")
            logger.error("  2. Verify DATABASE_URL in your .env file")
            logger.error("  3. For local development, use SQLite:")
            logger.error("     DATABASE_URL=sqlite:///./proposal_portal.db")
            logger.error("  4. Check .env.example for configuration examples")
            logger.error("")

        logger.error("=" * 80)
        return False

def init_database():
    """Initialize database tables"""
    from app.models.users import Base

    # Test connection first
    if not test_database_connection():
        logger.error("❌ Cannot initialize database - connection test failed")
        logger.error("💡 Please fix the database connection issue and restart the application")
        raise RuntimeError("Database connection failed. Check the logs above for troubleshooting steps.")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise