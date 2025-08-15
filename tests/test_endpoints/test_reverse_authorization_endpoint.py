"""Unit tests for reverse authorization endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.reverse_authorization_endpoint import ReverseAuthorizationEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestReverseAuthorizationEndpoint:
    """Test reverse authorization endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('reverse_authorization')
        assert endpoint == ReverseAuthorizationEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection"""
        assert ReverseAuthorizationEndpoint.supports_dcc() == True
        
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = ReverseAuthorizationEndpoint.get_dependencies()
        assert deps == ['payment_id']
        
    @patch('src.endpoints.reverse_authorization_endpoint.reverse_authorization_call')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = ReverseAuthorizationEndpoint.call_api(
            mock_client, 'acq123', 'merch456', 'pay789', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', 'pay789', mock_request
        )
        assert result == mock_response