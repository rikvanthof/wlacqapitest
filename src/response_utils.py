"""Response processing utilities"""

import pandas as pd
from typing import Any, Optional, Dict
from unittest.mock import Mock
from .logging_config import get_main_logger

def _is_meaningful_value(value):
    """Check if a value is meaningful (not a Mock object)"""
    if isinstance(value, Mock):
        return False
    if callable(value):
        return False
    return value is not None

def get_transaction_id(response: Any, call_type: str) -> str:
    """Extract transaction ID from API response"""
    try:
        # For known call types, use specific logic
        if call_type == 'create_payment':
            if hasattr(response, 'payment_id') and _is_meaningful_value(response.payment_id):
                return response.payment_id
        
        elif call_type in ['increment_payment', 'capture_payment']:
            # Check nested payment.payment_id first
            if (hasattr(response, 'payment') and 
                hasattr(response.payment, 'payment_id') and 
                _is_meaningful_value(response.payment.payment_id)):
                return response.payment.payment_id
        
        elif call_type in ['refund_payment', 'get_refund']:
            # Check refund responses
            if (hasattr(response, 'refund') and 
                hasattr(response.refund, 'refund_id') and 
                _is_meaningful_value(response.refund.refund_id)):
                return response.refund.refund_id
        
        elif call_type == 'get_payment':
            if hasattr(response, 'payment_id') and _is_meaningful_value(response.payment_id):
                return response.payment_id
        
        # For unknown call types, prioritize generic 'id' field over payment_id
        if hasattr(response, 'id') and _is_meaningful_value(response.id):
            return response.id
        
        # Fallback to payment_id for unknown types if id doesn't exist
        if hasattr(response, 'payment_id') and _is_meaningful_value(response.payment_id):
            return response.payment_id
            
        # Check nested payment.payment_id for unknown types
        if (hasattr(response, 'payment') and 
            hasattr(response.payment, 'payment_id') and 
            _is_meaningful_value(response.payment.payment_id)):
            return response.payment.payment_id
            
        # Check refund responses for unknown types
        if (hasattr(response, 'refund') and 
            hasattr(response.refund, 'refund_id') and 
            _is_meaningful_value(response.refund.refund_id)):
            return response.refund.refund_id
            
        # Fallback to dictionary approach
        if hasattr(response, 'to_dictionary'):
            resp_dict = response.to_dictionary()
            if 'payment' in resp_dict and 'paymentId' in resp_dict['payment']:
                return resp_dict['payment']['paymentId']
            elif 'paymentId' in resp_dict:
                return resp_dict['paymentId']
            elif 'refund' in resp_dict and 'refundId' in resp_dict['refund']:
                return resp_dict['refund']['refundId']
        
        return ''
    except Exception:
        return ''

def get_response_status(response: Any, call_type: str) -> Optional[str]:
    """Extract response status from API response"""
    try:
        # Check direct status first (create_payment)
        if hasattr(response, 'status') and _is_meaningful_value(response.status):
            return response.status
            
        # Check nested payment.status (increment_payment, capture_payment)
        if (hasattr(response, 'payment') and 
            hasattr(response.payment, 'status') and 
            _is_meaningful_value(response.payment.status)):
            return response.payment.status
            
        # Check refund responses
        if (hasattr(response, 'refund') and 
            hasattr(response.refund, 'status') and 
            _is_meaningful_value(response.refund.status)):
            return response.refund.status
            
        # Fallback to dictionary approach
        if hasattr(response, 'to_dictionary'):
            resp_dict = response.to_dictionary()
            if 'payment' in resp_dict and 'status' in resp_dict['payment']:
                return resp_dict['payment']['status']
            elif 'status' in resp_dict:
                return resp_dict['status']
            elif 'refund' in resp_dict and 'status' in resp_dict['refund']:
                return resp_dict['refund']['status']
        
        # Return None when no status found (instead of 'UNKNOWN')
        return None
    except Exception:
        return None

def update_previous_outputs(response: Any, call_type: str, previous_outputs: Dict[str, Any]):
    """Update previous outputs with response data for chain dependencies"""
    logger = get_main_logger()
    
    try:
        if call_type == 'create_payment':
            payment_id = get_transaction_id(response, call_type)
            if payment_id:
                previous_outputs['payment_id'] = payment_id
                logger.info(f"Updated previous_outputs with payment_id: {payment_id}")
        
        elif call_type == 'refund_payment':
            refund_id = get_transaction_id(response, call_type)
            if refund_id:
                previous_outputs['refund_id'] = refund_id
                logger.info(f"Updated previous_outputs with refund_id: {refund_id}")
    
    except Exception as e:
        logger.warning(f"Failed to update previous outputs: {e}")

def get_card_description(call_type: str, cards: pd.DataFrame, card_id: Optional[str]) -> str:
    """Get card description for result reporting"""
    try:
        if call_type == 'create_payment' and card_id and pd.notna(card_id):
            if card_id in cards.index:
                return cards.loc[card_id, 'card_description']
        return 'N/A'
    except Exception:
        return 'N/A'