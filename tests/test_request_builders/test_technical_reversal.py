"""Unit tests for technical reversal request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.technical_reversal import build_technical_reversal_request

class TestBuildTechnicalReversalRequest:
    """Test technical reversal request building"""

    def test_build_basic_request(self):
        """Test building basic technical reversal request"""
        row = pd.Series({
            'test_id': 'TECH_REV001'
        })
        
        with patch('src.request_builders.technical_reversal.generate_random_string', return_value='techrev123'):
            request = build_technical_reversal_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'TECH_REV001:techrev123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'reason')
            assert request.reason == 'TIMEOUT'  # Default reason
            
            # Should NOT have complex fields
            assert not hasattr(request, 'references')
            assert not hasattr(request, 'amount')
            assert not hasattr(request, 'dynamic_currency_conversion')
            assert not hasattr(request, 'card_payment_data')

    def test_build_with_custom_reason(self):
        """Test building request with custom reversal reason"""
        row = pd.Series({
            'test_id': 'TECH_REV002',
            'reversal_reason': 'NETWORK_ERROR'
        })
        
        with patch('src.request_builders.technical_reversal.generate_random_string', return_value='techrev456'):
            request = build_technical_reversal_request(row)
            
            # Verify custom reason
            assert request.reason == 'NETWORK_ERROR'
            assert request.operation_id == 'TECH_REV002:techrev456'

    def test_operation_id_format(self):
        """Test operation ID format"""
        row = pd.Series({
            'test_id': 'TECH_REV003'
        })
        
        with patch('src.request_builders.technical_reversal.generate_random_string', return_value='techrev789'):
            request = build_technical_reversal_request(row)
            
            # Verify operation ID format
            assert request.operation_id == 'TECH_REV003:techrev789'

    def test_minimal_request_structure(self):
        """Test that request has only minimal required fields"""
        row = pd.Series({
            'test_id': 'TECH_REV004'
        })
        
        request = build_technical_reversal_request(row)
        request_dict = request.to_dictionary()
        
        # Should only have the minimal required fields
        expected_keys = {'operationId', 'transactionTimestamp', 'reason'}
        actual_keys = set(request_dict.keys())
        
        # All expected keys should be present
        assert expected_keys.issubset(actual_keys)
        
        # Should not have complex fields
        unexpected_keys = {'amount', 'references', 'dynamicCurrencyConversion', 'cardPaymentData'}
        assert not any(key in actual_keys for key in unexpected_keys)

    def test_request_cleaning_called(self):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'TECH_REV005'
        })
        
        with patch('src.request_builders.technical_reversal.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_technical_reversal_request(row)
            mock_clean.assert_called_once()