"""Integration tests for DCC functionality"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.core.dcc_manager import DCCManager
from src.core.endpoint_registry import EndpointRegistry
from src.endpoints.get_dcc_rate_endpoint import GetDCCRateEndpoint

class TestDCCIntegration:
    """Test DCC integration with the framework"""
    
    def test_dcc_endpoint_registration(self):
        """Test that DCC endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('get_dcc_rate')
        assert endpoint is not None
        assert endpoint == GetDCCRateEndpoint
        
        # Test endpoint interface
        assert hasattr(endpoint, 'call_api')
        assert hasattr(endpoint, 'build_request')
        assert hasattr(endpoint, 'get_dependencies')
        assert hasattr(endpoint, 'supports_chaining')
        assert hasattr(endpoint, 'get_output_keys')
        assert hasattr(endpoint, 'supports_dcc')
        
        # Test DCC-specific properties
        assert endpoint.supports_dcc() is True
        assert endpoint.get_dependencies() == []
        assert endpoint.supports_chaining() is True
    
    def test_payment_endpoints_support_dcc(self):
        """Test that payment endpoints support DCC"""
        dcc_supported_endpoints = ['create_payment', 'increment_payment', 'capture_payment', 'refund_payment']
        
        for call_type in dcc_supported_endpoints:
            endpoint = EndpointRegistry.get_endpoint(call_type)
            assert endpoint is not None, f"Endpoint {call_type} not found"
            assert hasattr(endpoint, 'supports_dcc'), f"Endpoint {call_type} missing supports_dcc method"
            assert endpoint.supports_dcc() is True, f"Endpoint {call_type} should support DCC"
            assert hasattr(endpoint, 'build_request_with_dcc'), f"Endpoint {call_type} missing build_request_with_dcc method"
    
    def test_dcc_manager_with_test_data(self):
        """Test DCC manager with actual test data"""
        manager = DCCManager()
        
        # Test row from chain 7
        row = pd.Series({
            'test_id': 'API0050',
            'call_type': 'create_payment',
            'use_dcc': 'True',
            'dcc_target_currency': 'EUR',
            'amount': 555,
            'currency': 'GBP'
        })
        
        # Should perform DCC inquiry
        assert manager.should_perform_dcc_inquiry(row) is True
        
        # Should determine PAYMENT transaction type
        assert manager.determine_transaction_type('create_payment') == 'PAYMENT'
        assert manager.determine_transaction_type('capture_payment') == 'PAYMENT'
    
    def test_dcc_context_chain_management(self):
        """Test DCC context management across chain steps"""
        manager = DCCManager()
        chain_id = 'chain7'
        
        # Get initial context
        context = manager.get_chain_context(chain_id)
        assert context.rate_reference_id is None
        
        # ✅ Fix: Simulate DCC response with correct structure
        mock_response = Mock()
        mock_response.proposal = Mock()
        mock_response.proposal.rate_reference_id = 'rate_ref_12345'
        
        # Set up original_amount
        mock_response.proposal.original_amount = Mock()
        mock_response.proposal.original_amount.amount = 555
        mock_response.proposal.original_amount.currency_code = 'GBP'
        mock_response.proposal.original_amount.number_of_decimals = 2
        
        # Set up resulting_amount
        mock_response.proposal.resulting_amount = Mock()
        mock_response.proposal.resulting_amount.amount = 625
        mock_response.proposal.resulting_amount.currency_code = 'EUR'
        mock_response.proposal.resulting_amount.number_of_decimals = 2
        
        # ✅ Fix: Set up rate with nested structure
        mock_response.proposal.rate = Mock()
        mock_response.proposal.rate.inverted_exchange_rate = 0.888  # Real float, not Mock
        
        # Update context
        manager.update_context_from_dcc_response(chain_id, mock_response)
        
        # Verify context was updated
        updated_context = manager.get_chain_context(chain_id)
        assert updated_context.rate_reference_id == 'rate_ref_12345'
        assert updated_context.original_amount['amount'] == 555
        assert updated_context.original_amount['currency_code'] == 'GBP'
        assert updated_context.resulting_amount['amount'] == 625
        assert updated_context.resulting_amount['currency_code'] == 'EUR'
        assert updated_context.inverted_exchange_rate == 0.888
    
    @patch('src.endpoints.get_dcc_rate_endpoint.GetDCCRateEndpoint.call_api')
    def test_dcc_request_building(self, mock_call_api):
        """Test DCC request building with actual test data"""
        # Test row from chain 7
        row = pd.Series({
            'test_id': 'API0050',
            'amount': 555,
            'currency': 'GBP',
            'dcc_target_currency': 'EUR'
        })

        # Build DCC request
        endpoint = EndpointRegistry.get_endpoint('get_dcc_rate')
        request = endpoint.build_request(row, 'PAYMENT')

        # ✅ Fix: Use correct field structure
        assert hasattr(request, 'operation_id')
        assert 'API0050:dcc:' in request.operation_id
        assert request.transaction.amount.amount == 555  # ✅ Fixed path
        assert request.transaction.amount.currency_code == 'GBP'  # ✅ Fixed path
        assert request.target_currency == 'EUR'
    
    def test_registry_dcc_support_detection(self):
        """Test registry can detect DCC support"""
        # Should support DCC
        assert EndpointRegistry.endpoint_supports_dcc('create_payment') is True
        assert EndpointRegistry.endpoint_supports_dcc('increment_payment') is True
        assert EndpointRegistry.endpoint_supports_dcc('capture_payment') is True
        assert EndpointRegistry.endpoint_supports_dcc('refund_payment') is True
        assert EndpointRegistry.endpoint_supports_dcc('get_dcc_rate') is True
        
        # Should not support DCC
        assert EndpointRegistry.endpoint_supports_dcc('get_payment') is False
        assert EndpointRegistry.endpoint_supports_dcc('get_refund') is False