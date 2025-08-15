"""Reverse Authorization endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import reverse_authorization_call
from ..request_builders.reverse_authorization import build_reverse_authorization_request

@register_endpoint('reverse_authorization')
class ReverseAuthorizationEndpoint(EndpointInterface):
    """Reverse authorization endpoint for voiding payments"""
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, payment_id, request):
        """Execute reverse authorization API call"""
        return reverse_authorization_call(client, acquirer_id, merchant_id, payment_id, request)
    
    @staticmethod
    def build_request(row, **kwargs):
        """Build reverse authorization request without DCC"""
        return build_reverse_authorization_request(row)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, **kwargs):
        """Build reverse authorization request with DCC support"""
        return build_reverse_authorization_request(row, dcc_context)
    
    @staticmethod
    def supports_dcc() -> bool:
        """Reverse authorization supports DCC"""
        return True
    
    @staticmethod
    def get_dependencies() -> list:
        """Reverse authorization requires payment_id from previous operations"""
        return ['payment_id']