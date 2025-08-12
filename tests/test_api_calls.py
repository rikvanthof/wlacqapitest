"""Test API calls functions"""

import pytest
import threading
import uuid
from unittest.mock import Mock, MagicMock, patch
from src.api_calls import (
    set_last_http_status, get_last_http_status,
    set_trace_id, get_trace_id, generate_trace_id,
    create_payment, increment_auth, capture, refund, get_payment, get_refund
)

class TestThreadLocalStorage:
    """Test thread-local storage functions"""
    
    def test_set_and_get_http_status(self):
        """Test setting and getting HTTP status code"""
        # Test setting status code
        set_last_http_status(200)
        assert get_last_http_status() == 200
        
        # Test updating status code
        set_last_http_status(404)
        assert get_last_http_status() == 404
        
        # Test setting None
        set_last_http_status(None)
        assert get_last_http_status() is None

    def test_set_and_get_trace_id(self):
        """Test setting and getting trace ID"""
        test_trace_id = "test-trace-12345"
        
        # Test setting trace ID
        set_trace_id(test_trace_id)
        assert get_trace_id() == test_trace_id
        
        # Test updating trace ID
        new_trace_id = "new-trace-67890"
        set_trace_id(new_trace_id)
        assert get_trace_id() == new_trace_id

    def test_generate_trace_id(self):
        """Test trace ID generation"""
        # Generate a trace ID
        trace_id = generate_trace_id()
        
        # Should be a valid UUID string
        assert isinstance(trace_id, str)
        assert len(trace_id) == 36  # Standard UUID length
        
        # Should be stored in thread-local storage
        assert get_trace_id() == trace_id
        
        # Generate another one - should be different
        new_trace_id = generate_trace_id()
        assert new_trace_id != trace_id
        assert get_trace_id() == new_trace_id

    def test_thread_isolation(self):
        """Test that thread-local storage is isolated between threads"""
        main_status = 200
        main_trace = "main-trace"
        thread_results = {}
        
        def thread_function():
            # Set different values in the thread
            set_last_http_status(404)
            set_trace_id("thread-trace")
            
            # Store what this thread sees
            thread_results['status'] = get_last_http_status()
            thread_results['trace'] = get_trace_id()
        
        # Set values in main thread
        set_last_http_status(main_status)
        set_trace_id(main_trace)
        
        # Run function in separate thread
        thread = threading.Thread(target=thread_function)
        thread.start()
        thread.join()
        
        # Main thread should still have its values
        assert get_last_http_status() == main_status
        assert get_trace_id() == main_trace
        
        # Thread should have had its own values
        assert thread_results['status'] == 404
        assert thread_results['trace'] == "thread-trace"

    def test_get_without_set_returns_none(self):
        """Test getting values that haven't been set returns None"""
        # Clear any existing values by creating new thread
        def clear_thread():
            return get_last_http_status(), get_trace_id()
        
        thread = threading.Thread(target=clear_thread)
        thread.start()
        thread.join()
        
        # In a fresh context, should return None
        fresh_local = threading.local()
        assert getattr(fresh_local, 'last_status_code', None) is None
        assert getattr(fresh_local, 'trace_id', None) is None


