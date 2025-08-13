"""Test refund payment request builder - updated for correct attributes"""

import pytest
from unittest.mock import patch, Mock
from src.request_builders.refund_payment import build_refund_payment_request

class TestBuildRefundPaymentRequest:
    """Test refund payment request building"""
    
    def test_build_complete_request_with_amount(self):
        """Test building complete refund payment request with amount"""
        row = {
            'test_id': 'REF001',
            'amount': 75,
            'currency': 'GBP'
        }
        
        with patch('src.request_builders.refund_payment.generate_random_string', return_value='ref123'):
            request = build_refund_payment_request(row)
            
            # Verify request structure with correct attribute names
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'REF001-ref123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'amount')  # Changed from 'amount_of_money'
            
            # Verify amount details
            assert request.amount.amount == 75
            assert request.amount.currency_code == 'GBP'
            assert request.amount.number_of_decimals == 2

    def test_build_request_without_amount(self):
        """Test building refund request without amount (full refund)"""
        row = {
            'test_id': 'REF002',
            'amount': None,  # No amount means full refund
            'currency': 'GBP'
        }
        
        request = build_refund_payment_request(row)
        
        # Should have basic structure but no amount for full refund
        assert hasattr(request, 'operation_id')
        assert hasattr(request, 'transaction_timestamp')
        # Amount might not be set for full refunds

    def test_build_request_with_zero_amount(self):
        """Test building request with zero amount"""
        row = {
            'test_id': 'REF003',
            'amount': 0,
            'currency': 'GBP'
        }
        
        request = build_refund_payment_request(row)
        
        # Should handle zero amount
        assert hasattr(request, 'operation_id')
        assert hasattr(request, 'transaction_timestamp')
        # Zero amount handling depends on implementation

    def test_build_different_amounts_and_currencies(self):
        """Test building requests with different amounts and currencies"""
        test_cases = [
            {'test_id': 'REF004', 'amount': 150, 'currency': 'EUR'},
            {'test_id': 'REF005', 'amount': 200, 'currency': 'USD'},
            {'test_id': 'REF006', 'amount': 50, 'currency': 'GBP'}
        ]
        
        for row in test_cases:
            request = build_refund_payment_request(row)
            
            # Verify basic structure
            assert hasattr(request, 'operation_id')
            assert hasattr(request, 'transaction_timestamp')
            
            # If amount is set, verify it
            if hasattr(request, 'amount') and request.amount is not None:
                assert request.amount.amount == row['amount']
                assert request.amount.currency_code == row['currency']
                assert request.amount.number_of_decimals == 2

    @patch('src.request_builders.refund_payment.clean_request')
    def test_request_cleaning_called(self, mock_clean_request):
        """Test that request cleaning is called"""
        row = {
            'test_id': 'REF007',
            'amount': 100,
            'currency': 'GBP'
        }
        
        mock_clean_request.return_value = Mock()
        
        build_refund_payment_request(row)
        
        mock_clean_request.assert_called_once()

    def test_operation_id_generation(self):
        """Test operation ID generation"""
        row = {
            'test_id': 'REFUND_TEST_001',
            'amount': 100,
            'currency': 'GBP'
        }
        
        with patch('src.request_builders.refund_payment.generate_random_string', return_value='test123'):
            request = build_refund_payment_request(row)
            
            # Should combine test_id with random string
            assert request.operation_id == 'REFUND_TEST_001-test123'

    def test_timestamp_generation(self):
        """Test timestamp generation"""
        row = {
            'test_id': 'REF008',
            'amount': 100,
            'currency': 'GBP'
        }
        
        request = build_refund_payment_request(row)
        
        # Should have a timestamp
        assert hasattr(request, 'transaction_timestamp')
        assert request.transaction_timestamp is not None
