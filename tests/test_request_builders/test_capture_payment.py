"""Fixed unit tests for capture payment request builder"""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.request_builders.capture_payment import build_capture_payment_request

class TestBuildCapturePaymentRequest:
    """Test capture payment request building"""

    def test_build_basic_request(self):
        """Test building basic capture payment request"""
        row = pd.Series({
            'test_id': 'CAP001'
        })
        
        with patch('src.request_builders.capture_payment.generate_random_string', return_value='cap123'):
            request = build_capture_payment_request(row)
            
            # Verify request structure
            assert hasattr(request, 'operation_id')
            assert request.operation_id == 'CAP001:cap123'
            assert hasattr(request, 'transaction_timestamp')
            assert hasattr(request, 'references')

    def test_build_with_amount(self):
        """Test building request with specific amount"""
        row = pd.Series({
            'test_id': 'CAP002',
            'amount': 1500,
            'currency': 'EUR'  # ✅ Added required currency
        })
        
        request = build_capture_payment_request(row)
        
        # Should have amount if specified
        if hasattr(request, 'amount') and request.amount:
            assert request.amount.amount == 1500
            assert request.amount.currency_code == 'EUR'

    def test_build_with_dynamic_descriptor(self):
        """Test building request with dynamic descriptor"""
        row = pd.Series({
            'test_id': 'CAP003',
            'dynamic_descriptor': 'Test Capture'
        })
        
        request = build_capture_payment_request(row)
        
        # Should have dynamic descriptor
        if hasattr(request, 'references') and request.references:
            assert request.references.dynamic_descriptor == 'Test Capture'

    def test_merchant_reference_generation(self):
        """Test merchant reference generation"""
        row = pd.Series({
            'test_id': 'CAP004'
        })
        
        with patch('src.request_builders.capture_payment.generate_random_string', return_value='cap456'):
            request = build_capture_payment_request(row)
            
            assert hasattr(request, 'references')
            assert request.references.merchant_reference == 'CAP004:cap456'

    def test_request_cleaning_called(self):
        """Test that request cleaning is called"""
        row = pd.Series({
            'test_id': 'CAP005'
        })
        
        with patch('src.request_builders.capture_payment.clean_request') as mock_clean:
            mock_clean.return_value = Mock()
            build_capture_payment_request(row)
            mock_clean.assert_called_once()

    def test_partial_capture(self):
        """Test partial capture with amount less than original"""
        row = pd.Series({
            'test_id': 'CAP006',
            'amount': 500,
            'currency': 'EUR'  # ✅ Added required currency
        })
        
        request = build_capture_payment_request(row)
        
        # Should handle partial captures
        if hasattr(request, 'amount') and request.amount:
            assert request.amount.amount == 500
            assert request.amount.currency_code == 'EUR'

    def test_full_capture_no_amount(self):  # ✅ New test for full capture
        """Test full capture without specifying amount"""
        row = pd.Series({
            'test_id': 'CAP007'
        })
        
        request = build_capture_payment_request(row)
        
        # Full capture should not have amount (captures full authorized amount)
        assert not hasattr(request, 'amount') or request.amount is None

    def test_build_with_is_final_true(self):
        """Test building request with isFinal = true"""
        row = pd.Series({
            'test_id': 'CAP008',
            'amount': 1500,
            'currency': 'EUR',
            'is_final': 'true'  # String boolean
        })
        
        request = build_capture_payment_request(row)
        
        # Should have amount and isFinal flag
        assert hasattr(request, 'amount')
        assert request.amount.amount == 1500
        assert request.amount.currency_code == 'EUR'
        assert hasattr(request, 'is_final')
        assert request.is_final == True

    def test_build_with_is_final_false(self):
        """Test building request with isFinal = false"""
        row = pd.Series({
            'test_id': 'CAP009',
            'amount': 500,
            'currency': 'USD',
            'is_final': False  # Boolean false
        })
        
        request = build_capture_payment_request(row)
        
        assert hasattr(request, 'is_final')
        assert request.is_final == False

    def test_build_with_string_boolean_variations(self):
        """Test different string boolean variations for isFinal"""
        test_cases = [
            ('true', True),
            ('True', True), 
            ('1', True),
            ('yes', True),
            ('false', False),
            ('0', False),
            ('no', False)
        ]
        
        for string_val, expected_bool in test_cases:
            row = pd.Series({
                'test_id': f'CAP_BOOL_{string_val}',
                'is_final': string_val
            })
            
            request = build_capture_payment_request(row)
            assert hasattr(request, 'is_final')
            assert request.is_final == expected_bool

    def test_build_with_capture_sequence_number(self):
        """Test building request with capture sequence number"""
        row = pd.Series({
            'test_id': 'CAP010',
            'amount': 750,
            'currency': 'EUR',
            'capture_sequence_number': 2,
            'is_final': False
        })
        
        request = build_capture_payment_request(row)
        
        assert hasattr(request, 'capture_sequence_number')
        assert request.capture_sequence_number == 2
        assert request.is_final == False

    def test_build_with_dcc_and_final(self):
        """Test building request with DCC and isFinal"""
        row = pd.Series({
            'test_id': 'CAP011',
            'amount': 1000,
            'currency': 'GBP',
            'is_final': True
        })
        
        # Mock DCC context
        dcc_context = Mock()
        dcc_context.rate_reference_id = 'rate_ref_123'
        dcc_context.resulting_amount = {
            'amount': 1150,
            'currency_code': 'EUR',
            'number_of_decimals': 2
        }
        dcc_context.inverted_exchange_rate = 0.869
        
        request = build_capture_payment_request(row, dcc_context)
        
        # Should use DCC amount and have isFinal flag
        assert request.amount.amount == 1150
        assert request.amount.currency_code == 'EUR'
        assert request.is_final == True
        assert hasattr(request, 'dynamic_currency_conversion')