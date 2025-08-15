"""Unit tests for get payment endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.get_payment_endpoint import GetPaymentEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestGetPaymentEndpoint:
    """Test get payment endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('get_payment')
        assert endpoint == GetPaymentEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection - should be False for GET operations"""
        assert GetPaymentEndpoint.supports_dcc() == False
        
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = GetPaymentEndpoint.get_dependencies()
        assert deps == ['payment_id']
        
    @patch('src.endpoints.get_payment_endpoint.get_payment')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = GetPaymentEndpoint.call_api(
            mock_client, 'acq123', 'merch456', 'pay789'
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', 'pay789'
        )
        assert result == mock_response

    def test_build_request_returns_none(self):
        """Test that build_request returns None (no request body for GET)"""
        import pandas as pd
        
        row = pd.Series({'test_id': 'GET001'})
        request = GetPaymentEndpoint.build_request(row)
        
        assert request is None

    def test_build_request_with_dcc_returns_none(self):
        """Test that build_request_with_dcc returns None (no DCC for GET)"""
        import pandas as pd
        from unittest.mock import Mock
        
        row = pd.Series({'test_id': 'GET001'})
        dcc_context = Mock()
        
        request = GetPaymentEndpoint.build_request_with_dcc(row, None, dcc_context)
        
        assert request is None