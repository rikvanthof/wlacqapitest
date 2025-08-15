"""Capture Payment endpoint - standardized pattern"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import capture
from ..request_builders.capture_payment import build_capture_payment_request
from typing import List

@register_endpoint('capture_payment')
class CapturePaymentEndpoint(EndpointInterface):
    """Capture Payment endpoint with DCC support"""
    
    @staticmethod
    def call_api(client, acquirer_id: str, merchant_id: str, payment_id: str, request):
        """Execute capture payment API call"""
        return capture(client, acquirer_id, merchant_id, payment_id, request)
    
    @staticmethod
    def build_request(row):
        """Build capture payment request"""
        return build_capture_payment_request(row)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None):
        """Build capture payment request with DCC context"""
        return build_capture_payment_request(row, dcc_context=dcc_context)
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """Capture payment requires payment_id"""
        return ['payment_id']
    
    @staticmethod
    def supports_chaining() -> bool:
        """Capture payment can be used in chains"""
        return True
    
    @staticmethod
    def get_output_keys() -> List[str]:
        """Capture payment doesn't provide additional outputs"""
        return []
    
    @staticmethod
    def supports_dcc() -> bool:
        """Capture payment supports DCC"""
        return True