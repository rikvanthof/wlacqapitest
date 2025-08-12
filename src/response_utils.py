"""Helper functions for processing API responses with comprehensive logging"""

import logging

logger = logging.getLogger(__name__)

def get_transaction_id(response, call_type):
    """Extract transaction ID from different response types"""
    logger.debug(f"Extracting transaction ID for call_type: {call_type}")
    logger.debug(f"Response type: {type(response).__name__}")
    
    try:
        if call_type == 'create_payment':
            transaction_id = response.payment_id
            logger.debug(f"Extracted payment_id from create_payment: {transaction_id}")
            return transaction_id
            
        elif call_type == 'increment_payment':
            # ApiIncrementResponse has nested payment.paymentId
            if hasattr(response, 'payment'):
                transaction_id = response.payment.payment_id
                logger.debug(f"Extracted payment_id from increment_payment: {transaction_id}")
                return transaction_id
            else:
                logger.warning("increment_payment response missing 'payment' attribute")
                return None
                
        elif call_type == 'refund_payment':
            # ApiActionResponseForRefund has nested refund.refundId
            if hasattr(response, 'refund'):
                transaction_id = response.refund.refund_id
                logger.debug(f"Extracted refund_id from refund_payment: {transaction_id}")
                return transaction_id
            else:
                logger.warning("refund_payment response missing 'refund' attribute")
                return None
                
        elif call_type in ['get_payment']:
            if hasattr(response, 'payment_id'):
                transaction_id = response.payment_id
                logger.debug(f"Extracted payment_id from get_payment: {transaction_id}")
                return transaction_id
            else:
                logger.warning("get_payment response missing 'payment_id' attribute")
                return None
                
        elif call_type in ['get_refund']:
            if hasattr(response, 'refund_id'):
                transaction_id = response.refund_id
                logger.debug(f"Extracted refund_id from get_refund: {transaction_id}")
                return transaction_id
            else:
                logger.warning("get_refund response missing 'refund_id' attribute")
                return None
                
        else:
            # Fallback for other types
            logger.debug(f"Using fallback extraction for call_type: {call_type}")
            fallback_id = getattr(response, 'id', getattr(response, 'payment_id', None))
            if fallback_id:
                logger.debug(f"Extracted fallback transaction ID: {fallback_id}")
            else:
                logger.warning(f"No transaction ID found for call_type: {call_type}")
            return fallback_id
            
    except Exception as e:
        logger.error(f"Error extracting transaction ID for {call_type}: {e}")
        return None

def get_response_status(response, call_type):
    """Extract status from different response types"""
    logger.debug(f"Extracting status for call_type: {call_type}")
    logger.debug(f"Response type: {type(response).__name__}")
    
    try:
        if call_type == 'increment_payment':
            # ApiIncrementResponse has nested payment.status
            if hasattr(response, 'payment'):
                status = response.payment.status
                logger.debug(f"Extracted status from increment_payment: {status}")
                return status
            else:
                logger.warning("increment_payment response missing 'payment' attribute")
                return None
                
        elif call_type == 'refund_payment':
            # ApiActionResponseForRefund has nested refund.status
            if hasattr(response, 'refund'):
                status = response.refund.status
                logger.debug(f"Extracted status from refund_payment: {status}")
                return status
            else:
                logger.warning("refund_payment response missing 'refund' attribute")
                return None
                
        else:
            # Most other responses have status directly
            status = getattr(response, 'status', None)
            if status:
                logger.debug(f"Extracted direct status from {call_type}: {status}")
            else:
                logger.warning(f"No status found for call_type: {call_type}")
            return status
            
    except Exception as e:
        logger.error(f"Error extracting status for {call_type}: {e}")
        return None

def update_previous_outputs(response, call_type, previous_outputs):
    """Update previous_outputs with IDs from successful responses"""
    logger.debug(f"Updating previous outputs for call_type: {call_type}")
    logger.debug(f"Current previous_outputs: {list(previous_outputs.keys())}")
    
    try:
        if call_type == 'create_payment':
            if hasattr(response, 'payment_id'):
                previous_outputs['payment_id'] = response.payment_id
                logger.info(f"Updated previous_outputs with payment_id: {response.payment_id}")
            else:
                logger.warning("create_payment response missing payment_id")
                
        elif call_type == 'refund_payment':
            # Store refund_id from nested structure
            if hasattr(response, 'refund') and hasattr(response.refund, 'refund_id'):
                previous_outputs['refund_id'] = response.refund.refund_id
                logger.info(f"Updated previous_outputs with refund_id: {response.refund.refund_id}")
            else:
                logger.warning("refund_payment response missing refund.refund_id")
        
        logger.debug(f"Updated previous_outputs keys: {list(previous_outputs.keys())}")
        
    except Exception as e:
        logger.error(f"Error updating previous outputs for {call_type}: {e}")

def get_card_description(call_type, cards, card_id):
    """Get card description for result records"""
    logger.debug(f"Getting card description - call_type: {call_type}, card_id: {card_id}")
    
    try:
        if call_type == 'create_payment' and card_id:
            if card_id in cards.index:
                description = cards.loc[card_id].get('card_description', 'N/A')
                logger.debug(f"Found card description: {description}")
                return description
            else:
                logger.warning(f"Card ID {card_id} not found in cards DataFrame")
                return 'N/A'
        else:
            logger.debug(f"No card description needed for call_type: {call_type}")
            return 'N/A'
            
    except (KeyError, AttributeError) as e:
        logger.warning(f"Error retrieving card description: {e}")
        return 'N/A'
    except Exception as e:
        logger.error(f"Unexpected error retrieving card description: {e}")
        return 'N/A'