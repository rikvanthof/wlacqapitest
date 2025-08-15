"""Unit tests for standalone refund endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.standalone_refund_endpoint import StandaloneRefundEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestStandaloneRefundEndpoint:
    """Test standalone refund endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('standalone_refund')
        assert endpoint == StandaloneRefundEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection"""
        assert StandaloneRefundEndpoint.supports_dcc() == True
        
    def test_get_dependencies(self):
        """Test dependency requirements - should be empty for standalone"""
        deps = StandaloneRefundEndpoint.get_dependencies()
        assert deps == []
        
    @patch('src.endpoints.standalone_refund_endpoint.standalone_refund_call')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = StandaloneRefundEndpoint.call_api(
            mock_client, 'acq123', 'merch456', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', mock_request
        )
        assert result == mock_response

    def test_build_request_method_exists(self):
        """Test that build_request method exists and callable"""
        assert hasattr(StandaloneRefundEndpoint, 'build_request')
        assert callable(StandaloneRefundEndpoint.build_request)
        
    def test_build_request_with_dcc_method_exists(self):
        """Test that build_request_with_dcc method exists and callable"""
        assert hasattr(StandaloneRefundEndpoint, 'build_request_with_dcc')
        assert callable(StandaloneRefundEndpoint.build_request_with_dcc)