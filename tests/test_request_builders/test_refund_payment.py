"""Test refund payment request builder"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.request_builders.refund_payment import build_refund_payment_request

class TestBuildRefundPaymentRequest:
    """Test refund payment request building"""
    
    def test_build_complete_request_with_amount(self):
        """Test building complete refund request with amount"""
        row = {
            'test_id': 'REF001',
            'amount': 50,
            'currency': 'GBP'
        }
        
        with patch('src.request_builders.refund_payment.generate_random_string', return_value='ref123'):
            request = build_refund_payment_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'REF001-ref123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'amount_of_money')
            
            # Verify amount structure
            assert request.amount_of_money.amount == 50
            assert request.amount_of_money.currency_code == 'GBP'
            assert request.amount_of_money.number_of_decimals == 2

    def test_build_request_without_amount(self):
        """Test building refund request without amount (full refund)"""
        row = {
            'test_id': 'REF002',
            'amount': None,  # No amount specified
            'currency': 'GBP'
        }
        
        request = build_refund_payment_request(row)
        
        # Should not have amount_of_money for full refund
        assert not hasattr(request, 'amount_of_money')
        assert hasattr(request, 'operation_id')
        assert hasattr(request, 'transaction_timestamp')

    def test_build_request_with_none_amount(self):
        """Test building refund request with None amount"""
        row = {
            'test_id': 'REF003',
            'amount': None,
            'currency': 'EUR'
        }
        
        request = build_refund_payment_request(row)
        
        # Should not have amount_of_money
        assert not hasattr(request, 'amount_of_money')

    def test_build_request_with_zero_amount(self):
        """Test building refund request with zero amount"""
        row = {
            'test_id': 'REF004',
            'amount': 0,
            'currency': 'USD'
        }
        
        request = build_refund_payment_request(row)
        
        # Zero is considered a valid amount
        assert hasattr(request, 'amount_of_money')
        assert request.amount_of_money.amount == 0
        assert request.amount_of_money.currency_code == 'USD'

    @patch('src.request_builders.refund_payment.clean_request')
    def test_request_cleaning_called(self, mock_clean_request):
        """Test that request cleaning is called"""
        row = {
            'test_id': 'REF005',
            'amount': 25,
            'currency': 'GBP'
        }
        
        mock_clean_request.return_value = Mock()
        
        build_refund_payment_request(row)
        
        mock_clean_request.assert_called_once()