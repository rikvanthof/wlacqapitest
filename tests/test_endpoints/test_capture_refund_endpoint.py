"""Unit tests for capture refund endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.capture_refund_endpoint import CaptureRefundEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestCaptureRefundEndpoint:
    """Test capture refund endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('capture_refund')
        assert endpoint == CaptureRefundEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection - should be False for captures"""
        assert CaptureRefundEndpoint.supports_dcc() == False
        
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = CaptureRefundEndpoint.get_dependencies()
        assert deps == ['refund_id']
        
    @patch('src.endpoints.capture_refund_endpoint.capture_refund_call')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = CaptureRefundEndpoint.call_api(
            mock_client, 'acq123', 'merch456', 'ref789', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', 'ref789', mock_request
        )
        assert result == mock_response