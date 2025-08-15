"""Unit tests for capture refund request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.capture_refund import build_capture_refund_request

class TestBuildCaptureRefundRequest:
    """Test capture refund request building"""

    def test_build_basic_request(self):
        """Test building basic capture refund request"""
        row = pd.Series({
            'test_id': 'CAP_REF001'
        })
        
        with patch('src.request_builders.capture_refund.generate_random_string', return_value='capref123'):
            request = build_capture_refund_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'CAP_REF001:capref123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'references')
            
            # Should NOT have amount (capture everything authorized)
            assert not hasattr(request, 'amount') or request.amount is None

    def test_build_with_dynamic_descriptor(self):
        """Test building request with dynamic descriptor"""
        row = pd.Series({
            'test_id': 'CAP_REF002',
            'dynamic_descriptor': 'Test Refund Capture'
        })
        
        with patch('src.request_builders.capture_refund.generate_random_string', return_value='capref456'):
            request = build_capture_refund_request(row)
            
            # Verify dynamic descriptor
            assert hasattr(request, 'references')
            assert request.references.dynamic_descriptor == 'Test Refund Capture'

    def test_merchant_reference_generation(self):
        """Test merchant reference generation"""
        row = pd.Series({
            'test_id': 'CAP_REF003'
        })
        
        with patch('src.request_builders.capture_refund.generate_random_string', return_value='capref789'):
            request = build_capture_refund_request(row)
            
            # Should have references with generated merchant_reference
            assert hasattr(request, 'references')
            assert request.references.merchant_reference == 'CAP_REF003:capref789'

    def test_request_cleaning_called(self):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'CAP_REF004'
        })
        
        with patch('src.request_builders.capture_refund.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_capture_refund_request(row)
            mock_clean.assert_called_once()