# src/web/models/indexes.py
"""Database indexes for performance optimization"""

from sqlalchemy import Index
from .chain_state import ChainState
from .test_execution import TestExecution, TestResultEnhanced
from .external_data import ExternalDataUpload, ExternalDataRecord, E2EAnalysisResult

# Performance indexes
performance_indexes = [
    # Chain state indexes
    Index('ix_chain_states_status_scheduled', ChainState.status, ChainState.scheduled_for),
    Index('ix_chain_states_execution_status', ChainState.execution_id, ChainState.status),
    
    # Test execution indexes
    Index('ix_test_executions_status_started', TestExecution.status, TestExecution.started_at),
    Index('ix_test_executions_created_by_status', TestExecution.created_by, TestExecution.status),
    
    # Test results indexes
    Index('ix_test_results_execution_chain', TestResultEnhanced.execution_id, TestResultEnhanced.chain_id),
    Index('ix_test_results_transaction_ids', TestResultEnhanced.transaction_id, TestResultEnhanced.payment_id, TestResultEnhanced.scheme_transaction_id),
    Index('ix_test_results_executed_at_pass', TestResultEnhanced.executed_at, TestResultEnhanced.pass_result),
    
    # External data indexes
    Index('ix_external_uploads_execution_status', ExternalDataUpload.execution_id, ExternalDataUpload.processing_status),
    Index('ix_external_records_upload_correlation', ExternalDataRecord.upload_id, ExternalDataRecord.correlation_confidence),
    
    # E2E analysis indexes
    Index('ix_e2e_analysis_execution_type', E2EAnalysisResult.execution_id, E2EAnalysisResult.analysis_type),
    Index('ix_e2e_analysis_test_result', E2EAnalysisResult.test_result_id, E2EAnalysisResult.pass_result)
]

def create_performance_indexes():
    """Create all performance indexes"""
    from .database import engine
    
    for index in performance_indexes:
        try:
            index.create(engine, checkfirst=True)
            print(f"✅ Created index: {index.name}")
        except Exception as e:
            print(f"⚠️ Index {index.name} already exists or failed: {e}")
    
    print("✅ All performance indexes processed")

if __name__ == "__main__":
    create_performance_indexes()