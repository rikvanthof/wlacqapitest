"""Initialize SQLite database for development"""

import sys
import os

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Initialize database and create test data"""
    print("🗄️ Starting database initialization...")
    
    try:
        # Use absolute imports
        from src.web.models.database import create_tables, get_database_info, SessionLocal
        from src.web.models.chain_state import ChainState
        from src.web.models.test_execution import TestExecution
        import uuid
        from datetime import datetime
        
        # Show database info
        db_info = get_database_info()
        print(f"📍 Database Type: {db_info['type']}")
        if db_info['type'] == 'SQLite':
            print(f"📁 Database File: {db_info['file_path']}")
        
        # Create tables
        print("🔧 Creating database tables...")
        create_tables()
        
        print("🧪 Creating test data...")
        db = SessionLocal()
        
        try:
            # Create test execution
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            execution = TestExecution(
                execution_id=execution_id,
                name="Database Initialization",
                description="Database initialization",
                test_file_path="config/test_suites/smoke_tests.csv",
                execution_config={"threads": 1, "tags": ["development", "setup"]},
                created_by="dev_setup"
            )
            db.add(execution)
            
            # Create test chain state
            chain_id = f"chain_{uuid.uuid4().hex[:8]}"
            chain_state = ChainState.create_new(
                chain_id=chain_id,
                execution_id=execution.execution_id,
                chain_config={
                    "test_type": "development", 
                    "environment": "dev",
                    "setup_timestamp": datetime.now().isoformat()
                },
                created_by="dev_setup"
            )
            db.add(chain_state)
            
            db.commit()
            
            print(f"✅ Created test execution: {execution.execution_id}")
            print(f"✅ Created test chain state: {chain_state.chain_id}")
            
            # Verify data
            executions_count = db.query(TestExecution).count()
            chain_states_count = db.query(ChainState).count()
            
            print(f"📊 Database verification:")
            print(f"   - {executions_count} test execution(s)")
            print(f"   - {chain_states_count} chain state(s)")
            
            # Test chain state functionality
            print("🔄 Testing chain state operations...")
            
            # Update step
            test_outputs = {"payment_id": "pay_12345", "scheme_transaction_id": "scheme_67890"}
            chain_state.update_step(1, test_outputs)
            db.commit()
            
            # Schedule for later
            from datetime import timedelta
            future_time = datetime.now() + timedelta(hours=1)
            chain_state.schedule_for_later(future_time, delay_seconds=300)
            db.commit()
            
            print("✅ Chain state operations successful")
            
            # Show final state
            final_state = db.query(ChainState).filter_by(chain_id=chain_id).first()
            print(f"📋 Final chain state:")
            print(f"   - Status: {final_state.status}")
            print(f"   - Current step: {final_state.current_step_index}")
            print(f"   - Outputs: {final_state.previous_outputs}")
            print(f"   - Scheduled for: {final_state.scheduled_for}")
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.rollback()
            raise
        finally:
            db.close()
        
        print("🎉 Database initialization complete!")
        print("🚀 Ready for development!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the project root directory")
        print(f"💡 Current working directory: {os.getcwd()}")
        print(f"💡 Project root should be: {project_root}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
