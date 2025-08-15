"""Increment Payment endpoint with DCC support"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import increment_auth
from ..request_builders.increment_payment import build_increment_payment_request
from typing import List

@register_endpoint('increment_payment')
class IncrementPaymentEndpoint(EndpointInterface):
    """Increment Payment endpoint with DCC support"""
    
    @staticmethod
    def call_api(client, acquirer_id: str, merchant_id: str, payment_id: str, request):
        """Execute increment payment API call"""
        return increment_auth(client, acquirer_id, merchant_id, payment_id, request)
    
    @staticmethod
    def build_request(row):
        """Build increment payment request"""
        return build_increment_payment_request(row)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None):
        """✅ NEW: Build increment payment request with DCC context"""
        return build_increment_payment_request(row, dcc_context=dcc_context)
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """Increment payment requires payment_id"""
        return ['payment_id']
    
    @staticmethod
    def supports_chaining() -> bool:
        """Increment payment can be used in chains"""
        return True
    
    @staticmethod
    def get_output_keys() -> List[str]:
        """Increment payment doesn't add new keys"""
        return []
    
    @staticmethod
    def supports_dcc() -> bool:
        """✅ NEW: Increment payment supports DCC"""
        return True