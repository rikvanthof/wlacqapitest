"""Get payment endpoint implementation"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import get_payment

@register_endpoint('get_payment')
class GetPaymentEndpoint(EndpointInterface):
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, payment_id):
        return get_payment(client, acquirer_id, merchant_id, payment_id)
    
    @staticmethod
    def build_request(row, cards=None, address=None, networktokens=None, threeds=None):
        return None  # GET requests don't need request bodies
    
    @staticmethod
    def get_dependencies():
        return ['payment_id']
    
    @staticmethod
    def supports_chaining():
        return True
    
    @staticmethod
    def get_output_keys():
        return []  # Doesn't create new IDs