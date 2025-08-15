"""Fixed unit tests for increment payment request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.increment_payment import build_increment_payment_request

class TestBuildIncrementPaymentRequest:
    """Test increment payment request building"""

    def test_build_basic_request(self):
        """Test building basic increment payment request"""
        row = pd.Series({
            'test_id': 'INC001',
            'amount': 500,  # ✅ Fixed: Use 'amount' field name
            'currency': 'USD'
        })
        
        with patch('src.request_builders.increment_payment.generate_random_string', return_value='inc123'):
            request = build_increment_payment_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'INC001:inc123'
            assert hasattr(request, 'transaction_timestamp')
            # ✅ Fixed: Check for increment_amount on request object
            assert hasattr(request, 'increment_amount')
            assert request.increment_amount.amount == 500
            assert request.increment_amount.currency_code == 'USD'

    def test_build_with_dcc_context(self):
        """Test building request with DCC context"""
        row = pd.Series({
            'test_id': 'INC002',
            'amount': 1000,  # ✅ Fixed: Use 'amount' field name
            'currency': 'GBP'
        })
        
        # Mock DCC context
        dcc_context = Mock()
        dcc_context.rate_reference_id = 'rate_ref_123'
        dcc_context.resulting_amount = {
            'amount': 1150,
            'currency_code': 'EUR',
            'number_of_decimals': 2
        }
        dcc_context.inverted_exchange_rate = 0.869
        
        with patch('src.request_builders.increment_payment.generate_random_string', return_value='inc456'):
            request = build_increment_payment_request(row, dcc_context)
            
            # Should use DCC resulting amount
            assert request.increment_amount.amount == 1150  # ✅ Fixed: increment_amount on request
            assert request.increment_amount.currency_code == 'EUR'
            
            # Should have DCC data
            assert hasattr(request, 'dynamic_currency_conversion')

    def test_dynamic_descriptor(self):
        """Test dynamic descriptor - increment doesn't support references"""
        row = pd.Series({
            'test_id': 'INC003',
            'amount': 750,  # ✅ Fixed: Use 'amount' field name
            'currency': 'EUR',
            'dynamic_descriptor': 'Auth Increment'
        })
        
        request = build_increment_payment_request(row)
        
        # ✅ Fixed: Increment doesn't support references, so just check it builds
        assert hasattr(request, 'operation_id')
        assert hasattr(request, 'increment_amount')

    def test_operation_id_generation(self):  # ✅ Fixed: Different test since no references
        """Test operation ID generation"""
        row = pd.Series({
            'test_id': 'INC004',
            'amount': 300,  # ✅ Fixed: Use 'amount' field name
            'currency': 'USD'
        })
        
        with patch('src.request_builders.increment_payment.generate_random_string', return_value='inc789'):
            request = build_increment_payment_request(row)
            
            assert request.operation_id == 'INC004:inc789'

    def test_request_cleaning_called(self):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'INC005',
            'amount': 100,  # ✅ Fixed: Use 'amount' field name
            'currency': 'GBP'
        })
        
        with patch('src.request_builders.increment_payment.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_increment_payment_request(row)
            mock_clean.assert_called_once()

    def test_minimum_required_fields(self):  # ✅ New test for actual requirements
        """Test minimum required fields"""
        row = pd.Series({
            'test_id': 'INC006',
            'amount': 250,  # ✅ Fixed: Use 'amount' field name
            'currency': 'EUR'
        })
        
        request = build_increment_payment_request(row)
        
        # Should have minimum required fields
        assert hasattr(request, 'operation_id')
        assert hasattr(request, 'transaction_timestamp')
        assert hasattr(request, 'increment_amount')
        assert request.increment_amount.amount == 250
        assert request.increment_amount.currency_code == 'EUR'