"""Reverse Refund Authorization endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import reverse_refund_authorization_call
from ..request_builders.reverse_refund_authorization import build_reverse_refund_authorization_request

@register_endpoint('reverse_refund_authorization')
class ReverseRefundAuthorizationEndpoint(EndpointInterface):
    """Reverse refund authorization endpoint for voiding refund authorizations"""
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, refund_id, request):
        """Execute reverse refund authorization API call"""
        return reverse_refund_authorization_call(client, acquirer_id, merchant_id, refund_id, request)
    
    @staticmethod
    def build_request(row, **kwargs):
        """Build reverse refund authorization request"""
        return build_reverse_refund_authorization_request(row)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, **kwargs):
        """Build reverse refund authorization request - no DCC support"""
        return build_reverse_refund_authorization_request(row)
    
    @staticmethod
    def supports_dcc() -> bool:
        """Reverse refund authorization does not support DCC"""
        return False
    
    @staticmethod
    def get_dependencies() -> list:
        """Reverse refund authorization requires refund_id from previous operations"""
        return ['refund_id']