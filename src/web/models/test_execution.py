"""Test execution tracking models"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional
from .database import Base

class TestExecution(Base):
    """Test execution session tracking"""
    __tablename__ = "test_executions"
    
    # Primary identification
    execution_id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Execution configuration
    test_file_path = Column(String(500), nullable=False)
    execution_config = Column(JSON, nullable=True)
    
    # Status tracking
    status = Column(String(50), nullable=False, default='running', index=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # User tracking
    created_by = Column(String(255), nullable=True)
    
    # Execution statistics
    total_chains = Column(Integer, default=0)
    completed_chains = Column(Integer, default=0)
    failed_chains = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    passed_steps = Column(Integer, default=0)
    failed_steps = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<TestExecution(id='{self.execution_id}', name='{self.name}', status='{self.status}')>"
    
    def update_statistics(self, chain_completed: bool = False, chain_failed: bool = False,
                         step_passed: bool = False, step_failed: bool = False):
        """Update execution statistics"""
        if chain_completed:
            self.completed_chains += 1
        if chain_failed:
            self.failed_chains += 1
        if step_passed:
            self.passed_steps += 1
        if step_failed:
            self.failed_steps += 1
    
    def mark_completed(self):
        """Mark execution as completed"""
        self.status = 'completed'
        self.completed_at = datetime.now()
    
    def mark_failed(self):
        """Mark execution as failed"""
        self.status = 'failed'
        self.completed_at = datetime.now()
