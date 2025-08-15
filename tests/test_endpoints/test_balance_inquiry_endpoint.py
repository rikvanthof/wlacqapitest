"""Unit tests for balance inquiry endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.balance_inquiry_endpoint import BalanceInquiryEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestBalanceInquiryEndpoint:
    """Test balance inquiry endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('process_balance_inquiry')
        assert endpoint == BalanceInquiryEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection"""
        assert BalanceInquiryEndpoint.supports_dcc() == True
        
    def test_get_dependencies(self):
        """Test dependency requirements - should be empty for standalone"""
        deps = BalanceInquiryEndpoint.get_dependencies()
        assert deps == []
        
    @patch('src.endpoints.balance_inquiry_endpoint.balance_inquiry_call')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = BalanceInquiryEndpoint.call_api(
            mock_client, 'acq123', 'merch456', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', mock_request
        )
        assert result == mock_response

    def test_build_request_method_exists(self):
        """Test that build_request method exists and callable"""
        assert hasattr(BalanceInquiryEndpoint, 'build_request')
        assert callable(BalanceInquiryEndpoint.build_request)
        
    def test_build_request_with_dcc_method_exists(self):
        """Test that build_request_with_dcc method exists and callable"""
        assert hasattr(BalanceInquiryEndpoint, 'build_request_with_dcc')
        assert callable(BalanceInquiryEndpoint.build_request_with_dcc)

    def test_complex_features_support(self):
        """Test that endpoint supports complex payment features"""
        # Balance inquiry should support all the same features as create_payment and account_verification
        assert BalanceInquiryEndpoint.supports_dcc() == True
        assert BalanceInquiryEndpoint.get_dependencies() == []
        
        # Should be standalone operation (no dependencies)
        deps = BalanceInquiryEndpoint.get_dependencies()
        assert 'payment_id' not in deps
        assert 'refund_id' not in deps
        assert 'operation_id' not in deps

    def test_final_endpoint_completion(self):
        """Test that this completes our endpoint implementation"""
        # This is the 8th and final major endpoint
        endpoint = EndpointRegistry.get_endpoint('process_balance_inquiry')
        assert endpoint is not None
        assert endpoint == BalanceInquiryEndpoint
        
        # Should have all the required methods
        required_methods = ['call_api', 'build_request', 'build_request_with_dcc', 'supports_dcc', 'get_dependencies']
        for method in required_methods:
            assert hasattr(endpoint, method)
            assert callable(getattr(endpoint, method))