"""Unit tests for account verification endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.account_verification_endpoint import AccountVerificationEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestAccountVerificationEndpoint:
    """Test account verification endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('process_account_verification')
        assert endpoint == AccountVerificationEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection"""
        assert AccountVerificationEndpoint.supports_dcc() == True
        
    def test_get_dependencies(self):
        """Test dependency requirements - should be empty for standalone"""
        deps = AccountVerificationEndpoint.get_dependencies()
        assert deps == []
        
    @patch('src.endpoints.account_verification_endpoint.account_verification_call')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = AccountVerificationEndpoint.call_api(
            mock_client, 'acq123', 'merch456', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', mock_request
        )
        assert result == mock_response

    def test_build_request_method_exists(self):
        """Test that build_request method exists and callable"""
        assert hasattr(AccountVerificationEndpoint, 'build_request')
        assert callable(AccountVerificationEndpoint.build_request)
        
    def test_build_request_with_dcc_method_exists(self):
        """Test that build_request_with_dcc method exists and callable"""
        assert hasattr(AccountVerificationEndpoint, 'build_request_with_dcc')
        assert callable(AccountVerificationEndpoint.build_request_with_dcc)

    def test_complex_features_support(self):
        """Test that endpoint supports complex payment features"""
        # Account verification should support all the same features as create_payment
        assert AccountVerificationEndpoint.supports_dcc() == True
        assert AccountVerificationEndpoint.get_dependencies() == []
        
        # Should be standalone operation (no payment_id dependency)
        deps = AccountVerificationEndpoint.get_dependencies()
        assert 'payment_id' not in deps
        assert 'refund_id' not in deps
        assert 'operation_id' not in deps