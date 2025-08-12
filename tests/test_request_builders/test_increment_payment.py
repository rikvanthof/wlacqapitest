"""Test increment payment request builder"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.request_builders.increment_payment import build_increment_payment_request

class TestBuildIncrementPaymentRequest:
    """Test increment payment request building"""
    
    def test_build_complete_request(self):
        """Test building complete increment payment request"""
        row = {
            'test_id': 'INC001',
            'amount': 50,
            'currency': 'GBP'
        }
        
        with patch('src.request_builders.increment_payment.generate_random_string', return_value='inc123'):
            with patch('pandas.Timestamp.now') as mock_now:
                mock_timestamp = Mock()
                mock_now.return_value.tz_localize.return_value.replace.return_value.to_pydatetime.return_value = mock_timestamp
                
                request = build_increment_payment_request(row)
                
                # Verify request structure
                assert hasattr(request, 'operation_id')
                assert request.operation_id == 'INC001-inc123'
                assert hasattr(request, 'transaction_timestamp')
                assert hasattr(request, 'increment_amount')
                
                # Verify amount structure
                assert request.increment_amount.amount == 50
                assert request.increment_amount.currency_code == 'GBP'
                assert request.increment_amount.number_of_decimals == 2

    def test_build_with_different_currency(self):
        """Test building request with different currency"""
        row = {
            'test_id': 'INC002',
            'amount': 100,
            'currency': 'EUR'
        }
        
        request = build_increment_payment_request(row)
        
        assert request.increment_amount.amount == 100
        assert request.increment_amount.currency_code == 'EUR'

    def test_build_with_large_amount(self):
        """Test building request with large amount"""
        row = {
            'test_id': 'INC003',
            'amount': 9999.99,
            'currency': 'USD'
        }
        
        request = build_increment_payment_request(row)
        
        assert request.increment_amount.amount == 9999
        assert request.increment_amount.currency_code == 'USD'

    @patch('src.request_builders.increment_payment.clean_request')
    def test_request_cleaning_called(self, mock_clean_request):
        """Test that request cleaning is called"""
        row = {
            'test_id': 'INC004',
            'amount': 25,
            'currency': 'GBP'
        }
        
        mock_clean_request.return_value = Mock()
        
        build_increment_payment_request(row)
        
        mock_clean_request.assert_called_once()

    def test_operation_id_length_limit(self):
        """Test operation ID respects length limits"""
        long_test_id = 'A' * 35  # Long test ID
        row = {
            'test_id': long_test_id,
            'amount': 50,
            'currency': 'GBP'
        }
        
        request = build_increment_payment_request(row)
        
        # Operation ID should not exceed reasonable length
        assert len(request.operation_id) <= 40
        assert request.operation_id.startswith(long_test_id)