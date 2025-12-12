"""
Migration script to add chat_sessions table
Run this once to update the database schema
"""
from sqlalchemy import create_engine, inspect
from backend.database.models import Base, ChatSession
from backend.database.database import DATABASE_URL, engine as db_engine
from loguru import logger

def add_chat_sessions_table():
    """Add chat_sessions table to database"""
    try:
        # Use the existing engine from database module
        engine = db_engine
        
        # Check if table exists
        inspector = inspect(engine)
        if 'chat_sessions' in inspector.get_table_names():
            logger.info("chat_sessions table already exists")
            return
        
        # Create only the chat_sessions table
        ChatSession.__table__.create(bind=engine)
        logger.info("Successfully created chat_sessions table")
        
    except Exception as e:
        logger.error(f"Failed to create chat_sessions table: {e}")
        raise

if __name__ == "__main__":
    logger.info("Adding chat_sessions table to database...")
    add_chat_sessions_table()
    logger.info("Migration completed!")
