"""Create Payment endpoint with enhanced DCC support"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import create_payment
from ..request_builders.create_payment import build_create_payment_request
from typing import List

@register_endpoint('create_payment')
class CreatePaymentEndpoint(EndpointInterface):
    """Create Payment endpoint with full feature support including DCC"""
    
    @staticmethod
    def call_api(client, acquirer_id: str, merchant_id: str, request):
        """Execute create payment API call"""
        return create_payment(client, acquirer_id, merchant_id, request)
    
    @staticmethod
    def build_request(row, cards=None, address=None, networktokens=None, threeds=None, cardonfile=None, previous_outputs=None, dcc_context=None):
        """Build create payment request with full feature support"""
        return build_create_payment_request(row, cards, address, networktokens, threeds, cardonfile, previous_outputs, dcc_context)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, cards=None, address=None, networktokens=None, threeds=None, cardonfile=None, previous_outputs=None):
        """Build create payment request with DCC context"""
        return build_create_payment_request(row, cards, address, networktokens, threeds, cardonfile, previous_outputs, dcc_context)
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """Create payment has no dependencies"""
        return []
    
    @staticmethod
    def supports_chaining() -> bool:
        """Create payment can be used in chains"""
        return True
    
    @staticmethod
    def get_output_keys() -> List[str]:
        """Create payment provides payment_id"""
        return ['payment_id']
    
    @staticmethod
    def supports_dcc() -> bool:
        """✅ NEW: Create payment supports DCC"""
        return True