"""Unit tests for reverse refund authorization request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.reverse_refund_authorization import build_reverse_refund_authorization_request

class TestBuildReverseRefundAuthorizationRequest:
    """Test reverse refund authorization request building"""

    def test_build_basic_request(self):
        """Test building basic reverse refund authorization request"""
        row = pd.Series({
            'test_id': 'REV_REF001'
        })
        
        with patch('src.request_builders.reverse_refund_authorization.generate_random_string', return_value='revref123'):
            request = build_reverse_refund_authorization_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'REV_REF001:revref123'
            assert hasattr(request, 'transaction_timestamp')
            
            # Should NOT have amount (full reversal only)
            assert not hasattr(request, 'amount') or request.amount is None
            
            # Should NOT have any other complex fields
            assert not hasattr(request, 'dynamic_currency_conversion')
            assert not hasattr(request, 'card_payment_data')
            assert not hasattr(request, 'references')

    def test_operation_id_format(self):
        """Test operation ID format"""
        row = pd.Series({
            'test_id': 'REV_REF002'
        })
        
        with patch('src.request_builders.reverse_refund_authorization.generate_random_string', return_value='revref456'):
            request = build_reverse_refund_authorization_request(row)
            
            # Verify operation ID format
            assert request.operation_id == 'REV_REF002:revref456'

    def test_request_cleaning_called(self):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'REV_REF003'
        })
        
        with patch('src.request_builders.reverse_refund_authorization.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_reverse_refund_authorization_request(row)
            mock_clean.assert_called_once()

    def test_minimal_request_structure(self):
        """Test that request has only minimal required fields"""
        row = pd.Series({
            'test_id': 'REV_REF004'
        })
        
        request = build_reverse_refund_authorization_request(row)
        request_dict = request.to_dictionary()
        
        # Should only have the minimal required fields
        expected_keys = {'operationId', 'transactionTimestamp'}
        actual_keys = set(request_dict.keys())
        
        # All expected keys should be present
        assert expected_keys.issubset(actual_keys)
        
        # Should not have complex fields
        unexpected_keys = {'amount', 'dynamicCurrencyConversion', 'cardPaymentData', 'references'}
        assert not any(key in actual_keys for key in unexpected_keys)