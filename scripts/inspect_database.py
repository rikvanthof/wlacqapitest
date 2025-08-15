"""Inspect the current database state"""

import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

def main():
    """Inspect current database contents"""
    print("🔍 Database Inspector")
    print("=" * 50)
    
    try:
        from src.web.models.database import SessionLocal, get_database_info
        from src.web.models.chain_state import ChainState
        from src.web.models.test_execution import TestExecution
        from src.web.models import init_database
        
        # Show database info
        db_info = get_database_info()
        print(f"📍 Database: {db_info['type']}")
        if db_info['type'] == 'SQLite':
            print(f"📁 File: {db_info['file_path']}")
            
            # Check if file exists and show size
            if os.path.exists(db_info['file_path']):
                size = os.path.getsize(db_info['file_path'])
                print(f"📏 Size: {size:,} bytes")
            else:
                print("⚠️ Database file not found!")
                return 1
        
        print("\n" + "=" * 50)
        
        db = SessionLocal()
        
        try:
            # Try to query test executions
            try:
                executions = db.query(TestExecution).all()
                print(f"📊 Test Executions ({len(executions)}):")
                
                for execution in executions:
                    print(f"   🔸 {execution.execution_id}")
                    print(f"      Name: {execution.name}")
                    print(f"      Status: {execution.status}")
                    print(f"      Started: {execution.started_at}")
                    print(f"      Config: {execution.execution_config}")
                    print()
            except Exception as e:
                print(f"⚠️ Could not query test_executions table: {e}")
                print("🔧 Attempting to recreate database tables...")
                init_database()
                executions = db.query(TestExecution).all()
                print(f"📊 Test Executions ({len(executions)}):")
            
            # Try to query chain states
            try:
                chain_states = db.query(ChainState).all()
                print(f"🔗 Chain States ({len(chain_states)}):")
                
                for chain in chain_states:
                    print(f"   🔸 {chain.chain_id}")
                    print(f"      Execution: {chain.execution_id}")
                    print(f"      Status: {chain.status}")
                    print(f"      Step: {chain.current_step_index}")
                    print(f"      Outputs: {chain.previous_outputs}")
                    print(f"      Scheduled: {chain.scheduled_for}")
                    print(f"      Created: {chain.created_at}")
                    print(f"      Updated: {chain.updated_at}")
                    print()
            except Exception as e:
                print(f"⚠️ Could not query chain_states table: {e}")
                chain_states = []
            
            # Show summary
            print("=" * 50)
            print(f"📈 Summary:")
            print(f"   - {len(executions)} test execution(s)")
            print(f"   - {len(chain_states)} chain state(s)")
            
            # Check for scheduled chains
            scheduled_chains = db.query(ChainState).filter_by(status='scheduled').count()
            if scheduled_chains > 0:
                print(f"   - {scheduled_chains} scheduled chain(s)")
            
        finally:
            db.close()
            
        print("\n✅ Database inspection complete!")
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