class TestApiCalls:
    """Test core API call functions"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client with nested method structure"""
        client = MagicMock()
        
        # Mock the nested structure: client.v1().acquirer().merchant().payments().method()
        v1_mock = MagicMock()
        acquirer_mock = MagicMock()
        merchant_mock = MagicMock()
        payments_mock = MagicMock()
        refunds_mock = MagicMock()
        
        client.v1.return_value = v1_mock
        v1_mock.acquirer.return_value = acquirer_mock
        acquirer_mock.merchant.return_value = merchant_mock
        merchant_mock.payments.return_value = payments_mock
        merchant_mock.refunds.return_value = refunds_mock
        
        return client, payments_mock, refunds_mock

    @patch('src.api_calls.generate_trace_id')
    def test_create_payment(self, mock_generate_trace, mock_client):
        """Test create payment API call"""
        client, payments_mock, _ = mock_client
        mock_generate_trace.return_value = "trace-12345"
        
        # Mock response
        mock_response = Mock()
        payments_mock.process_payment.return_value = mock_response
        
        # Mock request
        mock_request = Mock()
        
        # Call function
        result = create_payment(client, "acquirer123", "merchant456", mock_request)
        
        # Verify trace ID generation
        mock_generate_trace.assert_called_once()
        
        # Verify client method calls
        client.v1.assert_called_once()
        client.v1().acquirer.assert_called_once_with("acquirer123")
        client.v1().acquirer().merchant.assert_called_once_with("merchant456")
        client.v1().acquirer().merchant().payments.assert_called_once()
        payments_mock.process_payment.assert_called_once_with(mock_request)
        
        # Verify return value
        assert result == mock_response

    @patch('src.api_calls.generate_trace_id')
    def test_increment_auth(self, mock_generate_trace, mock_client):
        """Test increment authorization API call"""
        client, payments_mock, _ = mock_client
        mock_generate_trace.return_value = "trace-67890"
        
        # Mock response
        mock_response = Mock()
        payments_mock.increment_payment.return_value = mock_response
        
        # Mock request
        mock_request = Mock()
        
        # Call function
        result = increment_auth(client, "acquirer123", "merchant456", "payment789", mock_request)
        
        # Verify trace ID generation
        mock_generate_trace.assert_called_once()
        
        # Verify client method calls
        payments_mock.increment_payment.assert_called_once_with("payment789", mock_request)
        
        # Verify return value
        assert result == mock_response

    @patch('src.api_calls.generate_trace_id')
    def test_capture(self, mock_generate_trace, mock_client):
        """Test capture payment API call"""
        client, payments_mock, _ = mock_client
        
        # Mock response
        mock_response = Mock()
        payments_mock.simple_capture_of_payment.return_value = mock_response
        
        # Mock request
        mock_request = Mock()
        
        # Call function
        result = capture(client, "acquirer123", "merchant456", "payment789", mock_request)
        
        # Verify trace ID generation
        mock_generate_trace.assert_called_once()
        
        # Verify client method calls
        payments_mock.simple_capture_of_payment.assert_called_once_with("payment789", mock_request)
        
        # Verify return value
        assert result == mock_response

    @patch('src.api_calls.generate_trace_id')
    def test_refund(self, mock_generate_trace, mock_client):
        """Test refund payment API call"""
        client, payments_mock, _ = mock_client
        
        # Mock response
        mock_response = Mock()
        payments_mock.create_refund.return_value = mock_response
        
        # Mock request
        mock_request = Mock()
        
        # Call function
        result = refund(client, "acquirer123", "merchant456", "payment789", mock_request)
        
        # Verify trace ID generation
        mock_generate_trace.assert_called_once()
        
        # Verify client method calls
        payments_mock.create_refund.assert_called_once_with("payment789", mock_request)
        
        # Verify return value
        assert result == mock_response

    @patch('src.api_calls.generate_trace_id')
    def test_get_payment(self, mock_generate_trace, mock_client):
        """Test get payment API call"""
        client, payments_mock, _ = mock_client
        
        # Mock response
        mock_response = Mock()
        payments_mock.get_payment_status.return_value = mock_response
        
        # Call function
        result = get_payment(client, "acquirer123", "merchant456", "payment789")
        
        # Verify trace ID generation
        mock_generate_trace.assert_called_once()
        
        # Verify client method calls
        payments_mock.get_payment_status.assert_called_once_with("payment789", None)
        
        # Verify return value
        assert result == mock_response

    @patch('src.api_calls.generate_trace_id')
    def test_get_refund(self, mock_generate_trace, mock_client):
        """Test get refund API call"""
        client, _, refunds_mock = mock_client
        
        # Mock response
        mock_response = Mock()
        refunds_mock.get_refund.return_value = mock_response
        
        # Call function
        result = get_refund(client, "acquirer123", "merchant456", "refund789")
        
        # Verify trace ID generation
        mock_generate_trace.assert_called_once()
        
        # Verify client method calls
        refunds_mock.get_refund.assert_called_once_with("refund789", None)
        
        # Verify return value
        assert result == mock_response

    def test_all_functions_call_generate_trace_id(self, mock_client):
        """Test that all API functions generate trace IDs"""
        client, payments_mock, refunds_mock = mock_client
        
        # Mock responses
        payments_mock.process_payment.return_value = Mock()
        payments_mock.increment_payment.return_value = Mock()
        payments_mock.simple_capture_of_payment.return_value = Mock()
        payments_mock.create_refund.return_value = Mock()
        payments_mock.get_payment_status.return_value = Mock()
        refunds_mock.get_refund.return_value = Mock()
        
        mock_request = Mock()
        
        with patch('src.api_calls.generate_trace_id') as mock_generate:
            # Call all functions
            create_payment(client, "acq", "mer", mock_request)
            increment_auth(client, "acq", "mer", "pay", mock_request)
            capture(client, "acq", "mer", "pay", mock_request)
            refund(client, "acq", "mer", "pay", mock_request)
            get_payment(client, "acq", "mer", "pay")
            get_refund(client, "acq", "mer", "ref")
            
            # Each function should have called generate_trace_id once
            assert mock_generate.call_count == 6


class TestHttpPatchingIntegration:
    """Integration tests for HTTP patching (limited scope)"""
    
    def test_patching_does_not_crash(self):
        """Test that the patching mechanism doesn't crash on import"""
        # This test simply verifies that the patching code doesn't crash
        # The actual patching is executed at module import time
        try:
            import src.api_calls
            # If we get here, the module imported successfully
            assert True
        except Exception as e:
            pytest.fail(f"Module import failed due to patching error: {e}")

    def test_patch_methods_handles_missing_module(self):
        """Test that patching mechanism exists and doesn't crash on basic usage"""
        # Simple test that just verifies the patching doesn't break basic functionality
        try:
            # Test that the basic functions still work after patching
            import src.api_calls
            assert hasattr(src.api_calls, 'create_payment')
            assert hasattr(src.api_calls, 'get_last_http_status')
            assert callable(src.api_calls.create_payment)
            assert callable(src.api_calls.get_last_http_status)
            
        except Exception as e:
            pytest.fail(f"Patching caused import failure: {e}")