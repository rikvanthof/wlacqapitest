"""Unit tests for account verification request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.account_verification import build_account_verification_request

class TestBuildAccountVerificationRequest:
    """Test account verification request building"""

    @pytest.fixture
    def mock_cards_df(self):
        """Mock cards DataFrame with correct column names"""
        return pd.DataFrame({
            'card_number': ['4111111111111111'],
            'expiry_date': ['122025'],
            'card_security_code': ['123'],
            'card_brand': ['VISA'],
            'card_sequence_number': [None]
        }, index=['card1'])

    def test_build_basic_request(self, mock_cards_df):
        """Test building basic account verification request"""
        row = pd.Series({
            'test_id': 'ACCT_VER001',
            'currency': 'EUR',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.account_verification.generate_random_string', return_value='acctver123'):
            request = build_account_verification_request(row, mock_cards_df)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'ACCT_VER001:acctver123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'amount')
            assert hasattr(request, 'card_payment_data')
            assert hasattr(request, 'references')
            
            # Verify zero amount for verification
            assert request.amount.amount == 0
            assert request.amount.currency_code == 'EUR'
            assert request.amount.number_of_decimals == 2

    def test_build_with_dcc_context(self, mock_cards_df):
        """Test building request with DCC context"""
        row = pd.Series({
            'test_id': 'ACCT_VER002',
            'currency': 'GBP',
            'card_id': 'card1'
        })
        
        # Mock DCC context
        dcc_context = Mock()
        dcc_context.rate_reference_id = 'rate_ref_456'
        dcc_context.resulting_amount = {
            'amount': 0,  # Should be zero for verification
            'currency_code': 'EUR', 
            'number_of_decimals': 2
        }
        dcc_context.inverted_exchange_rate = 0.869
        
        with patch('src.request_builders.account_verification.generate_random_string', return_value='acctver456'):
            request = build_account_verification_request(row, mock_cards_df, dcc_context=dcc_context)
            
            # Verify main amount uses DCC resulting currency but zero amount
            assert request.amount.amount == 0  # Always zero for verification
            assert request.amount.currency_code == 'EUR'  # DCC resulting currency
            
            # Verify DCC fields
            assert hasattr(request, 'dynamic_currency_conversion')
            dcc_data = request.dynamic_currency_conversion
            assert dcc_data.amount == 0  # Zero amount in merchant currency
            assert dcc_data.currency_code == 'GBP'  # Original merchant currency
            assert dcc_data.conversion_rate == 0.869

    def test_card_payment_data_structure(self, mock_cards_df):
        """Test card payment data structure"""
        row = pd.Series({
            'test_id': 'ACCT_VER003',
            'currency': 'USD',
            'card_id': 'card1'
        })
        
        request = build_account_verification_request(row, mock_cards_df)
        
        # Verify card payment data
        card_data = request.card_payment_data
        assert card_data.brand == 'VISA'
        assert card_data.card_entry_mode == 'ECOMMERCE'  # Default
        assert card_data.cardholder_verification_method == 'CARD_SECURITY_CODE'  # Default
        
        # Verify card data
        plain_card_data = card_data.card_data
        assert plain_card_data.card_number == '4111111111111111'
        assert plain_card_data.expiry_date == '122025'
        assert plain_card_data.card_security_code == '123'

    def test_custom_card_options(self, mock_cards_df):
        """Test custom card entry mode and verification method"""
        row = pd.Series({
            'test_id': 'ACCT_VER004',
            'currency': 'EUR',
            'card_id': 'card1',
            'card_entry_mode': 'MANUAL',
            'cardholder_verification_method': 'PIN'
        })
        
        request = build_account_verification_request(row, mock_cards_df)
        
        # Verify custom options
        card_data = request.card_payment_data
        assert card_data.card_entry_mode == 'MANUAL'
        assert card_data.cardholder_verification_method == 'PIN'

    def test_merchant_reference_generation(self, mock_cards_df):
        """Test merchant reference generation"""
        row = pd.Series({
            'test_id': 'ACCT_VER005',
            'currency': 'GBP',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.account_verification.generate_random_string', return_value='acctver789'):
            request = build_account_verification_request(row, mock_cards_df)
            
            # Should have references with generated merchant_reference
            assert hasattr(request, 'references')
            assert request.references.merchant_reference == 'ACCT_VER005:acctver789'

    def test_dynamic_descriptor(self, mock_cards_df):
        """Test dynamic descriptor"""
        row = pd.Series({
            'test_id': 'ACCT_VER006',
            'currency': 'USD',
            'card_id': 'card1',
            'dynamic_descriptor': 'Account Check'
        })
        
        request = build_account_verification_request(row, mock_cards_df)
        
        # Should have dynamic descriptor
        assert request.references.dynamic_descriptor == 'Account Check'

    def test_request_cleaning_called(self, mock_cards_df):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'ACCT_VER007',
            'currency': 'EUR',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.account_verification.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_account_verification_request(row, mock_cards_df)
            mock_clean.assert_called_once()
    
    def test_build_with_brand_selector_merchant(self):
        """Test building request with merchant brand selector"""
        row = pd.Series({
            'test_id': 'ACC_BRAND_001',
            'card_id': 'card1',
            'brand_selector': 'MERCHANT',
            'currency': '',     # ✅ Add missing currency
            'amount': ''        # ✅ Add missing amount (empty for account verification)
        })
        
        cards_df = pd.DataFrame({
            'card_number': ['4111111111111111'],
            'expiry_date': ['1225'],
            'card_brand': ['VISA'],
            'card_security_code': ['123']
        }, index=['card1'])
        
        request = build_account_verification_request(row, cards_df)
        
        assert hasattr(request, 'card_payment_data')
        assert hasattr(request.card_payment_data, 'brand_selector')
        assert request.card_payment_data.brand_selector == 'MERCHANT'

    def test_build_with_brand_selector_cardholder(self):
        """Test building request with cardholder brand selector"""
        row = pd.Series({
            'test_id': 'ACC_BRAND_002',
            'card_id': 'card1',
            'brand_selector': 'CARDHOLDER',
            'currency': '',     # ✅ Add missing currency
            'amount': ''        # ✅ Add missing amount (empty for account verification)
        })
        
        cards_df = pd.DataFrame({
            'card_number': ['4111111111111111'],
            'expiry_date': ['1225'],
            'card_brand': ['VISA'],
            'card_security_code': ['123']
        }, index=['card1'])
        
        request = build_account_verification_request(row, cards_df)
        
        assert request.card_payment_data.brand_selector == 'CARDHOLDER'