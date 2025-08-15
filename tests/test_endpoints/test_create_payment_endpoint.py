"""Unit tests for create payment endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.create_payment_endpoint import CreatePaymentEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestCreatePaymentEndpoint:
    """Test create payment endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('create_payment')
        assert endpoint == CreatePaymentEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection"""
        assert CreatePaymentEndpoint.supports_dcc() == True
        
    def test_get_dependencies(self):
        """Test dependency requirements - should be empty for standalone"""
        deps = CreatePaymentEndpoint.get_dependencies()
        assert deps == []
        
    @patch('src.endpoints.create_payment_endpoint.create_payment')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = CreatePaymentEndpoint.call_api(
            mock_client, 'acq123', 'merch456', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', mock_request
        )
        assert result == mock_response

    def test_build_request_method_exists(self):
        """Test that build_request method exists and callable"""
        assert hasattr(CreatePaymentEndpoint, 'build_request')
        assert callable(CreatePaymentEndpoint.build_request)
        
    def test_build_request_with_dcc_method_exists(self):
        """Test that build_request_with_dcc method exists and callable"""
        assert hasattr(CreatePaymentEndpoint, 'build_request_with_dcc')
        assert callable(CreatePaymentEndpoint.build_request_with_dcc)