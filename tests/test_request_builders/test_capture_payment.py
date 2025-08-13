"""Test capture payment request builder - updated for correct attributes"""

import pytest
from unittest.mock import patch, Mock
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
            
            # Verify request structure with correct attribute names
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'CAP001-cap123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'amount')  # Changed from 'amount_of_money'
            
            # Verify amount details
            assert request.amount.amount == 75
            assert request.amount.currency_code == 'GBP'
            assert request.amount.number_of_decimals == 2

    def test_build_different_amounts_and_currencies(self):
        """Test building requests with different amounts and currencies"""
        test_cases = [
            {'test_id': 'CAP002', 'amount': 150, 'currency': 'EUR'},
            {'test_id': 'CAP003', 'amount': 200, 'currency': 'USD'},
            {'test_id': 'CAP004', 'amount': 50, 'currency': 'GBP'}
        ]
        
        for row in test_cases:
            request = build_capture_payment_request(row)
            
            # Verify amount with correct attribute
            assert hasattr(request, 'amount')  # Changed from 'amount_of_money'
            assert request.amount.amount == row['amount']
            assert request.amount.currency_code == row['currency']
            assert request.amount.number_of_decimals == 2

    def test_build_minimal_request(self):
        """Test building minimal capture payment request"""
        row = {
            'test_id': 'CAP005',
            'amount': 100,
            'currency': 'GBP'
        }
        
        request = build_capture_payment_request(row)
        
        # Verify required fields
        assert hasattr(request, 'operation_id')
        assert hasattr(request, 'transaction_timestamp')
        assert hasattr(request, 'amount')  # Changed from 'amount_of_money'

    def test_build_request_with_zero_amount(self):
        """Test building request with zero amount (should still work)"""
        row = {
            'test_id': 'CAP006',
            'amount': 0,
            'currency': 'GBP'
        }
        
        request = build_capture_payment_request(row)
        
        # Should handle zero amount gracefully
        assert hasattr(request, 'amount')  # Changed from 'amount_of_money'
        assert request.amount.amount == 0

    @patch('src.request_builders.capture_payment.clean_request')
    def test_request_cleaning_called(self, mock_clean_request):
        """Test that request cleaning is called"""
        row = {
            'test_id': 'CAP007',
            'amount': 100,
            'currency': 'GBP'
        }
        
        mock_clean_request.return_value = Mock()
        
        build_capture_payment_request(row)
        
        mock_clean_request.assert_called_once()

    def test_operation_id_generation(self):
        """Test operation ID generation"""
        row = {
            'test_id': 'CAPTURE_TEST_001',
            'amount': 100,
            'currency': 'GBP'
        }
        
        with patch('src.request_builders.capture_payment.generate_random_string', return_value='test123'):
            request = build_capture_payment_request(row)
            
            # Should combine test_id with random string
            assert request.operation_id == 'CAPTURE_TEST_001-test123'

    def test_timestamp_generation(self):
        """Test timestamp generation"""
        row = {
            'test_id': 'CAP008',
            'amount': 100,
            'currency': 'GBP'
        }
        
        request = build_capture_payment_request(row)
        
        # Should have a timestamp
        assert hasattr(request, 'transaction_timestamp')
        assert request.transaction_timestamp is not None
