from app.database import engine, Base
from app.models import Module, Comment
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize database tables.
    Drops existing tables and recreates them.
    WARNING: This deletes all data!
    """
    logger.info("Initializing database...")
    
    # Drop all tables
    logger.info("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Database initialized successfully!")
    logger.info("Tables created: modules, comments")

if __name__ == "__main__":
    confirm = input("⚠️  WARNING: This will DELETE all existing data. Continue? (y/n): ")
    if confirm.lower() == 'y':
        init_database()
    else:
        logger.info("Aborted.")