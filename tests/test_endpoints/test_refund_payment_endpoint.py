"""Unit tests for refund payment endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.refund_payment_endpoint import RefundPaymentEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestRefundPaymentEndpoint:
    """Test refund payment endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('refund_payment')
        assert endpoint == RefundPaymentEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection"""
        assert RefundPaymentEndpoint.supports_dcc() == True
        
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = RefundPaymentEndpoint.get_dependencies()
        assert deps == ['payment_id']
        
    @patch('src.endpoints.refund_payment_endpoint.refund')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = RefundPaymentEndpoint.call_api(
            mock_client, 'acq123', 'merch456', 'pay789', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', 'pay789', mock_request
        )
        assert result == mock_response