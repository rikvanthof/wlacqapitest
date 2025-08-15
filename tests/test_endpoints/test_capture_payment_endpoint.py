"""Unit tests for capture payment endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.capture_payment_endpoint import CapturePaymentEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestCapturePaymentEndpoint:
    """Test capture payment endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('capture_payment')
        assert endpoint == CapturePaymentEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection"""
        assert CapturePaymentEndpoint.supports_dcc() == True  # ✅ Fixed: Actually supports DCC
        
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = CapturePaymentEndpoint.get_dependencies()
        assert deps == ['payment_id']
        
    @patch('src.endpoints.capture_payment_endpoint.capture')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = CapturePaymentEndpoint.call_api(
            mock_client, 'acq123', 'merch456', 'pay789', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', 'pay789', mock_request
        )
        assert result == mock_response