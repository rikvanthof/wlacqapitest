"""Unit tests for reverse refund authorization endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.reverse_refund_authorization_endpoint import ReverseRefundAuthorizationEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestReverseRefundAuthorizationEndpoint:
    """Test reverse refund authorization endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('reverse_refund_authorization')
        assert endpoint == ReverseRefundAuthorizationEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection - should be False"""
        assert ReverseRefundAuthorizationEndpoint.supports_dcc() == False
        
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = ReverseRefundAuthorizationEndpoint.get_dependencies()
        assert deps == ['refund_id']
        
    @patch('src.endpoints.reverse_refund_authorization_endpoint.reverse_refund_authorization_call')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = ReverseRefundAuthorizationEndpoint.call_api(
            mock_client, 'acq123', 'merch456', 'ref789', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', 'ref789', mock_request
        )
        assert result == mock_response

    def test_build_request_with_dcc_ignores_dcc(self):
        """Test that build_request_with_dcc ignores DCC context"""
        import pandas as pd
        from unittest.mock import Mock
        
        row = pd.Series({'test_id': 'TEST001'})
        dcc_context = Mock()  # Should be ignored
        
        # Both methods should return the same result
        result1 = ReverseRefundAuthorizationEndpoint.build_request(row)
        result2 = ReverseRefundAuthorizationEndpoint.build_request_with_dcc(row, dcc_context)
        
        # Both should have the same structure (DCC ignored)
        assert type(result1) == type(result2)
        assert hasattr(result1, 'operation_id')
        assert hasattr(result2, 'operation_id')