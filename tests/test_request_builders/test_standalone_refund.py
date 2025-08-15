"""Unit tests for standalone refund request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.standalone_refund import build_standalone_refund_request

class TestBuildStandaloneRefundRequest:
    """Test standalone refund request building"""

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

    def test_build_complete_request(self, mock_cards_df):
        """Test building complete standalone refund request"""
        row = pd.Series({
            'test_id': 'REF001',
            'amount': 750,
            'currency': 'EUR',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.standalone_refund.generate_random_string', return_value='ref123'):
            request = build_standalone_refund_request(row, mock_cards_df)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'REF001:ref123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'amount')
            assert hasattr(request, 'card_payment_data')
            assert hasattr(request, 'references')
            
            # Verify amount
            assert request.amount.amount == 750
            assert request.amount.currency_code == 'EUR'
            assert request.amount.number_of_decimals == 2

    def test_build_with_dcc_context(self, mock_cards_df):
        """Test building request with DCC context"""
        row = pd.Series({
            'test_id': 'REF002',
            'amount': 1000,
            'currency': 'GBP',
            'card_id': 'card1'
        })

        # Mock DCC context
        dcc_context = Mock()
        dcc_context.rate_reference_id = 'rate_ref_456'
        dcc_context.resulting_amount = {
            'amount': 1150,
            'currency_code': 'EUR',
            'number_of_decimals': 2
        }
        dcc_context.inverted_exchange_rate = 0.869

        with patch('src.request_builders.standalone_refund.generate_random_string', return_value='ref456'):
            # ✅ FIX: Use correct parameter name for new signature
            request = build_standalone_refund_request(row, mock_cards_df, merchantdata=None, dcc_context=dcc_context)

            # Verify main amount uses DCC resulting amount
            assert request.amount.amount == 1150
            assert request.amount.currency_code == 'EUR'
            
            # Verify DCC fields
            assert hasattr(request, 'dynamic_currency_conversion')
            dcc_data = request.dynamic_currency_conversion
            assert dcc_data.amount == 1000  # Original merchant amount
            assert dcc_data.currency_code == 'GBP'  # Original merchant currency
            assert dcc_data.conversion_rate == 0.869

    def test_merchant_reference_generation(self, mock_cards_df):
        """Test merchant reference generation"""
        row = pd.Series({
            'test_id': 'REF003',
            'amount': 500,
            'currency': 'USD',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.standalone_refund.generate_random_string', return_value='ref789'):
            request = build_standalone_refund_request(row, mock_cards_df)
            
            # Should have references with generated merchant_reference
            assert hasattr(request, 'references')
            assert request.references.merchant_reference == 'REF003:ref789'

    def test_custom_merchant_reference(self, mock_cards_df):
        """Test custom merchant reference"""
        row = pd.Series({
            'test_id': 'REF004',
            'amount': 300,
            'currency': 'GBP',
            'card_id': 'card1',
            'merchant_reference': 'CUSTOM_REF_123'
        })
        
        with patch('src.request_builders.standalone_refund.generate_random_string', return_value='ref999'):
            request = build_standalone_refund_request(row, mock_cards_df)
            
            # Should use custom merchant reference
            assert request.references.merchant_reference == 'CUSTOM_REF_123'

    def test_card_payment_data_structure(self, mock_cards_df):
        """Test card payment data structure"""
        row = pd.Series({
            'test_id': 'REF005',
            'amount': 400,
            'currency': 'EUR',
            'card_id': 'card1'
        })
        
        request = build_standalone_refund_request(row, mock_cards_df)
        
        # Verify card payment data
        card_data = request.card_payment_data
        assert card_data.brand == 'VISA'
        assert card_data.capture_immediately == True  # Default
        assert card_data.card_entry_mode == 'ECOMMERCE'  # Default
        assert card_data.cardholder_verification_method == 'CARD_SECURITY_CODE'  # Default
        
        # Verify card data
        plain_card_data = card_data.card_data
        assert plain_card_data.card_number == '4111111111111111'
        assert plain_card_data.expiry_date == '122025'
        assert plain_card_data.card_security_code == '123'

    def test_request_cleaning_called(self, mock_cards_df):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'REF006',
            'amount': 250,
            'currency': 'USD',
            'card_id': 'card1'
        })
        
        with patch('src.request_builders.standalone_refund.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_standalone_refund_request(row, mock_cards_df)
            mock_clean.assert_called_once()

    def test_build_with_brand_selector_merchant(self):
        """Test building request with merchant brand selector"""
        row = pd.Series({
            'test_id': 'REF_BRAND_001',
            'card_id': 'card1',
            'currency': 'EUR',
            'amount': 500,
            'brand_selector': 'MERCHANT'
        })
        
        cards_df = pd.DataFrame({
            'card_number': ['4111111111111111'],
            'expiry_date': ['1225'],
            'card_brand': ['VISA'],
            'card_security_code': ['123']
        }, index=['card1'])
        
        request = build_standalone_refund_request(row, cards_df)
        
        assert hasattr(request, 'card_payment_data')
        assert hasattr(request.card_payment_data, 'brand_selector')
        assert request.card_payment_data.brand_selector == 'MERCHANT'

    def test_build_with_brand_selector_cardholder(self):
        """Test building request with cardholder brand selector"""
        row = pd.Series({
            'test_id': 'REF_BRAND_002',
            'card_id': 'card1',
            'currency': 'EUR',
            'amount': 500,
            'brand_selector': 'CARDHOLDER'
        })
        
        cards_df = pd.DataFrame({
            'card_number': ['4111111111111111'],
            'expiry_date': ['1225'],
            'card_brand': ['VISA'],
            'card_security_code': ['123']
        }, index=['card1'])
        
        request = build_standalone_refund_request(row, cards_df)
        
        assert request.card_payment_data.brand_selector == 'CARDHOLDER'

    def test_build_with_merchant_data(self):
        """Test building standalone refund request with merchant data"""
        row = pd.Series({
            'test_id': 'REF_MERCH_001',
            'card_id': 'card1',
            'currency': 'EUR',
            'amount': 500,
            'merchant_data': 'EU_MERCHANT'
        })
        
        # Mock merchantdata DataFrame
        merchantdata_df = pd.DataFrame({
            'merchant_category_code': [5411],
            'name': ['European Grocery Store'],
            'address': ['456 High Street'],
            'postal_code': ['SW1A 1AA'],
            'city': ['London'],
            'state_code': [None],
            'country_code': ['GB']
        }, index=['EU_MERCHANT'])
        
        cards_df = pd.DataFrame({
            'card_number': ['4111111111111111'],
            'expiry_date': ['1225'],
            'card_brand': ['VISA'],
            'card_sequence_number': [None],
            'card_security_code': ['123']
        }, index=['card1'])
        
        request = build_standalone_refund_request(row, cards_df, merchantdata=merchantdata_df)
        
        # Should have merchant data
        assert hasattr(request, 'merchant_data')
        assert request.merchant_data.merchant_category_code == 5411
        assert request.merchant_data.name == 'European Grocery Store'
        assert request.merchant_data.country_code == 'GB'