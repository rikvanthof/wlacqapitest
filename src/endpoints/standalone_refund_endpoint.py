"""Standalone Refund endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import standalone_refund_call
from ..request_builders.standalone_refund import build_standalone_refund_request

@register_endpoint('standalone_refund')
class StandaloneRefundEndpoint(EndpointInterface):
    """Standalone refund endpoint for independent refunds"""
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, request):
        """Execute standalone refund API call"""
        return standalone_refund_call(client, acquirer_id, merchant_id, request)
    
    @staticmethod
    def build_request(row, cards_df, **kwargs):
        """Build standalone refund request without DCC"""
        return build_standalone_refund_request(row, cards_df)
    
    @staticmethod
    def build_request_with_dcc(row, cards_df, dcc_context=None, **kwargs):
        """Build standalone refund request with DCC support"""
        return build_standalone_refund_request(row, cards_df, dcc_context)
    
    @staticmethod
    def supports_dcc() -> bool:
        """Standalone refund supports DCC"""
        return True
    
    @staticmethod
    def get_dependencies() -> list:
        """Standalone refund requires no dependencies"""
        return []  # No payment_id needed - it's standalone!