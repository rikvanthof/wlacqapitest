"""Database connection and configuration"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker  # Updated import
from sqlalchemy.pool import StaticPool
import logging

logger = logging.getLogger(__name__)

# Database configuration with fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Default SQLite database for development
    db_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
    os.makedirs(db_dir, exist_ok=True)
    DATABASE_URL = f"sqlite:///{db_dir}/payment_testing.db"

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=bool(os.getenv("SQL_DEBUG", False))
    )
    print(f"🗄️ Using SQLite database: {DATABASE_URL}")
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=bool(os.getenv("SQL_DEBUG", False))
    )
    print(f"🗄️ Using PostgreSQL database")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models (updated syntax)
Base = declarative_base()

# Naming convention for constraints (helps with migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=convention)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    print("✅ Database tables created successfully")

def drop_tables():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")
    print("⚠️ All database tables dropped")

def get_database_info():
    """Get database connection information"""
    if DATABASE_URL.startswith("sqlite"):
        return {
            "type": "SQLite",
            "url": DATABASE_URL,
            "file_path": DATABASE_URL.replace("sqlite:///", "")
        }
    else:
        return {
            "type": "PostgreSQL", 
            "url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "Unknown"
        }
