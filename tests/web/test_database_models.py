# tests/web/test_database_models.py
"""Test database models and basic operations"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime, timedelta

from src.web.models import Base, ChainState, TestExecution, TestResultEnhanced

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

class TestChainStateModel:
    def test_create_chain_state(self, db_session):
        """Test creating a new chain state"""
        chain_id = f"test_chain_{uuid.uuid4()}"
        execution_id = f"exec_{uuid.uuid4()}"
        
        chain_state = ChainState.create_new(
            chain_id=chain_id,
            execution_id=execution_id,
            chain_config={"test": "config"},
            created_by="test_user"
        )
        
        db_session.add(chain_state)
        db_session.commit()
        
        # Verify saved correctly
        saved_state = db_session.query(ChainState).filter_by(chain_id=chain_id).first()
        assert saved_state is not None
        assert saved_state.execution_id == execution_id
        assert saved_state.status == 'active'
        assert saved_state.current_step_index == 0
        assert saved_state.previous_outputs == {}
    
    def test_update_chain_step(self, db_session):
        """Test updating chain step and outputs"""
        chain_state = ChainState.create_new(
            chain_id="test_chain",
            execution_id="test_exec",
            chain_config={}
        )
        db_session.add(chain_state)
        db_session.commit()
        
        # Update step
        outputs = {"payment_id": "pay_123", "scheme_transaction_id": "scheme_456"}
        chain_state.update_step(1, outputs)
        db_session.commit()
        
        # Verify update
        updated_state = db_session.query(ChainState).filter_by(chain_id="test_chain").first()
        assert updated_state.current_step_index == 1
        assert updated_state.previous_outputs["payment_id"] == "pay_123"
        assert updated_state.previous_outputs["scheme_transaction_id"] == "scheme_456"
    
    def test_schedule_chain(self, db_session):
        """Test scheduling chain for later execution"""
        chain_state = ChainState.create_new(
            chain_id="scheduled_chain",
            execution_id="scheduled_exec",
            chain_config={}
        )
        db_session.add(chain_state)
        db_session.commit()
        
        # Schedule for tomorrow
        future_time = datetime.now() + timedelta(days=1)
        chain_state.schedule_for_later(future_time, delay_seconds=300)
        db_session.commit()
        
        # Verify scheduling
        scheduled_state = db_session.query(ChainState).filter_by(chain_id="scheduled_chain").first()
        assert scheduled_state.status == 'scheduled'
        assert scheduled_state.scheduled_for is not None
        assert scheduled_state.delay_seconds == 300

class TestTestExecutionModel:
    def test_create_test_execution(self, db_session):
        """Test creating a test execution"""
        execution_id = f"exec_{uuid.uuid4()}"
        
        execution = TestExecution(
            execution_id=execution_id,
            name="Test Execution",
            description="Test description",
            test_file_path="/path/to/test.csv",
            execution_config={"threads": 3, "tags": ["smoke"]},
            created_by="test_user"
        )
        
        db_session.add(execution)
        db_session.commit()
        
        # Verify saved correctly
        saved_execution = db_session.query(TestExecution).filter_by(execution_id=execution_id).first()
        assert saved_execution is not None
        assert saved_execution.name == "Test Execution"
        assert saved_execution.status == 'running'
        assert saved_execution.execution_config["threads"] == 3
    
    def test_update_execution_statistics(self, db_session):
        """Test updating execution statistics"""
        execution = TestExecution(
            execution_id="stats_test",
            name="Statistics Test",
            test_file_path="/path/to/test.csv"
        )
        db_session.add(execution)
        db_session.commit()
        
        # Update statistics
        execution.update_statistics(step_passed=True)
        execution.update_statistics(step_failed=True)
        execution.update_statistics(chain_completed=True)
        db_session.commit()
        
        # Verify statistics
        updated_execution = db_session.query(TestExecution).filter_by(execution_id="stats_test").first()
        assert updated_execution.passed_steps == 1
        assert updated_execution.failed_steps == 1
        assert updated_execution.completed_chains == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])