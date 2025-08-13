"""Create payment endpoint implementation"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import create_payment
from ..request_builders.create_payment import build_create_payment_request

@register_endpoint('create_payment')
class CreatePaymentEndpoint(EndpointInterface):
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, request):
        return create_payment(client, acquirer_id, merchant_id, request)
    
    @staticmethod
    def build_request(row, cards, address, networktokens, threeds):
        return build_create_payment_request(row, cards, address, networktokens, threeds)
    
    @staticmethod
    def get_dependencies():
        return []  # No dependencies needed
    
    @staticmethod
    def supports_chaining():
        return True
    
    @staticmethod
    def get_output_keys():
        return ['payment_id']