"""Ping endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import ping_call

@register_endpoint('ping')
class PingEndpoint(EndpointInterface):
    """Ping endpoint for testing API connectivity"""
    
    @staticmethod
    def call_api(client, **kwargs):
        """Execute ping API call - no parameters needed!"""
        return ping_call(client)
    
    @staticmethod
    def build_request(row, **kwargs):
        """Ping has no request body"""
        return None
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, **kwargs):
        """Ping has no request body and no DCC support"""
        return None
    
    @staticmethod
    def supports_dcc() -> bool:
        """Ping does not support DCC"""
        return False
    
    @staticmethod
    def get_dependencies() -> list:
        """Ping requires no dependencies"""
        return []