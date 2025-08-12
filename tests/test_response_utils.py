"""Test response utility functions"""

import pytest
from unittest.mock import Mock
from src.response_utils import (
    get_transaction_id, get_response_status, update_previous_outputs, get_card_description
)

class TestGetTransactionId:
    """Test transaction ID extraction"""
    
    def test_create_payment_transaction_id(self, mock_api_payment_response):
        """Test transaction ID extraction from create_payment response"""
        result = get_transaction_id(mock_api_payment_response, 'create_payment')
        assert result == 'pay:test:12345'

    def test_increment_payment_transaction_id(self, mock_api_increment_response):
        """Test transaction ID extraction from increment_payment response"""
        result = get_transaction_id(mock_api_increment_response, 'increment_payment')
        assert result == 'pay:test:12345'

    def test_refund_payment_transaction_id(self, mock_api_refund_response):
        """Test transaction ID extraction from refund_payment response"""
        result = get_transaction_id(mock_api_refund_response, 'refund_payment')
        assert result == 'refund:test:67890'

    def test_get_payment_transaction_id(self):
        """Test transaction ID extraction from get_payment response"""
        response = Mock()
        response.payment_id = 'pay:test:54321'
        
        result = get_transaction_id(response, 'get_payment')
        assert result == 'pay:test:54321'

    def test_unknown_call_type_fallback(self):
        """Test fallback for unknown call types"""
        response = Mock()
        response.id = 'fallback:123'
        response.payment_id = 'pay:test:456'
        
        result = get_transaction_id(response, 'unknown_type')
        assert result == 'fallback:123'

class TestGetResponseStatus:
    """Test response status extraction"""
    
    def test_increment_payment_status(self, mock_api_increment_response):
        """Test status extraction from increment_payment response"""
        result = get_response_status(mock_api_increment_response, 'increment_payment')
        assert result == 'AUTHORIZED'

    def test_refund_payment_status(self, mock_api_refund_response):
        """Test status extraction from refund_payment response"""
        result = get_response_status(mock_api_refund_response, 'refund_payment')
        assert result == 'REFUNDED'

    def test_direct_status_field(self, mock_api_payment_response):
        """Test status extraction from direct status field"""
        result = get_response_status(mock_api_payment_response, 'create_payment')
        assert result == 'AUTHORIZED'

    def test_missing_status_field(self):
        """Test status extraction when status field is missing"""
        response = Mock()
        del response.status  # Remove status attribute
        
        result = get_response_status(response, 'create_payment')
        assert result is None

class TestUpdatePreviousOutputs:
    """Test previous outputs update"""
    
    def test_create_payment_updates_payment_id(self, mock_api_payment_response):
        """Test that create_payment updates payment_id"""
        previous_outputs = {}
        
        update_previous_outputs(mock_api_payment_response, 'create_payment', previous_outputs)
        
        assert previous_outputs['payment_id'] == 'pay:test:12345'

    def test_refund_payment_updates_refund_id(self, mock_api_refund_response):
        """Test that refund_payment updates refund_id"""
        previous_outputs = {'payment_id': 'existing_payment'}
        
        update_previous_outputs(mock_api_refund_response, 'refund_payment', previous_outputs)
        
        assert previous_outputs['payment_id'] == 'existing_payment'  # Unchanged
        assert previous_outputs['refund_id'] == 'refund:test:67890'

    def test_other_call_types_no_update(self, mock_api_payment_response):
        """Test that other call types don't update previous_outputs"""
        previous_outputs = {'existing': 'value'}
        
        update_previous_outputs(mock_api_payment_response, 'get_payment', previous_outputs)
        
        assert previous_outputs == {'existing': 'value'}

class TestGetCardDescription:
    """Test card description extraction"""
    
    def test_create_payment_with_valid_card(self, mock_cards_df):
        """Test card description for create_payment with valid card"""
        result = get_card_description('create_payment', mock_cards_df, 'card1')
        assert result == 'Test Visa'

    def test_create_payment_with_invalid_card(self, mock_cards_df):
        """Test card description for create_payment with invalid card"""
        result = get_card_description('create_payment', mock_cards_df, 'invalid_card')
        assert result == 'N/A'

    def test_non_create_payment_call_type(self, mock_cards_df):
        """Test card description for non-create_payment call types"""
        result = get_card_description('increment_payment', mock_cards_df, 'card1')
        assert result == 'N/A'

    def test_none_card_id(self, mock_cards_df):
        """Test card description with None card_id"""
        result = get_card_description('create_payment', mock_cards_df, None)
        assert result == 'N/A'