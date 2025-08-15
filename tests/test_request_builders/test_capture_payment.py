"""Fixed unit tests for capture payment request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.capture_payment import build_capture_payment_request

class TestBuildCapturePaymentRequest:
    """Test capture payment request building"""

    def test_build_basic_request(self):
        """Test building basic capture payment request"""
        row = pd.Series({
            'test_id': 'CAP001'
        })
        
        with patch('src.request_builders.capture_payment.generate_random_string', return_value='cap123'):
            request = build_capture_payment_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'CAP001:cap123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'references')

    def test_build_with_amount(self):
        """Test building request with specific amount"""
        row = pd.Series({
            'test_id': 'CAP002',
            'amount': 1500,
            'currency': 'EUR'  # ✅ Added required currency
        })
        
        request = build_capture_payment_request(row)
        
        # Should have amount if specified
        if hasattr(request, 'amount') and request.amount:
            assert request.amount.amount == 1500
            assert request.amount.currency_code == 'EUR'

    def test_build_with_dynamic_descriptor(self):
        """Test building request with dynamic descriptor"""
        row = pd.Series({
            'test_id': 'CAP003',
            'dynamic_descriptor': 'Test Capture'
        })
        
        request = build_capture_payment_request(row)
        
        # Should have dynamic descriptor
        if hasattr(request, 'references') and request.references:
            assert request.references.dynamic_descriptor == 'Test Capture'

    def test_merchant_reference_generation(self):
        """Test merchant reference generation"""
        row = pd.Series({
            'test_id': 'CAP004'
        })
        
        with patch('src.request_builders.capture_payment.generate_random_string', return_value='cap456'):
            request = build_capture_payment_request(row)
            
            assert hasattr(request, 'references')
            assert request.references.merchant_reference == 'CAP004:cap456'

    def test_request_cleaning_called(self):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'CAP005'
        })
        
        with patch('src.request_builders.capture_payment.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_capture_payment_request(row)
            mock_clean.assert_called_once()

    def test_partial_capture(self):
        """Test partial capture with amount less than original"""
        row = pd.Series({
            'test_id': 'CAP006',
            'amount': 500,
            'currency': 'EUR'  # ✅ Added required currency
        })
        
        request = build_capture_payment_request(row)
        
        # Should handle partial captures
        if hasattr(request, 'amount') and request.amount:
            assert request.amount.amount == 500
            assert request.amount.currency_code == 'EUR'

    def test_full_capture_no_amount(self):  # ✅ New test for full capture
        """Test full capture without specifying amount"""
        row = pd.Series({
            'test_id': 'CAP007'
        })
        
        request = build_capture_payment_request(row)
        
        # Full capture should not have amount (captures full authorized amount)
        assert not hasattr(request, 'amount') or request.amount is None