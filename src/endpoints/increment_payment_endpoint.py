"""Increment payment endpoint implementation"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import increment_auth
from ..request_builders.increment_payment import build_increment_payment_request

@register_endpoint('increment_payment')
class IncrementPaymentEndpoint(EndpointInterface):
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, payment_id, request):
        return increment_auth(client, acquirer_id, merchant_id, payment_id, request)
    
    @staticmethod
    def build_request(row, cards=None, address=None, networktokens=None, threeds=None):
        return build_increment_payment_request(row)
    
    @staticmethod
    def get_dependencies():
        return ['payment_id']
    
    @staticmethod
    def supports_chaining():
        return True
    
    @staticmethod
    def get_output_keys():
        return []  # Doesn't create new IDs