"""Shared test fixtures and configuration"""

import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_environments_df():
    """Mock environments DataFrame"""
    return pd.DataFrame({
        'env': ['test', 'preprod'],
        'integrator': ['Test Integrator', 'Preprod Integrator'],
        'endpoint_host': ['api.test.com', 'api.preprod.com'],
        'authorization_type': ['OAuth2', 'OAuth2'],
        'oauth2_token_uri': ['https://auth.test.com', 'https://auth.preprod.com'],
        'connect_timeout': [5, 5],
        'socket_timeout': [300, 300],
        'max_connections': [10, 10],
        'client_id': ['test-client-id', 'preprod-client-id'],
        'client_secret': ['test-secret', 'preprod-secret']
    }).set_index('env')

@pytest.fixture
def mock_cards_df():
    """Mock cards DataFrame"""
    return pd.DataFrame({
        'card_id': ['card1', 'card2'],
        'card_brand': ['VISA', 'MASTERCARD'],
        'card_bin': ['411111', '522222'],
        'card_number': ['4111111111111111', '5222222222222222'],
        'expiry_date': ['122025', '122025'],
        'card_sequence_number': ['001', '002'],
        'card_security_code': ['123', '456'],
        'card_pin': ['1234', '5678'],
        'card_description': ['Test Visa', 'Test Mastercard']
    }).set_index('card_id')

@pytest.fixture
def mock_merchants_df():
    """Mock merchants DataFrame"""
    return pd.DataFrame({
        'merchant': ['merchant1', 'merchant2'],
        'env': ['test', 'test'],
        'acquirer_id': ['100812', '100812'],
        'merchant_id': ['520001857', '520001858'],
        'merchant_description': ['Test Merchant 1', 'Test Merchant 2']
    }).set_index(['env', 'merchant'])

@pytest.fixture
def mock_tests_df():
    """Mock tests DataFrame"""
    return pd.DataFrame({
        'chain_id': ['chain1', 'chain1', 'chain2'],
        'step_order': [1, 2, 1],
        'call_type': ['create_payment', 'increment_payment', 'create_payment'],
        'test_id': ['TEST001', 'TEST002', 'TEST003'],
        'card_id': ['card1', None, 'card2'],
        'merchant_id': ['merchant1', 'merchant1', 'merchant1'],
        'env': ['test', 'test', 'test'],
        'amount': [100, 50, 200],
        'currency': ['GBP', 'GBP', 'EUR'],
        'authorization_type': ['PRE_AUTHORIZATION', None, 'FINAL_AUTHORIZATION'],
        'allow_partial_approval': [None, None, 'TRUE'],
        'capture_immediately': ['FALSE', None, 'FALSE'],
        'card_entry_mode': ['ECOMMERCE', None, 'MAIL'],
        'cardholder_verification_method': ['CARD_SECURITY_CODE', None, 'NONE'],
        'dynamic_descriptor': [None, None, 'Test Merchant']
    })

@pytest.fixture
def mock_address_df():
    """Mock address DataFrame"""
    return pd.DataFrame({
        'address_id': ['AVS_FULL', 'AVS_PARTIAL_ADDRESS', 'AVS_PARTIAL_ZIP', 'AVS_MINIMAL'],
        'cardholder_postal_code': ['000008021', '000008021', '000008022', None],
        'cardholder_address': ['Hardturmstrasse 201', 'Hardturmstrasse 202', 'Hardturmstrasse 201', 'Minimal Street']
    }).set_index('address_id')

@pytest.fixture
def mock_networktokens_df():
    """Mock network tokens DataFrame"""
    return pd.DataFrame({
        'networktoken_id': ['APPLE_PAY_VISA', 'APPLE_PAY_MASTERCARD'],
        'wallet_id': ['103', '103'],
        'network_token_cryptogram': ['/wAAAAEACwuDlYgAAAAAgIRgE4A=', '/wAAAAEACwuDlYgAAAAAgIRgE4A='],
        'network_token_eci': ['05', '02']
    }).set_index('networktoken_id')

@pytest.fixture
def mock_api_payment_response():
    """Mock API payment response"""
    response = Mock()
    response.payment_id = 'pay:test:12345'
    response.status = 'AUTHORIZED'
    response.to_dictionary.return_value = {
        'paymentId': 'pay:test:12345',
        'status': 'AUTHORIZED',
        'operationId': 'TEST001-abc123',
        'responseCode': '0',
        'responseCodeCategory': 'APPROVED'
    }
    return response

@pytest.fixture
def mock_api_increment_response():
    """Mock API increment response"""
    response = Mock()
    response.payment = Mock()
    response.payment.payment_id = 'pay:test:12345'
    response.payment.status = 'AUTHORIZED'
    response.to_dictionary.return_value = {
        'operationId': 'TEST002-def456',
        'payment': {
            'paymentId': 'pay:test:12345',
            'status': 'AUTHORIZED'
        }
    }
    return response

@pytest.fixture
def mock_api_refund_response():
    """Mock API refund response"""
    response = Mock()
    response.refund = Mock()
    response.refund.refund_id = 'refund:test:67890'
    response.refund.status = 'REFUNDED'
    response.to_dictionary.return_value = {
        'operationId': 'TEST003-ghi789',
        'refund': {
            'refundId': 'refund:test:67890',
            'status': 'REFUNDED'
        }
    }
    return response

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    def _create_csv(data, columns):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(f.name, index=False)
            return f.name
    
    files_created = []
    
    def cleanup():
        for file_path in files_created:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    yield _create_csv
    cleanup()

@pytest.fixture
def mock_previous_outputs():
    """Mock previous outputs dictionary"""
    return {
        'payment_id': 'pay:test:12345',
        'refund_id': 'refund:test:67890'
    }