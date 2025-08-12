"""Test get payment request builder"""

import pytest
from src.request_builders.get_payment import build_get_payment_request

class TestBuildGetPaymentRequest:
    """Test get payment request building"""
    
    def test_build_get_payment_request_returns_none(self):
        """Test that get payment request builder returns None (no request body)"""
        row = {
            'test_id': 'GET001',
            'payment_id': 'pay:test:12345'
        }
        
        result = build_get_payment_request(row)
        
        assert result is None

    def test_build_get_payment_request_with_empty_row(self):
        """Test get payment request builder with empty row"""
        row = {}
        
        result = build_get_payment_request(row)
        
        assert result is None

    def test_build_get_payment_request_with_none_row(self):
        """Test get payment request builder with None row"""
        result = build_get_payment_request(None)
        
        assert result is None