"""Unit tests for balance inquiry request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.balance_inquiry import build_balance_inquiry_request

class TestBuildBalanceInquiryRequest:
    """Test balance inquiry request building"""

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
        """Test building basic balance inquiry request"""
        row = pd.Series({
            'test_id': 'BAL_INQ001',
            'currency': 'USD',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.balance_inquiry.generate_random_string', return_value='balinq123'):
            request = build_balance_inquiry_request(row, mock_cards_df)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'BAL_INQ001:balinq123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'amount')
            assert hasattr(request, 'card_payment_data')
            assert hasattr(request, 'references')
            
            # Verify zero amount for balance inquiry
            assert request.amount.amount == 0
            assert request.amount.currency_code == 'USD'
            assert request.amount.number_of_decimals == 2

    def test_build_with_dcc_context(self, mock_cards_df):
        """Test building request with DCC context"""
        row = pd.Series({
            'test_id': 'BAL_INQ002',
            'currency': 'GBP',
            'card_id': 'card1'
        })
        
        # Mock DCC context
        dcc_context = Mock()
        dcc_context.rate_reference_id = 'rate_ref_789'
        dcc_context.resulting_amount = {
            'amount': 0,  # Should be zero for balance inquiry
            'currency_code': 'USD', 
            'number_of_decimals': 2
        }
        dcc_context.inverted_exchange_rate = 1.25
        
        with patch('src.request_builders.balance_inquiry.generate_random_string', return_value='balinq456'):
            request = build_balance_inquiry_request(row, mock_cards_df, dcc_context=dcc_context)
            
            # Verify main amount uses DCC resulting currency but zero amount
            assert request.amount.amount == 0  # Always zero for balance inquiry
            assert request.amount.currency_code == 'USD'  # DCC resulting currency
            
            # Verify DCC fields
            assert hasattr(request, 'dynamic_currency_conversion')
            dcc_data = request.dynamic_currency_conversion
            assert dcc_data.amount == 0  # Zero amount in merchant currency
            assert dcc_data.currency_code == 'GBP'  # Original merchant currency
            assert dcc_data.conversion_rate == 1.25

    def test_card_payment_data_structure(self, mock_cards_df):
        """Test card payment data structure"""
        row = pd.Series({
            'test_id': 'BAL_INQ003',
            'currency': 'EUR',
            'card_id': 'card1'
        })
        
        request = build_balance_inquiry_request(row, mock_cards_df)
        
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
            'test_id': 'BAL_INQ004',
            'currency': 'USD',
            'card_id': 'card1',
            'card_entry_mode': 'CHIP',
            'cardholder_verification_method': 'PIN'
        })
        
        request = build_balance_inquiry_request(row, mock_cards_df)
        
        # Verify custom options
        card_data = request.card_payment_data
        assert card_data.card_entry_mode == 'CHIP'
        assert card_data.cardholder_verification_method == 'PIN'

    def test_merchant_reference_generation(self, mock_cards_df):
        """Test merchant reference generation"""
        row = pd.Series({
            'test_id': 'BAL_INQ005',
            'currency': 'EUR',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.balance_inquiry.generate_random_string', return_value='balinq789'):
            request = build_balance_inquiry_request(row, mock_cards_df)
            
            # Should have references with generated merchant_reference
            assert hasattr(request, 'references')
            assert request.references.merchant_reference == 'BAL_INQ005:balinq789'

    def test_dynamic_descriptor(self, mock_cards_df):
        """Test dynamic descriptor"""
        row = pd.Series({
            'test_id': 'BAL_INQ006',
            'currency': 'USD',
            'card_id': 'card1',
            'dynamic_descriptor': 'Balance Check'
        })
        
        request = build_balance_inquiry_request(row, mock_cards_df)
        
        # Should have dynamic descriptor
        assert request.references.dynamic_descriptor == 'Balance Check'

    def test_request_cleaning_called(self, mock_cards_df):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'BAL_INQ007',
            'currency': 'USD',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.balance_inquiry.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_balance_inquiry_request(row, mock_cards_df)
            mock_clean.assert_called_once()