"""Test get refund request builder"""

import pytest
from src.request_builders.get_refund import build_get_refund_request

class TestBuildGetRefundRequest:
    """Test get refund request building"""
    
    def test_build_get_refund_request_returns_none(self):
        """Test that get refund request builder returns None (no request body)"""
        row = {
            'test_id': 'GETREF001',
            'refund_id': 'refund:test:67890'
        }
        
        result = build_get_refund_request(row)
        
        assert result is None

    def test_build_get_refund_request_with_empty_row(self):
        """Test get refund request builder with empty row"""
        row = {}
        
        result = build_get_refund_request(row)
        
        assert result is None

    def test_build_get_refund_request_with_none_row(self):
        """Test get refund request builder with None row"""
        result = build_get_refund_request(None)
        
        assert result is None