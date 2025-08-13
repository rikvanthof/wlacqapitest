"""Refund payment endpoint implementation"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import refund
from ..request_builders.refund_payment import build_refund_payment_request

@register_endpoint('refund_payment')
class RefundPaymentEndpoint(EndpointInterface):
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, payment_id, request):
        return refund(client, acquirer_id, merchant_id, payment_id, request)
    
    @staticmethod
    def build_request(row, cards=None, address=None, networktokens=None, threeds=None):
        return build_refund_payment_request(row)
    
    @staticmethod
    def get_dependencies():
        return ['payment_id']
    
    @staticmethod
    def supports_chaining():
        return True
    
    @staticmethod
    def get_output_keys():
        return ['refund_id']