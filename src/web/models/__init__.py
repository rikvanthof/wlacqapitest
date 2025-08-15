"""Database models package"""

# Import Base and database utilities first
from .database import Base, engine, SessionLocal, get_db, create_tables, drop_tables

# Import ALL models to ensure they're registered with SQLAlchemy
from .chain_state import ChainState
from .test_execution import TestExecution

# Make sure all models are registered by accessing their metadata
def _ensure_models_registered():
    """Ensure all models are registered with SQLAlchemy"""
    # This forces SQLAlchemy to see all model classes
    models = [ChainState, TestExecution]
    for model in models:
        # Access the table to ensure it's registered
        _ = model.__table__
    print(f"🔧 Registered {len(models)} model(s) with SQLAlchemy")

# Call it when the module is imported
_ensure_models_registered()

__all__ = [
    'Base',
    'engine', 
    'SessionLocal',
    'get_db',
    'create_tables',
    'drop_tables',
    'ChainState',
    'TestExecution'
]

def init_database():
    """Initialize database with all tables"""
    print("🔧 Creating all database tables...")
    create_tables()
    print("✅ Database initialized with all tables")

if __name__ == "__main__":
    init_database()
