"""Test create payment request builder"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.request_builders.create_payment import build_create_payment_request

class TestBuildCreatePaymentRequest:
    """Test create payment request building"""
    
    def test_build_complete_request(self, mock_cards_df):
        """Test building complete create payment request"""
        row = {
            'test_id': 'TEST001',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'authorization_type': 'PRE_AUTHORIZATION',
            'allow_partial_approval': 'TRUE',
            'capture_immediately': 'FALSE',
            'card_entry_mode': 'ECOMMERCE',
            'cardholder_verification_method': 'CARD_SECURITY_CODE',
            'dynamic_descriptor': 'Test Merchant'
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='abc123'):
            with patch('pandas.Timestamp.now') as mock_now:
                mock_timestamp = Mock()
                mock_now.return_value.tz_localize.return_value.replace.return_value.to_pydatetime.return_value = mock_timestamp
                
                request = build_create_payment_request(row, mock_cards_df, None, None)
                
                # Verify request structure
                assert hasattr(request, 'operation_id')
                assert request.operation_id == 'TEST001-abc123'
                assert hasattr(request, 'transaction_timestamp')
                assert hasattr(request, 'card_payment_data')
                assert hasattr(request, 'amount')
                assert hasattr(request, 'authorization_type')
                assert hasattr(request, 'dynamic_descriptor')
                
                # Verify card data
                card_data = request.card_payment_data.card_data
                assert card_data.card_number == '4111111111111111'
                assert card_data.expiry_date == '122025'
                assert card_data.cvv == '123'
                
                # Verify payment data
                assert request.card_payment_data.brand == 'VISA'
                assert request.card_payment_data.allow_partial_approval is True
                assert request.card_payment_data.capture_immediately is False
                assert request.card_payment_data.card_entry_mode == 'ECOMMERCE'
                assert request.card_payment_data.cardholder_verification_method == 'CARD_SECURITY_CODE'
                
                # Verify amount
                assert request.amount.amount == 100
                assert request.amount.currency_code == 'GBP'
                assert request.amount.number_of_decimals == 2
                
                # Verify other fields
                assert request.authorization_type == 'PRE_AUTHORIZATION'
                assert request.dynamic_descriptor == 'Test Merchant'

    def test_build_minimal_request(self, mock_cards_df):
        """Test building minimal create payment request"""
        row = {
            'test_id': 'TEST002',
            'card_id': 'card2',
            'amount': 200,
            'currency': 'EUR',
            'authorization_type': None,  # Should be skipped
            'allow_partial_approval': None,
            'capture_immediately': None,
            'card_entry_mode': None,
            'cardholder_verification_method': None,
            'dynamic_descriptor': None
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='def456'):
            request = build_create_payment_request(row, mock_cards_df, None, None)
            
            # Verify required fields are set
            assert hasattr(request, 'operation_id')
            assert hasattr(request, 'card_payment_data')
            assert hasattr(request, 'amount')
            
        # Verify optional fields have no meaningful values
        assert getattr(request.card_payment_data, 'allow_partial_approval', None) is None
        assert getattr(request.card_payment_data, 'capture_immediately', None) is None

    def test_build_with_missing_card_fields(self):
        """Test building request with missing optional card fields"""
        cards_df = pd.DataFrame({
            'card_id': ['card_minimal'],
            'card_brand': ['VISA'],
            'card_bin': [None],
            'card_number': ['4111111111111111'],
            'expiry_date': ['122025'],
            'card_sequence_number': [None],
            'card_security_code': [None],
            'card_pin': [None],
            'card_description': ['Minimal Card']
        }).set_index('card_id')
        
        row = {
            'test_id': 'TEST003',
            'card_id': 'card_minimal',
            'amount': 50,
            'currency': 'USD',
            'allow_partial_approval': None,
            'capture_immediately': None,
            'card_entry_mode': None,
            'cardholder_verification_method': None,
            'dynamic_descriptor': None,
            'authorization_type': None
        }
        
        request = build_create_payment_request(row, cards_df, None, None)
        
        # Should have card number and expiry date
        card_data = request.card_payment_data.card_data
        assert card_data.card_number == '4111111111111111'
        assert card_data.expiry_date == '122025'
        
        # Should not have optional fields set to meaningful values
        assert getattr(card_data, 'cvv', None) is None
        assert getattr(card_data, 'card_sequence_number', None) is None

    def test_build_with_invalid_card_id(self, mock_cards_df):
        """Test building request with invalid card ID"""
        row = {
            'test_id': 'TEST004',
            'card_id': 'invalid_card',
            'amount': 100,
            'currency': 'GBP'
        }
        
        with pytest.raises(KeyError):
            build_create_payment_request(row, mock_cards_df, None, None)

    @patch('src.request_builders.create_payment.clean_request')
    def test_request_cleaning_called(self, mock_clean_request, mock_cards_df):
        """Test that request cleaning is called"""
        row = {
            'test_id': 'TEST005',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'allow_partial_approval': None,
            'capture_immediately': None,
            'card_entry_mode': None,
            'cardholder_verification_method': None,
            'dynamic_descriptor': None,
            'authorization_type': None
        }
        
        mock_clean_request.return_value = Mock()
        
        build_create_payment_request(row, mock_cards_df, None, None)
        
        mock_clean_request.assert_called_once()

    def test_build_request_with_avs_data(self, mock_cards_df, mock_address_df):
        """Test building request with AVS data"""
        row = {
            'test_id': 'TEST_AVS001',
            'card_id': 'card1',
            'amount': 123,
            'currency': 'GBP',
            'authorization_type': 'PRE_AUTHORIZATION',
            'address_data': 'AVS_FULL'
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='avs123'):
            request = build_create_payment_request(row, mock_cards_df, mock_address_df, None)
            
            # Verify basic request structure
            assert hasattr(request, 'card_payment_data')
            assert hasattr(request.card_payment_data, 'ecommerce_data')
            
            # Verify AVS data structure
            ecommerce_data = request.card_payment_data.ecommerce_data
            assert hasattr(ecommerce_data, 'address_verification_data')
            
            avs_data = ecommerce_data.address_verification_data
            assert avs_data.cardholder_address == 'Hardturmstrasse 201'
            assert avs_data.cardholder_postal_code == '000008021'

    def test_build_request_with_partial_avs_data(self, mock_cards_df, mock_address_df):
        """Test building request with partial AVS data (missing postal code)"""
        row = {
            'test_id': 'TEST_AVS002',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'EUR',
            'address_data': 'AVS_MINIMAL'  # Has address but no postal code
        }
        
        request = build_create_payment_request(row, mock_cards_df, mock_address_df, None)
        
        # Verify AVS data structure exists
        assert hasattr(request.card_payment_data, 'ecommerce_data')
        avs_data = request.card_payment_data.ecommerce_data.address_verification_data
        
        # Should have address but not postal code
        assert avs_data.cardholder_address == 'Minimal Street'
        assert not hasattr(avs_data, 'cardholder_postal_code') or avs_data.cardholder_postal_code is None

    def test_build_request_without_avs_data(self, mock_cards_df):
        """Test building request without AVS data"""
        row = {
            'test_id': 'TEST_NO_AVS',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP'
        }
        
        request = build_create_payment_request(row, mock_cards_df, None, None)
        
        # Should not have ecommerce_data when no AVS data is provided
        assert not hasattr(request.card_payment_data, 'ecommerce_data') or \
               request.card_payment_data.ecommerce_data is None

    def test_build_request_with_none_address_data(self, mock_cards_df, mock_address_df):
        """Test building request with None address_data"""
        row = {
            'test_id': 'TEST_NONE_AVS',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'address_data': None
        }
        
        request = build_create_payment_request(row, mock_cards_df, mock_address_df, None)
        
        # Should not have ecommerce_data when address_data is None
        assert not hasattr(request.card_payment_data, 'ecommerce_data') or \
               request.card_payment_data.ecommerce_data is None

    def test_build_request_with_invalid_address_id(self, mock_cards_df, mock_address_df):
        """Test building request with invalid address ID"""
        row = {
            'test_id': 'TEST_INVALID_AVS',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'address_data': 'INVALID_ADDRESS_ID'
        }
        
        request = build_create_payment_request(row, mock_cards_df, mock_address_df, None)
        
        # Should not have ecommerce_data when address_id is invalid
        assert not hasattr(request.card_payment_data, 'ecommerce_data') or \
               request.card_payment_data.ecommerce_data is None

    def test_build_request_with_empty_address_dataframe(self, mock_cards_df):
        """Test building request when address dataframe is None"""
        row = {
            'test_id': 'TEST_NO_ADDRESS_DF',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'address_data': 'AVS_FULL'
        }
        
        request = build_create_payment_request(row, mock_cards_df, address=None, networktokens=None)
        
        # Should not have ecommerce_data when address dataframe is None
        assert not hasattr(request.card_payment_data, 'ecommerce_data') or \
               request.card_payment_data.ecommerce_data is None

    def test_build_request_avs_with_other_fields(self, mock_cards_df, mock_address_df):
        """Test building request with AVS data combined with other optional fields"""
        row = {
            'test_id': 'TEST_AVS_COMBO',
            'card_id': 'card1',
            'amount': 150,
            'currency': 'USD',
            'authorization_type': 'FINAL_AUTHORIZATION',
            'allow_partial_approval': 'TRUE',
            'capture_immediately': 'TRUE',
            'card_entry_mode': 'ECOMMERCE',
            'cardholder_verification_method': 'CARD_SECURITY_CODE',
            'dynamic_descriptor': 'AVS Test Merchant',
            'address_data': 'AVS_PARTIAL_ADDRESS'
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='combo123'):
            request = build_create_payment_request(row, mock_cards_df, mock_address_df, None)
            
            # Verify all non-AVS fields are set correctly
            assert request.authorization_type == 'FINAL_AUTHORIZATION'
            assert request.dynamic_descriptor == 'AVS Test Merchant'
            assert request.card_payment_data.allow_partial_approval is True
            assert request.card_payment_data.capture_immediately is True
            assert request.card_payment_data.card_entry_mode == 'ECOMMERCE'
            assert request.card_payment_data.cardholder_verification_method == 'CARD_SECURITY_CODE'
            
            # Verify AVS data is also set correctly
            assert hasattr(request.card_payment_data, 'ecommerce_data')
            avs_data = request.card_payment_data.ecommerce_data.address_verification_data
            assert avs_data.cardholder_address == 'Hardturmstrasse 202'
            assert avs_data.cardholder_postal_code == '000008021'

    @patch('src.request_builders.create_payment.clean_request')
    def test_avs_request_cleaning_called(self, mock_clean_request, mock_cards_df, mock_address_df):
        """Test that request cleaning is called even with AVS data"""
        row = {
            'test_id': 'TEST_AVS_CLEAN',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'address_data': 'AVS_FULL'
        }
        
        mock_clean_request.return_value = Mock()
        
        build_create_payment_request(row, mock_cards_df, mock_address_df, None)
        
        mock_clean_request.assert_called_once()

    # NEW NETWORK TOKEN TESTS
    def test_build_with_network_token_data(self, mock_cards_df, mock_networktokens_df):
        """Test building request with network token data"""
        row = {
            'test_id': 'TEST_NETWORK_TOKEN',
            'card_id': 'card1',
            'amount': 150,
            'currency': 'GBP',
            'network_token_data': 'APPLE_PAY_VISA',
            'allow_partial_approval': None,
            'capture_immediately': None,
            'card_entry_mode': None,
            'cardholder_verification_method': None,
            'dynamic_descriptor': None,
            'authorization_type': None
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='token123'):
            request = build_create_payment_request(row, mock_cards_df, None, mock_networktokens_df)
            
            # Verify request has network token data
            assert hasattr(request.card_payment_data, 'ecommerce_data')
            assert request.card_payment_data.ecommerce_data is not None
            assert hasattr(request.card_payment_data.ecommerce_data, 'network_token_data')
            
            network_token_data = request.card_payment_data.ecommerce_data.network_token_data
            assert network_token_data.cryptogram == '/wAAAAEACwuDlYgAAAAAgIRgE4A='
            assert network_token_data.eci == '05'

    def test_build_with_both_avs_and_network_token(self, mock_cards_df, mock_address_df, mock_networktokens_df):
        """Test building request with both AVS and network token data"""
        row = {
            'test_id': 'TEST_COMBINED',
            'card_id': 'card1',
            'amount': 200,
            'currency': 'EUR',
            'address_data': 'AVS_FULL',
            'network_token_data': 'APPLE_PAY_MASTERCARD',
            'allow_partial_approval': None,
            'capture_immediately': None,
            'card_entry_mode': None,
            'cardholder_verification_method': None,
            'dynamic_descriptor': None,
            'authorization_type': None
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='combo123'):
            request = build_create_payment_request(row, mock_cards_df, mock_address_df, mock_networktokens_df)
            
            # Verify both AVS and network token data are present
            ecommerce_data = request.card_payment_data.ecommerce_data
            assert ecommerce_data is not None
            
            # Check AVS data
            assert hasattr(ecommerce_data, 'address_verification_data')
            avs_data = ecommerce_data.address_verification_data
            assert avs_data.cardholder_address == 'Hardturmstrasse 201'
            assert avs_data.cardholder_postal_code == '000008021'
            
            # Check network token data
            assert hasattr(ecommerce_data, 'network_token_data')
            network_token_data = ecommerce_data.network_token_data
            assert network_token_data.cryptogram == '/wAAAAEACwuDlYgAAAAAgIRgE4A='
            assert network_token_data.eci == '02'  # MASTERCARD has eci '02'

    def test_build_with_invalid_network_token_id(self, mock_cards_df, mock_networktokens_df):
        """Test building request with invalid network token ID"""
        row = {
            'test_id': 'TEST_INVALID_TOKEN',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'network_token_data': 'INVALID_TOKEN_ID',
            'allow_partial_approval': None,
            'capture_immediately': None,
            'card_entry_mode': None,
            'cardholder_verification_method': None,
            'dynamic_descriptor': None,
            'authorization_type': None
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='invalid123'):
            request = build_create_payment_request(row, mock_cards_df, None, mock_networktokens_df)
            
            # Should not have ecommerce_data since invalid token ID
            ecommerce_data = getattr(request.card_payment_data, 'ecommerce_data', None)
            assert ecommerce_data is None

    def test_build_with_missing_network_token_fields(self, mock_cards_df):
        """Test building request with missing optional network token fields"""
        networktokens_df = pd.DataFrame({
            'networktoken_id': ['INCOMPLETE_TOKEN'],
            'wallet_id': ['103'],
            'network_token_cryptogram': [None],  # Missing cryptogram
            'network_token_eci': ['05']
        }).set_index('networktoken_id')
        
        row = {
            'test_id': 'TEST_INCOMPLETE',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'network_token_data': 'INCOMPLETE_TOKEN',
            'allow_partial_approval': None,
            'capture_immediately': None,
            'card_entry_mode': None,
            'cardholder_verification_method': None,
            'dynamic_descriptor': None,
            'authorization_type': None
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='incomplete123'):
            request = build_create_payment_request(row, mock_cards_df, None, networktokens_df)
            
            # Should have network token data but with only available fields
            ecommerce_data = request.card_payment_data.ecommerce_data
            assert ecommerce_data is not None
            
            network_token_data = ecommerce_data.network_token_data
            assert network_token_data.eci == '05'
            # Cryptogram should not be set since it was None/NaN
            assert not hasattr(network_token_data, 'cryptogram') or network_token_data.cryptogram is None

    def test_build_without_network_tokens_dataframe(self, mock_cards_df):
        """Test building request when networktokens DataFrame is None"""
        row = {
            'test_id': 'TEST_NO_TOKENS_DF',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'network_token_data': 'APPLE_PAY_VISA',  # Token specified but no DataFrame
            'allow_partial_approval': None,
            'capture_immediately': None,
            'card_entry_mode': None,
            'cardholder_verification_method': None,
            'dynamic_descriptor': None,
            'authorization_type': None
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='nodf123'):
            request = build_create_payment_request(row, mock_cards_df, None, None)  # networktokens=None
            
            # Should not have ecommerce_data since networktokens DataFrame is None
            ecommerce_data = getattr(request.card_payment_data, 'ecommerce_data', None)
            assert ecommerce_data is None

    def test_build_network_token_with_other_fields(self, mock_cards_df, mock_networktokens_df):
        """Test building request with network token data combined with other optional fields"""
        row = {
            'test_id': 'TEST_TOKEN_COMBO',
            'card_id': 'card1',
            'amount': 175,
            'currency': 'USD',
            'authorization_type': 'FINAL_AUTHORIZATION',
            'allow_partial_approval': 'TRUE',
            'capture_immediately': 'FALSE',
            'card_entry_mode': 'ECOMMERCE',
            'cardholder_verification_method': 'CARD_SECURITY_CODE',
            'dynamic_descriptor': 'Token Test Merchant',
            'network_token_data': 'APPLE_PAY_VISA'
        }
        
        with patch('src.request_builders.create_payment.generate_random_string', return_value='tokencombo123'):
            request = build_create_payment_request(row, mock_cards_df, None, mock_networktokens_df)
            
            # Verify all non-token fields are set correctly
            assert request.authorization_type == 'FINAL_AUTHORIZATION'
            assert request.dynamic_descriptor == 'Token Test Merchant'
            assert request.card_payment_data.allow_partial_approval is True
            assert request.card_payment_data.capture_immediately is False
            assert request.card_payment_data.card_entry_mode == 'ECOMMERCE'
            assert request.card_payment_data.cardholder_verification_method == 'CARD_SECURITY_CODE'
            
            # Verify network token data is also set correctly
            assert hasattr(request.card_payment_data, 'ecommerce_data')
            network_token_data = request.card_payment_data.ecommerce_data.network_token_data
            assert network_token_data.cryptogram == '/wAAAAEACwuDlYgAAAAAgIRgE4A='
            assert network_token_data.eci == '05'

    @patch('src.request_builders.create_payment.clean_request')
    def test_network_token_request_cleaning_called(self, mock_clean_request, mock_cards_df, mock_networktokens_df):
        """Test that request cleaning is called even with network token data"""
        row = {
            'test_id': 'TEST_TOKEN_CLEAN',
            'card_id': 'card1',
            'amount': 100,
            'currency': 'GBP',
            'network_token_data': 'APPLE_PAY_VISA'
        }
        
        mock_clean_request.return_value = Mock()
        
        build_create_payment_request(row, mock_cards_df, None, mock_networktokens_df)
        
        mock_clean_request.assert_called_once()