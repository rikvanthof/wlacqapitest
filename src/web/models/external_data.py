# src/web/models/external_data.py
"""External data upload and processing models"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, List, Optional
from .database import Base

class ExternalDataUpload(Base):
    """External data file uploads"""
    __tablename__ = "external_data_uploads"
    
    # Primary identification
    upload_id = Column(String(255), primary_key=True)
    execution_id = Column(String(255), ForeignKey('test_executions.execution_id'), nullable=False, index=True)
    
    # File information
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'csv', 'xml'
    file_size = Column(BigInteger, nullable=False)
    upload_path = Column(String(1000), nullable=False)
    
    # Processing status
    processing_status = Column(String(50), nullable=False, default='pending', index=True)
    # Valid statuses: 'pending', 'processing', 'completed', 'failed'
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_errors = Column(JSON, nullable=True)
    
    # Upload metadata
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(String(255), nullable=True)
    
    # Configuration for processing
    correlation_config = Column(JSON, nullable=True)
    processing_config = Column(JSON, nullable=True)
    
    # Processing statistics
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    matched_records = Column(Integer, default=0)
    error_records = Column(Integer, default=0)
    
    # Relationships
    data_records = relationship("ExternalDataRecord", backref="upload", lazy="dynamic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ExternalDataUpload(id='{self.upload_id}', filename='{self.original_filename}', status='{self.processing_status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'upload_id': self.upload_id,
            'execution_id': self.execution_id,
            'file_info': {
                'filename': self.filename,
                'original_filename': self.original_filename,
                'file_type': self.file_type,
                'file_size': self.file_size,
                'upload_path': self.upload_path
            },
            'processing': {
                'status': self.processing_status,
                'processed_at': self.processed_at.isoformat() if self.processed_at else None,
                'errors': self.processing_errors
            },
            'uploaded_at': self.uploaded_at.isoformat(),
            'uploaded_by': self.uploaded_by,
            'configuration': {
                'correlation_config': self.correlation_config,
                'processing_config': self.processing_config
            },
            'statistics': {
                'total_records': self.total_records,
                'processed_records': self.processed_records,
                'matched_records': self.matched_records,
                'error_records': self.error_records
            }
        }
    
    def update_processing_status(self, status: str, error_message: str = None):
        """Update processing status"""
        self.processing_status = status
        if status == 'completed' or status == 'failed':
            self.processed_at = datetime.now()
        if error_message and status == 'failed':
            self.processing_errors = {'error': error_message, 'timestamp': datetime.now().isoformat()}

class ExternalDataRecord(Base):
    """Individual records from external data files"""
    __tablename__ = "external_data_records"
    
    # Primary identification
    record_id = Column(String(255), primary_key=True)
    upload_id = Column(String(255), ForeignKey('external_data_uploads.upload_id'), nullable=False, index=True)
    
    # Source information
    source_row_number = Column(Integer, nullable=True)
    
    # Correlation and matching
    correlation_keys = Column(JSON, nullable=False, index=True)  # Keys used for matching
    record_data = Column(JSON, nullable=False)  # Full record data
    matched_test_results = Column(JSON, nullable=True)  # Array of test_result IDs
    
    # Processing information
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    correlation_confidence = Column(Integer, nullable=True)  # 0-100 confidence score
    validation_errors = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<ExternalDataRecord(id='{self.record_id}', upload_id='{self.upload_id}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'record_id': self.record_id,
            'upload_id': self.upload_id,
            'source_row_number': self.source_row_number,
            'correlation_keys': self.correlation_keys,
            'record_data': self.record_data,
            'matched_test_results': self.matched_test_results,
            'processed_at': self.processed_at.isoformat(),
            'correlation_confidence': self.correlation_confidence,
            'validation_errors': self.validation_errors
        }

class E2EAnalysisResult(Base):
    """End-to-end analysis results"""
    __tablename__ = "e2e_analysis_results"
    
    # Primary identification
    analysis_id = Column(String(255), primary_key=True)
    execution_id = Column(String(255), ForeignKey('test_executions.execution_id'), nullable=False, index=True)
    test_result_id = Column(String(255), ForeignKey('test_results_enhanced.result_id'), nullable=True, index=True)
    
    # Analysis configuration
    analysis_type = Column(String(100), nullable=False)
    # Valid types: 'settlement_match', 'notification_delivery', 'processing_time', 'amount_reconciliation', 'custom'
    analysis_config = Column(JSON, nullable=True)
    
    # Analysis results
    analysis_results = Column(JSON, nullable=False)
    pass_result = Column('pass', Boolean, nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    
    # Related data
    external_record_ids = Column(JSON, nullable=True)  # Array of external_data_record IDs
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    analysis_duration_ms = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<E2EAnalysisResult(id='{self.analysis_id}', type='{self.analysis_type}', pass={self.pass_result})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'analysis_id': self.analysis_id,
            'execution_id': self.execution_id,
            'test_result_id': self.test_result_id,
            'analysis_type': self.analysis_type,
            'analysis_config': self.analysis_config,
            'results': self.analysis_results,
            'pass': self.pass_result,
            'confidence_score': self.confidence_score,
            'external_record_ids': self.external_record_ids,
            'created_at': self.created_at.isoformat(),
            'analysis_duration_ms': self.analysis_duration_ms
        }