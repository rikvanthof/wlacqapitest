"""Capture Refund endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import capture_refund_call
from ..request_builders.capture_refund import build_capture_refund_request

@register_endpoint('capture_refund')
class CaptureRefundEndpoint(EndpointInterface):
    """Capture refund endpoint for capturing authorized refunds"""
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, refund_id, request):
        """Execute capture refund API call"""
        return capture_refund_call(client, acquirer_id, merchant_id, refund_id, request)
    
    @staticmethod
    def build_request(row, **kwargs):
        """Build capture refund request"""
        return build_capture_refund_request(row)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, **kwargs):
        """Build capture refund request - no DCC support for captures"""
        return build_capture_refund_request(row)
    
    @staticmethod
    def supports_dcc() -> bool:
        """Capture refund does not support DCC"""
        return False
    
    @staticmethod
    def get_dependencies() -> list:
        """Capture refund requires refund_id from previous operations"""
        return ['refund_id']