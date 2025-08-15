"""Unit tests for ping endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.ping_endpoint import PingEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestPingEndpoint:
    """Test ping endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('ping')
        assert endpoint == PingEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection - should be False"""
        assert PingEndpoint.supports_dcc() == False
        
    def test_get_dependencies(self):
        """Test dependency requirements - should be empty"""
        deps = PingEndpoint.get_dependencies()
        assert deps == []
        
    @patch('src.endpoints.ping_endpoint.ping_call')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = PingEndpoint.call_api(mock_client)
        
        mock_api_call.assert_called_once_with(mock_client)
        assert result == mock_response

    def test_build_request_returns_none(self):
        """Test that build_request returns None (no request body needed)"""
        import pandas as pd
        
        row = pd.Series({'test_id': 'PING001'})
        request = PingEndpoint.build_request(row)
        
        assert request is None

    def test_build_request_with_dcc_returns_none(self):
        """Test that build_request_with_dcc returns None and ignores DCC"""
        import pandas as pd
        from unittest.mock import Mock
        
        row = pd.Series({'test_id': 'PING001'})
        dcc_context = Mock()  # Should be ignored
        
        request = PingEndpoint.build_request_with_dcc(row, dcc_context)
        
        assert request is None

    def test_ping_simplicity(self):
        """Test that ping endpoint is truly minimal"""
        # Ping should have the simplest possible interface
        assert PingEndpoint.supports_dcc() == False
        assert PingEndpoint.get_dependencies() == []
        assert PingEndpoint.build_request(None) is None
        assert PingEndpoint.build_request_with_dcc(None, None) is None

    def test_call_api_signature(self):
        """Test that call_api has the right signature for ping"""
        import inspect
        
        sig = inspect.signature(PingEndpoint.call_api)
        params = list(sig.parameters.keys())
        
        # Should only have client parameter (and **kwargs for flexibility)
        assert 'client' in params
        # Should not require acquirer_id, merchant_id, etc.
        assert 'acquirer_id' not in params
        assert 'merchant_id' not in params