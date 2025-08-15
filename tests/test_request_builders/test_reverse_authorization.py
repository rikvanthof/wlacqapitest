"""Unit tests for reverse authorization request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.reverse_authorization import build_reverse_authorization_request

class TestBuildReverseAuthorizationRequest:
    """Test reverse authorization request building"""

    def test_build_complete_request(self):
        """Test building complete reverse authorization request"""
        row = pd.Series({
            'test_id': 'REV001',
            'amount': 500,
            'currency': 'GBP'
        })
        
        with patch('src.request_builders.reverse_authorization.generate_random_string', return_value='rev123'):
            request = build_reverse_authorization_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'REV001:rev123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'reversal_amount')
            
            # Verify reversal amount
            assert request.reversal_amount.amount == 500
            assert request.reversal_amount.currency_code == 'GBP'
            assert request.reversal_amount.number_of_decimals == 2

    def test_build_full_reversal_without_amount(self):
        """Test building full reversal (no amount specified)"""
        row = pd.Series({
            'test_id': 'REV002',
            'currency': 'EUR'
        })
        
        with patch('src.request_builders.reverse_authorization.generate_random_string', return_value='rev456'):
            request = build_reverse_authorization_request(row)
            
            # Should not have reversal_amount for full reversal
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'REV002:rev456'
            # For full reversal, reversal_amount should be None or not set
            assert not hasattr(request, 'reversal_amount') or request.reversal_amount is None

    def test_build_with_dcc_context(self):
        """Test building request with DCC context"""
        row = pd.Series({
            'test_id': 'REV003',
            'amount': 1000,
            'currency': 'GBP'
        })
        
        # Mock DCC context
        dcc_context = Mock()
        dcc_context.rate_reference_id = 'rate_ref_789'
        dcc_context.resulting_amount = {
            'amount': 1150,
            'currency_code': 'EUR', 
            'number_of_decimals': 2
        }
        dcc_context.inverted_exchange_rate = 0.869
        
        with patch('src.request_builders.reverse_authorization.generate_random_string', return_value='rev789'):
            request = build_reverse_authorization_request(row, dcc_context)
            
            # Verify main amount uses DCC resulting amount
            assert request.reversal_amount.amount == 1150
            assert request.reversal_amount.currency_code == 'EUR'
            
            # Verify DCC fields
            assert hasattr(request, 'dynamic_currency_conversion')
            dcc_data = request.dynamic_currency_conversion
            assert dcc_data.amount == 1000  # Original merchant amount
            assert dcc_data.currency_code == 'GBP'  # Original merchant currency
            assert dcc_data.conversion_rate == 0.869

    def test_request_cleaning_called(self):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'REV004',
            'amount': 250,
            'currency': 'USD'
        })
        
        with patch('src.request_builders.reverse_authorization.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_reverse_authorization_request(row)
            mock_clean.assert_called_once()

    def test_build_partial_reversal_with_amount(self):
        """Test building partial reversal request with specific amount"""
        row = pd.Series({
            'test_id': 'REV_PARTIAL_001',
            'amount': 500,
            'currency': 'EUR'
        })
        
        request = build_reverse_authorization_request(row)
        
        # Should have reversal_amount for partial reversal
        assert hasattr(request, 'reversal_amount')
        assert request.reversal_amount.amount == 500
        assert request.reversal_amount.currency_code == 'EUR'
        assert request.reversal_amount.number_of_decimals == 2

    def test_build_full_reversal_no_amount(self):
        """Test building full reversal request without amount"""
        row = pd.Series({
            'test_id': 'REV_FULL_001'
        })
        
        request = build_reverse_authorization_request(row)
        
        # Should NOT have reversal_amount for full reversal
        assert not hasattr(request, 'reversal_amount') or request.reversal_amount is None

    def test_build_full_reversal_empty_amount(self):
        """Test building full reversal with empty amount"""
        row = pd.Series({
            'test_id': 'REV_FULL_002',
            'amount': '',
            'currency': 'EUR'
        })
        
        request = build_reverse_authorization_request(row)
        
        # Should NOT have reversal_amount for empty amount
        assert not hasattr(request, 'reversal_amount') or request.reversal_amount is None

    def test_build_full_reversal_zero_amount(self):
        """Test building full reversal with zero amount"""
        row = pd.Series({
            'test_id': 'REV_FULL_003',
            'amount': 0,
            'currency': 'EUR'
        })
        
        request = build_reverse_authorization_request(row)
        
        # Should NOT have reversal_amount for zero amount
        assert not hasattr(request, 'reversal_amount') or request.reversal_amount is None

    def test_build_with_dcc_partial_reversal(self):
        """Test building partial reversal with DCC"""
        row = pd.Series({
            'test_id': 'REV_DCC_001',
            'amount': 1000,
            'currency': 'GBP'
        })
        
        # Mock DCC context
        from unittest.mock import Mock
        dcc_context = Mock()
        dcc_context.rate_reference_id = 'rate_ref_123'
        dcc_context.resulting_amount = {
            'amount': 1150,
            'currency_code': 'EUR',
            'number_of_decimals': 2
        }
        dcc_context.inverted_exchange_rate = 0.869
        
        request = build_reverse_authorization_request(row, dcc_context)
        
        # Should use DCC amount for reversal
        assert request.reversal_amount.amount == 1150
        assert request.reversal_amount.currency_code == 'EUR'
        assert hasattr(request, 'dynamic_currency_conversion')

    def test_build_with_string_amount(self):
        """Test building reversal with string amount"""
        row = pd.Series({
            'test_id': 'REV_STRING_001',
            'amount': '750.00',  # String amount
            'currency': 'USD'
        })
        
        request = build_reverse_authorization_request(row)
        
        # Should handle string amounts correctly
        assert request.reversal_amount.amount == 750
        assert request.reversal_amount.currency_code == 'USD'