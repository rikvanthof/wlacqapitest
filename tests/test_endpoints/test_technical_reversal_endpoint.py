"""Unit tests for technical reversal endpoint"""
import pytest
from unittest.mock import patch, Mock
from src.endpoints.technical_reversal_endpoint import TechnicalReversalEndpoint
from src.core.endpoint_registry import EndpointRegistry

class TestTechnicalReversalEndpoint:
    """Test technical reversal endpoint"""

    def test_endpoint_registration(self):
        """Test that endpoint is properly registered"""
        endpoint = EndpointRegistry.get_endpoint('technical_reversal')
        assert endpoint == TechnicalReversalEndpoint
        
    def test_supports_dcc(self):
        """Test DCC support detection - should be False"""
        assert TechnicalReversalEndpoint.supports_dcc() == False
        
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = TechnicalReversalEndpoint.get_dependencies()
        assert deps == ['operation_id']
        
    @patch('src.endpoints.technical_reversal_endpoint.technical_reversal_call')
    def test_call_api(self, mock_api_call):
        """Test API call execution"""
        mock_client = Mock()
        mock_request = Mock()
        mock_response = Mock()
        mock_api_call.return_value = mock_response
        
        result = TechnicalReversalEndpoint.call_api(
            mock_client, 'acq123', 'merch456', 'original_op_789', mock_request
        )
        
        mock_api_call.assert_called_once_with(
            mock_client, 'acq123', 'merch456', 'original_op_789', mock_request
        )
        assert result == mock_response

    def test_build_request_with_dcc_ignores_dcc(self):
        """Test that build_request_with_dcc ignores DCC context"""
        import pandas as pd
        from unittest.mock import Mock
        
        row = pd.Series({'test_id': 'TEST001'})
        dcc_context = Mock()  # Should be ignored
        
        # Both methods should return the same type of result
        result1 = TechnicalReversalEndpoint.build_request(row)
        result2 = TechnicalReversalEndpoint.build_request_with_dcc(row, dcc_context)
        
        # Both should have the same structure (DCC ignored)
        assert type(result1) == type(result2)
        assert hasattr(result1, 'operation_id')
        assert hasattr(result2, 'operation_id')
        assert hasattr(result1, 'reason')
        assert hasattr(result2, 'reason')

    def test_operation_id_dependency(self):
        """Test that endpoint correctly specifies operation_id dependency"""
        deps = TechnicalReversalEndpoint.get_dependencies()
        
        # Should require operation_id (not payment_id or refund_id)
        assert 'operation_id' in deps
        assert 'payment_id' not in deps
        assert 'refund_id' not in deps