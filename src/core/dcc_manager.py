"""DCC (Dynamic Currency Conversion) management for test chains"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd
import logging

@dataclass
class DCCContext:
    """DCC context for a test chain"""
    rate_reference_id: Optional[str] = None
    original_amount: Optional[Dict[str, Any]] = None
    resulting_amount: Optional[Dict[str, Any]] = None
    inverted_exchange_rate: Optional[float] = None
    target_currency: Optional[str] = None
    merchant_currency: Optional[str] = None

class DCCManager:
    """Manages DCC operations and context within test chains"""
    
    def __init__(self):
        self.chain_contexts: Dict[str, DCCContext] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_chain_context(self, chain_id: str) -> DCCContext:
        """Get or create DCC context for a chain"""
        if chain_id not in self.chain_contexts:
            self.chain_contexts[chain_id] = DCCContext()
        return self.chain_contexts[chain_id]
    
    def should_perform_dcc_inquiry(self, row: pd.Series) -> bool:
        """Determine if DCC inquiry should be performed for this step"""
        use_dcc = str(row.get('use_dcc', '')).upper() == 'TRUE'
        call_type = row.get('call_type', '')
        
        # Only perform DCC for payment/refund operations (not get_payment, get_refund)
        dcc_supported_calls = [
            'create_payment', 'increment_payment', 'capture_payment', 
            'refund_payment', 'payment_authorization_reversal', 'standalone_refund'
        ]
        
        return use_dcc and call_type in dcc_supported_calls
    
    def determine_transaction_type(self, call_type: str) -> str:
        """Determine transaction type for DCC inquiry based on call type"""
        payment_calls = [
            'create_payment', 'increment_payment', 'capture_payment', 
            'payment_authorization_reversal'
        ]
        refund_calls = ['refund_payment', 'standalone_refund']
        
        if call_type in payment_calls:
            return 'PAYMENT'
        elif call_type in refund_calls:
            return 'REFUND'
        else:
            # This shouldn't happen given our should_perform_dcc_inquiry check
            raise ValueError(f"Unsupported call type for DCC: {call_type}")
    
    def update_context_from_dcc_response(self, chain_id: str, dcc_response: Any):
        """Update chain context with DCC rate response data"""
        context = self.get_chain_context(chain_id)
        
        # Extract data from DCC response based on your sample structure
        if hasattr(dcc_response, 'proposal'):
            proposal = dcc_response.proposal
            
            if hasattr(proposal, 'rate_reference_id'):
                context.rate_reference_id = proposal.rate_reference_id
                self.logger.info(f"DCC rate reference ID: {context.rate_reference_id}")
            
            if hasattr(proposal, 'original_amount'):
                context.original_amount = {
                    'amount': proposal.original_amount.amount,
                    'currency_code': proposal.original_amount.currency_code,
                    'number_of_decimals': proposal.original_amount.number_of_decimals
                }
            
            if hasattr(proposal, 'resulting_amount'):
                context.resulting_amount = {
                    'amount': proposal.resulting_amount.amount,
                    'currency_code': proposal.resulting_amount.currency_code,
                    'number_of_decimals': proposal.resulting_amount.number_of_decimals
                }
                self.logger.info(f"DCC resulting amount: {context.resulting_amount}")
            
            if hasattr(proposal, 'rate') and hasattr(proposal.rate, 'inverted_exchange_rate'):
                context.inverted_exchange_rate = float(proposal.rate.inverted_exchange_rate)
                self.logger.info(f"DCC exchange rate: {context.inverted_exchange_rate}")
    
    def get_transaction_amount_for_api(self, chain_id: str, test_amount: int, test_currency: str) -> Dict[str, Any]:
        """Get the amount to use for actual API transaction"""
        context = self.get_chain_context(chain_id)
        
        if context.resulting_amount:
            # Use DCC resulting amount (customer currency amount)
            return context.resulting_amount
        else:
            # Fallback to test amount (merchant currency)
            return {
                'amount': test_amount,
                'currency_code': test_currency,
                'number_of_decimals': 2
            }
    
    def clear_chain_context(self, chain_id: str):
        """Clear DCC context for a chain (useful for cleanup)"""
        if chain_id in self.chain_contexts:
            del self.chain_contexts[chain_id]

def perform_dcc_inquiry(row, call_type, client, merchant_info, dcc_manager, chain_id, cards=None, verbose=False):
    """✅ NEW: Perform DCC inquiry for a test step"""
    
    # Check if DCC inquiry should be performed
    if not dcc_manager.should_perform_dcc_inquiry(row):
        return None
    
    # Get existing rate reference ID from chain context
    context = dcc_manager.get_chain_context(chain_id)
    existing_rate_ref = context.rate_reference_id
    
    if verbose:
        print(f"[{chain_id}] Performing DCC inquiry for {dcc_manager.determine_transaction_type(call_type)} (existing rate: {existing_rate_ref})")
    
    logger = logging.getLogger(__name__)
    logger.info(f"[{chain_id}] DCC inquiry: {dcc_manager.determine_transaction_type(call_type)}, rate_ref: {existing_rate_ref}")
    
    # Get DCC endpoint from registry
    from ..core.endpoint_registry import EndpointRegistry
    dcc_endpoint = EndpointRegistry.get_endpoint('get_dcc_rate')
    if not dcc_endpoint:
        raise ValueError("DCC endpoint not found in registry")
    
    # Build DCC request
    try:
        transaction_type = dcc_manager.determine_transaction_type(call_type)
        dcc_request = dcc_endpoint.build_request(
            row, 
            transaction_type, 
            existing_rate_ref,
            cards  # ✅ Pass cards data for BIN extraction
        )
    except Exception as e:
        raise ValueError(f"Failed to build DCC request: {e}")
    
    # Execute DCC API call
    try:
        dcc_response = dcc_endpoint.call_api(
            client,
            merchant_info['acquirer_id'],
            merchant_info['merchant_id'],
            dcc_request
        )
        
        # Update DCC context with response
        dcc_manager.update_context_from_dcc_response(chain_id, dcc_response)
        
        if verbose:
            print(f"[{chain_id}] DCC inquiry successful, rate ID: {context.rate_reference_id}")
        
        return dcc_response
        
    except Exception as e:
        error_msg = f"DCC inquiry failed for {call_type}: {e}"
        logger.error(f"[{chain_id}] {error_msg}")
        raise ValueError(error_msg)
    
def update_context_from_dcc_response(self, chain_id: str, dcc_response: Any):
    """Update chain context with DCC rate response data"""
    context = self.get_chain_context(chain_id)

    # Extract data from DCC response based on your sample structure
    if hasattr(dcc_response, 'proposal'):
        proposal = dcc_response.proposal
        
        if hasattr(proposal, 'rate_reference_id'):
            context.rate_reference_id = proposal.rate_reference_id
            self.logger.info(f"DCC rate reference ID: {context.rate_reference_id}")
        
        if hasattr(proposal, 'original_amount'):
            context.original_amount = {
                'amount': proposal.original_amount.amount,
                'currency_code': proposal.original_amount.currency_code,
                'number_of_decimals': proposal.original_amount.number_of_decimals
            }
        
        if hasattr(proposal, 'resulting_amount'):
            context.resulting_amount = {
                'amount': proposal.resulting_amount.amount,
                'currency_code': proposal.resulting_amount.currency_code,
                'number_of_decimals': proposal.resulting_amount.number_of_decimals
            }
            self.logger.info(f"DCC resulting amount: {context.resulting_amount}")
        
        # ✅ ENHANCED: Extract conversion rate from rate object
        if hasattr(proposal, 'rate'):
            rate = proposal.rate
            if hasattr(rate, 'inverted_exchange_rate'):
                context.inverted_exchange_rate = float(rate.inverted_exchange_rate)
                self.logger.info(f"DCC exchange rate: {context.inverted_exchange_rate}")
            
            # Store additional rate information that might be needed
            if hasattr(rate, 'exchange_rate'):
                context.exchange_rate = float(rate.exchange_rate)
            if hasattr(rate, 'mark_up'):
                context.mark_up = float(rate.mark_up)