"""Comprehensive database functionality test"""

import sys
import os
import unittest
from unittest import TestCase
from datetime import datetime, timedelta

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..', 'src')
sys.path.insert(0, src_dir)

class TestDatabaseFoundation(TestCase):
    def setUp(self):
        """Setup test database"""
        from web.models.database import create_tables, SessionLocal, engine
        from web.models import Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
    
    def tearDown(self):
        """Cleanup test database"""
        from web.models import Base
        from web.models.database import engine
        
        self.db.close()
        Base.metadata.drop_all(bind=engine)
    
    def test_chain_state_lifecycle(self):
        """Test complete chain state lifecycle"""
        from web.models.chain_state import ChainState
        import uuid
        
        chain_id = f"lifecycle_{uuid.uuid4().hex[:8]}"
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        # 1. Create new chain state
        chain_state = ChainState.create_new(
            chain_id=chain_id,
            execution_id=execution_id,
            chain_config={"environment": "test", "threads": 1},
            created_by="test_user"
        )
        
        self.assertEqual(chain_state.status, 'active')
        self.assertEqual(chain_state.current_step_index, 0)
        self.assertEqual(chain_state.previous_outputs, {})
        
        self.db.add(chain_state)
        self.db.commit()
        
        # 2. Update step with outputs
        step1_outputs = {"payment_id": "pay_123", "transaction_id": "txn_456"}
        chain_state.update_step(1, step1_outputs)
        self.db.commit()
        
        # Verify step update
        updated_chain = self.db.query(ChainState).filter_by(chain_id=chain_id).first()
        self.assertEqual(updated_chain.current_step_index, 1)
        self.assertEqual(updated_chain.previous_outputs["payment_id"], "pay_123")
        self.assertEqual(updated_chain.previous_outputs["transaction_id"], "txn_456")
        
        # 3. Add more outputs
        step2_outputs = {"capture_id": "cap_789", "scheme_transaction_id": "scheme_abc"}
        chain_state.update_step(2, step2_outputs)
        self.db.commit()
        
        # Verify accumulated outputs
        updated_chain = self.db.query(ChainState).filter_by(chain_id=chain_id).first()
        self.assertEqual(updated_chain.current_step_index, 2)
        self.assertEqual(len(updated_chain.previous_outputs), 4)  # All 4 outputs
        self.assertIn("payment_id", updated_chain.previous_outputs)
        self.assertIn("capture_id", updated_chain.previous_outputs)
        
        # 4. Schedule for later
        future_time = datetime.now() + timedelta(hours=2)
        chain_state.schedule_for_later(future_time, delay_seconds=600)
        self.db.commit()
        
        # Verify scheduling
        scheduled_chain = self.db.query(ChainState).filter_by(chain_id=chain_id).first()
        self.assertEqual(scheduled_chain.status, 'scheduled')
        self.assertIsNotNone(scheduled_chain.scheduled_for)
        self.assertEqual(scheduled_chain.delay_seconds, 600)
        
        # 5. Mark as completed
        chain_state.mark_completed()
        self.db.commit()
        
        # Verify completion
        completed_chain = self.db.query(ChainState).filter_by(chain_id=chain_id).first()
        self.assertEqual(completed_chain.status, 'completed')
        
        # 6. Test failure scenario
        chain_state.mark_failed("Test error message")
        self.db.commit()
        
        # Verify failure
        failed_chain = self.db.query(ChainState).filter_by(chain_id=chain_id).first()
        self.assertEqual(failed_chain.status, 'failed')
        self.assertEqual(failed_chain.error_message, "Test error message")
    
    def test_test_execution_functionality(self):
        """Test test execution tracking"""
        from web.models.test_execution import TestExecution
        import uuid
        
        execution_id = f"test_exec_{uuid.uuid4().hex[:8]}"
        
        # Create execution
        execution = TestExecution(
            execution_id=execution_id,
            name="Comprehensive Test",
            description="Testing all functionality",
            test_file_path="/path/to/comprehensive_test.csv",
            execution_config={
                "threads": 4,
                "tags": ["comprehensive", "test"],
                "environment": "test"
            },
            created_by="test_suite"
        )
        
        self.db.add(execution)
        self.db.commit()
        
        # Test statistics updates
        execution.update_statistics(step_passed=True)
        execution.update_statistics(step_passed=True)
        execution.update_statistics(step_failed=True)
        execution.update_statistics(chain_completed=True)
        execution.update_statistics(chain_failed=True)
        
        self.db.commit()
        
        # Verify statistics
        updated_execution = self.db.query(TestExecution).filter_by(execution_id=execution_id).first()
        self.assertEqual(updated_execution.passed_steps, 2)
        self.assertEqual(updated_execution.failed_steps, 1)
        self.assertEqual(updated_execution.completed_chains, 1)
        self.assertEqual(updated_execution.failed_chains, 1)
        
        # Test completion
        execution.mark_completed()
        self.db.commit()
        
        completed_execution = self.db.query(TestExecution).filter_by(execution_id=execution_id).first()
        self.assertEqual(completed_execution.status, 'completed')
        self.assertIsNotNone(completed_execution.completed_at)
    
    def test_database_queries(self):
        """Test various database queries"""
        from web.models.chain_state import ChainState
        from web.models.test_execution import TestExecution
        import uuid
        
        # Create test data
        execution_id = f"query_test_{uuid.uuid4().hex[:8]}"
        execution = TestExecution(
            execution_id=execution_id,
            name="Query Test",
            test_file_path="/test.csv"
        )
        self.db.add(execution)
        
        # Create multiple chain states
        chain_ids = []
        for i in range(3):
            chain_id = f"query_chain_{i}_{uuid.uuid4().hex[:6]}"
            chain_ids.append(chain_id)
            
            chain_state = ChainState.create_new(
                chain_id=chain_id,
                execution_id=execution_id,
                chain_config={"test_index": i}
            )
            
            if i == 0:
                chain_state.status = 'active'
            elif i == 1:
                chain_state.status = 'scheduled'
                chain_state.scheduled_for = datetime.now() + timedelta(hours=1)
            else:
                chain_state.status = 'completed'
            
            self.db.add(chain_state)
        
        self.db.commit()
        
        # Test queries
        
        # 1. Query by execution
        execution_chains = self.db.query(ChainState).filter_by(execution_id=execution_id).all()
        self.assertEqual(len(execution_chains), 3)
        
        # 2. Query by status
        active_chains = self.db.query(ChainState).filter_by(status='active').all()
        scheduled_chains = self.db.query(ChainState).filter_by(status='scheduled').all()
        completed_chains = self.db.query(ChainState).filter_by(status='completed').all()
        
        self.assertEqual(len(active_chains), 1)
        self.assertEqual(len(scheduled_chains), 1)
        self.assertEqual(len(completed_chains), 1)
        
        # 3. Query scheduled chains ready for execution
        ready_time = datetime.now() + timedelta(hours=2)
        ready_chains = self.db.query(ChainState).filter(
            ChainState.status == 'scheduled',
            ChainState.scheduled_for <= ready_time
        ).all()
        
        self.assertEqual(len(ready_chains), 1)
        
        # 4. Count queries
        total_chains = self.db.query(ChainState).count()
        self.assertGreaterEqual(total_chains, 3)

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests()
