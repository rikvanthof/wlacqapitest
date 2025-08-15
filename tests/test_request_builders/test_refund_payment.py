"""Fixed unit tests for refund payment request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.refund_payment import build_refund_payment_request

class TestBuildRefundPaymentRequest:
    """Test refund payment request building"""

    def test_build_basic_request(self):
        """Test building basic refund payment request"""
        row = pd.Series({
            'test_id': 'REF001',
            'amount': 750,  # ✅ Amount is required
            'currency': 'EUR'
        })
        
        with patch('src.request_builders.refund_payment.generate_random_string', return_value='ref123'):
            request = build_refund_payment_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'REF001:ref123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'references')

    def test_build_with_amount(self):
        """Test building request with amount"""
        row = pd.Series({
            'test_id': 'REF002',
            'amount': 750,
            'currency': 'EUR'
        })
        
        request = build_refund_payment_request(row)
        
        # Should have amount when specified
        assert hasattr(request, 'amount')
        assert request.amount.amount == 750
        assert request.amount.currency_code == 'EUR'

    def test_build_with_dcc_context(self):
        """Test building request with DCC context"""
        row = pd.Series({
            'test_id': 'REF003',
            'amount': 1000,
            'currency': 'USD'
        })
        
        # Mock DCC context
        dcc_context = Mock()
        dcc_context.rate_reference_id = 'rate_ref_456'
        dcc_context.resulting_amount = {
            'amount': 850,
            'currency_code': 'EUR',
            'number_of_decimals': 2
        }
        dcc_context.inverted_exchange_rate = 1.176
        
        with patch('src.request_builders.refund_payment.generate_random_string', return_value='ref456'):
            request = build_refund_payment_request(row, dcc_context)
            
            # Should use DCC resulting amount
            assert request.amount.amount == 850
            assert request.amount.currency_code == 'EUR'
            
            # Should have DCC data
            assert hasattr(request, 'dynamic_currency_conversion')
            dcc_data = request.dynamic_currency_conversion
            assert dcc_data.amount == 1000  # Original amount
            assert dcc_data.currency_code == 'USD'  # Original currency

    def test_partial_refund(self):  # ✅ Fixed: Test partial refund instead of full
        """Test partial refund with specific amount"""
        row = pd.Series({
            'test_id': 'REF004',
            'amount': 500,  # Partial refund amount
            'currency': 'USD'
        })
        
        request = build_refund_payment_request(row)
        
        # Should have specified amount
        assert request.amount.amount == 500
        assert request.amount.currency_code == 'USD'

    def test_dynamic_descriptor(self):
        """Test dynamic descriptor"""
        row = pd.Series({
            'test_id': 'REF005',
            'amount': 300,  # ✅ Required field
            'currency': 'EUR',
            'dynamic_descriptor': 'Refund Processing'
        })
        
        request = build_refund_payment_request(row)
        
        assert request.references.dynamic_descriptor == 'Refund Processing'

    def test_merchant_reference_generation(self):
        """Test merchant reference generation"""
        row = pd.Series({
            'test_id': 'REF006',
            'amount': 200,  # ✅ Required field
            'currency': 'GBP'
        })
        
        with patch('src.request_builders.refund_payment.generate_random_string', return_value='ref789'):
            request = build_refund_payment_request(row)
            
            assert request.references.merchant_reference == 'REF006:ref789'

    def test_request_cleaning_called(self):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'REF007',
            'amount': 150,  # ✅ Required field
            'currency': 'USD'
        })
        
        with patch('src.request_builders.refund_payment.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_refund_payment_request(row)
            mock_clean.assert_called_once()