"""Chain state persistence models"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.orm.attributes import flag_modified  # ✅ Correct import location
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional
from .database import Base

class ChainState(Base):
    """Persistent chain execution state"""
    __tablename__ = "chain_states"
    
    # Primary identification
    chain_id = Column(String(255), primary_key=True)
    execution_id = Column(String(255), nullable=False, index=True)
    
    # Execution state
    current_step_index = Column(Integer, nullable=False, default=0)
    previous_outputs = Column(JSON, nullable=False, default=dict)
    
    # Scheduling information
    scheduled_for = Column(DateTime(timezone=True), nullable=True, index=True)
    delay_seconds = Column(Integer, nullable=True)
    
    # Status tracking
    status = Column(String(50), nullable=False, default='active', index=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    
    # Extended chain context
    chain_config = Column(JSON, nullable=True)
    execution_metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<ChainState(chain_id='{self.chain_id}', status='{self.status}', step={self.current_step_index})>"
    
    @classmethod
    def create_new(cls, chain_id: str, execution_id: str, chain_config: Dict[str, Any],
                   created_by: Optional[str] = None) -> 'ChainState':
        """Create new chain state"""
        return cls(
            chain_id=chain_id,
            execution_id=execution_id,
            current_step_index=0,
            previous_outputs={},
            status='active',
            chain_config=chain_config,
            created_by=created_by,
            execution_metadata={
                'created_timestamp': datetime.now().isoformat(),
                'framework_version': '3.0.0'
            }
        )
    
    def update_step(self, step_index: int, outputs: Dict[str, Any]):
        """Update current step and outputs"""
        self.current_step_index = step_index
        
        # Ensure previous_outputs is a dictionary
        if self.previous_outputs is None:
            self.previous_outputs = {}
        
        # Create a new dictionary and update it
        updated_outputs = dict(self.previous_outputs)
        updated_outputs.update(outputs)
        self.previous_outputs = updated_outputs
        
        # Mark the JSON field as modified for SQLAlchemy
        flag_modified(self, 'previous_outputs')
        
        self.updated_at = datetime.now()
    
    def add_outputs(self, outputs: Dict[str, Any]):
        """Add outputs without changing step index"""
        if self.previous_outputs is None:
            self.previous_outputs = {}
        
        # Create new dict and update
        current_outputs = dict(self.previous_outputs)
        current_outputs.update(outputs)
        self.previous_outputs = current_outputs
        
        # Mark as modified
        flag_modified(self, 'previous_outputs')
        self.updated_at = datetime.now()
    
    def schedule_for_later(self, scheduled_time: datetime, delay_seconds: Optional[int] = None):
        """Schedule chain for future execution"""
        self.scheduled_for = scheduled_time
        self.delay_seconds = delay_seconds
        self.status = 'scheduled'
        self.updated_at = datetime.now()
    
    def mark_completed(self):
        """Mark chain as completed"""
        self.status = 'completed'
        self.updated_at = datetime.now()
    
    def mark_failed(self, error_message: str):
        """Mark chain as failed with error"""
        self.status = 'failed'
        self.error_message = error_message
        self.updated_at = datetime.now()
        
    def get_output(self, key: str, default=None):
        """Get a specific output value"""
        if self.previous_outputs and isinstance(self.previous_outputs, dict):
            return self.previous_outputs.get(key, default)
        return default
    
    def has_output(self, key: str) -> bool:
        """Check if output key exists"""
        if self.previous_outputs and isinstance(self.previous_outputs, dict):
            return key in self.previous_outputs
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'chain_id': self.chain_id,
            'execution_id': self.execution_id,
            'current_step_index': self.current_step_index,
            'previous_outputs': self.previous_outputs or {},
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'delay_seconds': self.delay_seconds,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'chain_config': self.chain_config or {},
            'execution_metadata': self.execution_metadata or {},
            'error_message': self.error_message,
            'retry_count': self.retry_count
        }
