"""
Example setup script Ä‘á»ƒ initialize database schema

Cháº¡y: python setup_db.py
"""

from sqlalchemy import create_engine
from app.config import settings
from app.database import Base

def init_db():
    """Initialize database tables"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL, echo=True)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        print("OK Database initialized successfully!")
        print(f"   Database: {settings.DATABASE_URL}")
        
    except Exception as e:
        print(f"ERROR initializing database: {e}")
        raise


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    try:
        engine = create_engine(settings.DATABASE_URL, echo=True)
        Base.metadata.drop_all(bind=engine)
        print("OK All tables dropped successfully!")
        
    except Exception as e:
        print(f"ERROR dropping tables: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == "yes":
            drop_all_tables()
        else:
            print("Aborted.")
    else:
        init_db()
