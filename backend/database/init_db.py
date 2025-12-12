"""
Initialize database with sample data
"""
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.database.database import init_db, get_db_session
from backend.database.crud import create_user
from loguru import logger


def create_sample_users():
    """Create sample users for testing"""
    with get_db_session() as db:
        # Admin user
        admin = create_user(
            db,
            username="admin",
            email="admin@deepvision.com",
            password="admin123",
            full_name="Admin User"
        )
        admin.is_admin = True
        db.commit()
        logger.success("Created admin user")
        
        # Demo user
        demo = create_user(
            db,
            username="demo",
            email="demo@deepvision.com",
            password="demo123",
            full_name="Demo User"
        )
        logger.success("Created demo user")
        
        return admin, demo


def main():
    """Initialize database"""
    logger.info("Starting database initialization...")
    
    # Create tables
    init_db()
    
    # Create sample users
    logger.info("Creating sample users...")
    create_sample_users()
    
    logger.success("Database initialization complete!")
    logger.info("Sample credentials:")
    logger.info("  Admin: username=admin, password=admin123")
    logger.info("  Demo:  username=demo, password=demo123")


if __name__ == "__main__":
    main()