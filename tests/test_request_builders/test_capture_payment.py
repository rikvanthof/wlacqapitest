"""Test capture payment request builder"""

import pytest
from unittest.mock import Mock, patch
from src.request_builders.capture_payment import build_capture_payment_request

class TestBuildCapturePaymentRequest:
    """Test capture payment request building"""
    
    def test_build_complete_request(self):
        """Test building complete capture payment request"""
        row = {
            'test_id': 'CAP001',
            'amount': 75,
            'currency': 'GBP'
        }
        
        with patch('src.request_builders.capture_payment.generate_random_string', return_value='cap123'):
            request = build_capture_payment_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'CAP001-cap123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'amount_of_money')
            
            # Verify amount structure
            assert request.amount_of_money.amount == 75
            assert request.amount_of_money.currency_code == 'GBP'
            assert request.amount_of_money.number_of_decimals == 2

    def test_build_different_amounts_and_currencies(self):
        """Test building requests with different amounts and currencies"""
        test_cases = [
            {'amount': 10, 'currency': 'EUR', 'test_id': 'CAP002'},
            {'amount': 500, 'currency': 'USD', 'test_id': 'CAP003'},
            {'amount': 1.50, 'currency': 'GBP', 'test_id': 'CAP004'}
        ]
        
        for case in test_cases:
            request = build_capture_payment_request(case)
            
            assert request.amount_of_money.amount == case['amount']
            assert request.amount_of_money.currency_code == case['currency']
            assert case['test_id'] in request.operation_id

    @patch('request_builders.capture_payment.clean_request')
    def test_request_cleaning_called(self, mock_clean_request):
        """Test that request cleaning is called"""
        row = {
            'test_id': 'CAP005',
            'amount': 100,
            'currency': 'GBP'
        }
        
        mock_clean_request.return_value = Mock()
        
        build_capture_payment_request(row)
        
        mock_clean_request.assert_called_once()