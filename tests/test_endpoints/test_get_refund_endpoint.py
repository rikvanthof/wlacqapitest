"""Unit tests for get refund endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.get_refund_endpoint import GetRefundEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestGetRefundEndpoint:
    """Test get refund endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('get_refund')
        assert endpoint == GetRefundEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection - should be False for GET operations"""
        assert GetRefundEndpoint.supports_dcc() == False
        
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = GetRefundEndpoint.get_dependencies()
        assert deps == ['refund_id']
        
    @patch('src.endpoints.get_refund_endpoint.get_refund')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = GetRefundEndpoint.call_api(
            mock_client, 'acq123', 'merch456', 'ref789'
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', 'ref789'
        )
        assert result == mock_response

    def test_build_request_returns_none(self):
        """Test that build_request returns None (no request body for GET)"""
        import pandas as pd
        
        row = pd.Series({'test_id': 'GET_REF001'})
        request = GetRefundEndpoint.build_request(row)
        
        assert request is None

    def test_build_request_with_dcc_returns_none(self):
        """Test that build_request_with_dcc returns None (no DCC for GET)"""
        import pandas as pd
        from unittest.mock import Mock
        
        row = pd.Series({'test_id': 'GET_REF001'})
        dcc_context = Mock()
        
        request = GetRefundEndpoint.build_request_with_dcc(row, None, dcc_context)
        
        assert request is None