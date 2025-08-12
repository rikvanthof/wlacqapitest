"""Test data loading functions"""

import pytest
import pandas as pd
import tempfile
import os
from src.data_loader import load_data

class TestLoadData:
    """Test data loading function"""
    
    def test_load_data_success(self, temp_csv_file):
        """Test successful data loading including address data"""
        # Create temporary CSV files
        envs_data = [
            ['dev', 'Test Integrator', 'api.dev.com', 'OAuth2', 'https://auth.dev.com', 5, 300, 10, 'dev-client', 'dev-secret'],
            ['prod', 'Prod Integrator', 'api.prod.com', 'OAuth2', 'https://auth.prod.com', 5, 300, 10, 'prod-client', 'prod-secret']
        ]
        envs_columns = ['env', 'integrator', 'endpoint_host', 'authorization_type', 'oauth2_token_uri', 
                       'connect_timeout', 'socket_timeout', 'max_connections', 'client_id', 'client_secret']
        envs_file = temp_csv_file(envs_data, envs_columns)
        
        cards_data = [
            ['card1', 'VISA', '411111', '4111111111111111', '122025', '001', '123', '1234', 'Test Visa'],
            ['card2', 'MASTERCARD', '522222', '5222222222222222', '122025', '002', '456', '5678', 'Test MC']
        ]
        cards_columns = ['card_id', 'card_brand', 'card_bin', 'card_number', 'expiry_date', 
                        'card_sequence_number', 'card_security_code', 'card_pin', 'card_description']
        cards_file = temp_csv_file(cards_data, cards_columns)
        
        merchants_data = [
            ['merchant1', 'dev', '100812', '520001857', 'Test Merchant 1'],
            ['merchant2', 'prod', '100812', '520001858', 'Test Merchant 2']
        ]
        merchants_columns = ['merchant', 'env', 'acquirer_id', 'merchant_id', 'merchant_description']
        merchants_file = temp_csv_file(merchants_data, merchants_columns)
        
        # Add address data
        address_data = [
            ['AVS_FULL', '000008021', 'Hardturmstrasse 201'],
            ['AVS_PARTIAL', '000008022', 'Hardturmstrasse 202']
        ]
        address_columns = ['address_id', 'cardholder_postal_code', 'cardholder_address']
        address_file = temp_csv_file(address_data, address_columns)
        
        tests_data = [
            ['chain1', 1, 'create_payment', 'TEST001', 'card1', 'merchant1', 'dev', 100, 'GBP', 'PRE_AUTHORIZATION', None, 'FALSE', 'ECOMMERCE', 'CARD_SECURITY_CODE', None],
            ['chain1', 2, 'increment_payment', 'TEST002', None, 'merchant1', 'dev', 50, 'GBP', None, None, None, None, None, None]
        ]
        tests_columns = ['chain_id', 'step_order', 'call_type', 'test_id', 'card_id', 'merchant_id', 'env', 'amount', 'currency',
                        'authorization_type', 'allow_partial_approval', 'capture_immediately', 'card_entry_mode', 
                        'cardholder_verification_method', 'dynamic_descriptor']
        tests_file = temp_csv_file(tests_data, tests_columns)
        
        # Mock the file paths
        with pytest.MonkeyPatch().context() as m:
            m.setattr('pandas.read_csv', lambda path, **kwargs: {
                'config/environments.csv': pd.DataFrame(envs_data, columns=envs_columns),
                'config/cards.csv': pd.DataFrame(cards_data, columns=cards_columns),
                'config/merchants.csv': pd.DataFrame(merchants_data, columns=merchants_columns),
                'config/address.csv': pd.DataFrame(address_data, columns=address_columns),
                tests_file: pd.DataFrame(tests_data, columns=tests_columns)
            }[path])
            
            environments, cards, merchants, address, tests = load_data(tests_file)
            
            # Verify data was loaded correctly
            assert len(environments) == 2
            assert len(cards) == 2
            assert len(merchants) == 2
            assert len(address) == 2
            assert len(tests) == 2
            
            # Verify indexing
            assert 'dev' in environments.index
            assert 'card1' in cards.index
            assert ('dev', 'merchant1') in merchants.index
            assert 'AVS_FULL' in address.index
            
            # Verify address data types
            assert address.loc['AVS_FULL', 'cardholder_postal_code'] == '000008021'
            assert address.loc['AVS_FULL', 'cardholder_address'] == 'Hardturmstrasse 201'

    def test_load_data_address_data_types(self, temp_csv_file):
        """Test that address data is loaded with correct string types"""
        # Create minimal data for other files
        minimal_env_data = [['dev', 'Test', 'api.dev.com', 'OAuth2', 'https://auth.dev.com', 5, 300, 10, 'dev-client', 'dev-secret']]
        minimal_cards_data = [['card1', 'VISA', '411111', '4111111111111111', '122025', '001', '123', '1234', 'Test Visa']]
        minimal_merchants_data = [['merchant1', 'dev', '100812', '520001857', 'Test Merchant 1']]
        
        # Test address data with different scenarios
        address_data = [
            ['AVS_FULL', '000008021', 'Hardturmstrasse 201'],
            ['AVS_NUMERIC_ZIP', '12345', 'Main Street 123'],
            ['AVS_EMPTY_FIELDS', '', '']
        ]
        address_columns = ['address_id', 'cardholder_postal_code', 'cardholder_address']
        
        tests_data = [['chain1', 1, 'create_payment', 'TEST001', 'card1', 'merchant1', 'dev', 100, 'GBP', 'PRE_AUTHORIZATION', None, 'FALSE', 'ECOMMERCE', 'CARD_SECURITY_CODE', None]]
        tests_columns = ['chain_id', 'step_order', 'call_type', 'test_id', 'card_id', 'merchant_id', 'env', 'amount', 'currency',
                        'authorization_type', 'allow_partial_approval', 'capture_immediately', 'card_entry_mode', 
                        'cardholder_verification_method', 'dynamic_descriptor']
        tests_file = temp_csv_file(tests_data, tests_columns)
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('pandas.read_csv', lambda path, **kwargs: {
                'config/environments.csv': pd.DataFrame(minimal_env_data, columns=['env', 'integrator', 'endpoint_host', 'authorization_type', 'oauth2_token_uri', 'connect_timeout', 'socket_timeout', 'max_connections', 'client_id', 'client_secret']),
                'config/cards.csv': pd.DataFrame(minimal_cards_data, columns=['card_id', 'card_brand', 'card_bin', 'card_number', 'expiry_date', 'card_sequence_number', 'card_security_code', 'card_pin', 'card_description']),
                'config/merchants.csv': pd.DataFrame(minimal_merchants_data, columns=['merchant', 'env', 'acquirer_id', 'merchant_id', 'merchant_description']),
                'config/address.csv': pd.DataFrame(address_data, columns=address_columns),
                tests_file: pd.DataFrame(tests_data, columns=tests_columns)
            }[path])
            
            _, _, _, address, _ = load_data(tests_file)
            
            # Verify address data types are strings
            assert isinstance(address.loc['AVS_FULL', 'cardholder_postal_code'], str)
            assert isinstance(address.loc['AVS_FULL', 'cardholder_address'], str)
            assert isinstance(address.loc['AVS_NUMERIC_ZIP', 'cardholder_postal_code'], str)
            
            # Verify content
            assert address.loc['AVS_NUMERIC_ZIP', 'cardholder_postal_code'] == '12345'
            assert address.loc['AVS_NUMERIC_ZIP', 'cardholder_address'] == 'Main Street 123'

    def test_load_data_with_networktokens(self, temp_csv_file):
        """Test that network tokens are loaded correctly"""
        # Create test data files (reusing existing pattern)
        envs_data = [['dev', 'Test', 'api.dev.com', 'OAuth2', 'https://auth.dev.com', 5, 300, 10, 'dev-client', 'dev-secret']]
        envs_columns = ['env', 'integrator', 'endpoint_host', 'authorization_type', 'oauth2_token_uri', 'connect_timeout', 'socket_timeout', 'max_connections', 'client_id', 'client_secret']
        
        cards_data = [['card1', 'VISA', '411111', '4111111111111111', '122025', '001', '123', '1234', 'Test Visa']]
        cards_columns = ['card_id', 'card_brand', 'card_bin', 'card_number', 'expiry_date', 'card_sequence_number', 'card_security_code', 'card_pin', 'card_description']
        
        merchants_data = [['merchant1', 'dev', '100812', '520001857', 'Test Merchant']]
        merchants_columns = ['merchant', 'env', 'acquirer_id', 'merchant_id', 'merchant_description']
        
        address_data = [['addr1', '123 Test St', '12345']]
        address_columns = ['address_id', 'cardholder_address', 'cardholder_postal_code']
        
        networktokens_data = [['APPLE_PAY_VISA', '103', '/wAAAAEACwuDlYgAAAAAgIRgE4A=', '05']]
        networktokens_columns = ['networktoken_id', 'wallet_id', 'network_token_cryptogram', 'network_token_eci']
        
        tests_data = [['chain1', 1, 'create_payment', 'TEST001', 'card1', 'merchant1', 'dev', 100, 'GBP', None, None, None, None, None, None]]
        tests_columns = ['chain_id', 'step_order', 'call_type', 'test_id', 'card_id', 'merchant_id', 'env', 'amount', 'currency', 'authorization_type', 'allow_partial_approval', 'capture_immediately', 'card_entry_mode', 'cardholder_verification_method', 'dynamic_descriptor']
        
        tests_file = temp_csv_file(tests_data, tests_columns)
        
        # Mock all file reads
        with pytest.MonkeyPatch().context() as m:
            m.setattr('pandas.read_csv', lambda path, **kwargs: {
                'config/environments.csv': pd.DataFrame(envs_data, columns=envs_columns),
                'config/cards.csv': pd.DataFrame(cards_data, columns=cards_columns),
                'config/merchants.csv': pd.DataFrame(merchants_data, columns=merchants_columns),
                'config/address.csv': pd.DataFrame(address_data, columns=address_columns),
                'config/networktoken.csv': pd.DataFrame(networktokens_data, columns=networktokens_columns),
                tests_file: pd.DataFrame(tests_data, columns=tests_columns)
            }[path])
            
            environments, cards, merchants, address, networktokens, tests = load_data(tests_file)
            
            # Verify network tokens were loaded correctly
            assert len(networktokens) == 1
            assert 'APPLE_PAY_VISA' in networktokens.index
            assert networktokens.loc['APPLE_PAY_VISA']['wallet_id'] == '103'
            assert networktokens.loc['APPLE_PAY_VISA']['network_token_cryptogram'] == '/wAAAAEACwuDlYgAAAAAgIRgE4A='
            assert networktokens.loc['APPLE_PAY_VISA']['network_token_eci'] == '05'

    def test_load_data_file_not_found(self):
        """Test data loading with non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_data('non_existent_file.csv')

    def test_load_data_sorting(self, temp_csv_file):
        """Test that tests are sorted by chain_id and step_order"""
        tests_data = [
            ['chain2', 2, 'increment_payment', 'TEST004', None, 'merchant1', 'dev', 50, 'GBP', None, None, None, None, None, None],
            ['chain1', 2, 'increment_payment', 'TEST002', None, 'merchant1', 'dev', 50, 'GBP', None, None, None, None, None, None],
            ['chain2', 1, 'create_payment', 'TEST003', 'card1', 'merchant1', 'dev', 100, 'GBP', 'PRE_AUTHORIZATION', None, 'FALSE', 'ECOMMERCE', 'CARD_SECURITY_CODE', None],
            ['chain1', 1, 'create_payment', 'TEST001', 'card1', 'merchant1', 'dev', 100, 'GBP', 'PRE_AUTHORIZATION', None, 'FALSE', 'ECOMMERCE', 'CARD_SECURITY_CODE', None]
        ]
        tests_columns = ['chain_id', 'step_order', 'call_type', 'test_id', 'card_id', 'merchant_id', 'env', 'amount', 'currency',
                        'authorization_type', 'allow_partial_approval', 'capture_immediately', 'card_entry_mode', 
                        'cardholder_verification_method', 'dynamic_descriptor']
        tests_file = temp_csv_file(tests_data, tests_columns)
        
        # Mock other files to avoid FileNotFoundError
        with pytest.MonkeyPatch().context() as m:
            m.setattr('pandas.read_csv', lambda path, **kwargs: {
                'config/environments.csv': pd.DataFrame([['dev', 'Test', 'api.dev.com', 'OAuth2', 'https://auth.dev.com', 5, 300, 10, 'dev-client', 'dev-secret']], 
                                                       columns=['env', 'integrator', 'endpoint_host', 'authorization_type', 'oauth2_token_uri', 'connect_timeout', 'socket_timeout', 'max_connections', 'client_id', 'client_secret']),
                'config/cards.csv': pd.DataFrame([['card1', 'VISA', '411111', '4111111111111111', '122025', '001', '123', '1234', 'Test Visa']], 
                                                columns=['card_id', 'card_brand', 'card_bin', 'card_number', 'expiry_date', 'card_sequence_number', 'card_security_code', 'card_pin', 'card_description']),
                'config/merchants.csv': pd.DataFrame([['merchant1', 'dev', '100812', '520001857', 'Test Merchant 1']], 
                                                   columns=['merchant', 'env', 'acquirer_id', 'merchant_id', 'merchant_description']),
                'config/address.csv': pd.DataFrame([['AVS_TEST', '12345', 'Test Street']], 
                                                 columns=['address_id', 'cardholder_postal_code', 'cardholder_address']),
                tests_file: pd.DataFrame(tests_data, columns=tests_columns)
            }[path])
            
            _, _, _, _, tests = load_data(tests_file)
            
            # Verify sorting
            expected_order = ['TEST001', 'TEST002', 'TEST003', 'TEST004']
            actual_order = tests['test_id'].tolist()
            assert actual_order == expected_order