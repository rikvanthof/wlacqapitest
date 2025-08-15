"""Refund Payment endpoint with DCC support"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import refund
from ..request_builders.refund_payment import build_refund_payment_request
from typing import List

@register_endpoint('refund_payment')
class RefundPaymentEndpoint(EndpointInterface):
    """Refund Payment endpoint with DCC support"""
    
    @staticmethod
    def call_api(client, acquirer_id: str, merchant_id: str, payment_id: str, request):
        """Execute refund payment API call"""
        return refund(client, acquirer_id, merchant_id, payment_id, request)
    
    @staticmethod
    def build_request(row):
        """Build refund payment request"""
        return build_refund_payment_request(row)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None):
        """✅ NEW: Build refund payment request with DCC context"""
        return build_refund_payment_request(row, dcc_context=dcc_context)
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """Refund payment requires payment_id"""
        return ['payment_id']
    
    @staticmethod
    def supports_chaining() -> bool:
        """Refund payment can be used in chains"""
        return True
    
    @staticmethod
    def get_output_keys() -> List[str]:
        """Refund payment provides refund_id"""
        return ['refund_id']
    
    @staticmethod
    def supports_dcc() -> bool:
        """✅ NEW: Refund payment supports DCC"""
        return True