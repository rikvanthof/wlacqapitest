"""Response processing utilities"""

import pandas as pd
from typing import Any, Optional, Dict
from .logging_config import get_main_logger

def get_transaction_id(response: Any, call_type: str) -> str:
    """Extract transaction ID from API response"""
    try:
        if hasattr(response, 'payment_id'):
            return response.payment_id
        elif hasattr(response, 'refund') and hasattr(response.refund, 'refund_id'):
            return response.refund.refund_id
        elif hasattr(response, 'to_dictionary'):
            resp_dict = response.to_dictionary()
            if 'paymentId' in resp_dict:
                return resp_dict['paymentId']
            elif 'refund' in resp_dict and 'refundId' in resp_dict['refund']:
                return resp_dict['refund']['refundId']
        return ''
    except Exception:
        return ''

def get_response_status(response: Any, call_type: str) -> str:
    """Extract response status from API response"""
    try:
        if hasattr(response, 'status'):
            return response.status
        elif hasattr(response, 'payment') and hasattr(response.payment, 'status'):
            return response.payment.status
        elif hasattr(response, 'refund') and hasattr(response.refund, 'status'):
            return response.refund.status
        elif hasattr(response, 'to_dictionary'):
            resp_dict = response.to_dictionary()
            if 'status' in resp_dict:
                return resp_dict['status']
            elif 'payment' in resp_dict and 'status' in resp_dict['payment']:
                return resp_dict['payment']['status']
            elif 'refund' in resp_dict and 'status' in resp_dict['refund']:
                return resp_dict['refund']['status']
        return 'UNKNOWN'
    except Exception:
        return 'UNKNOWN'

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