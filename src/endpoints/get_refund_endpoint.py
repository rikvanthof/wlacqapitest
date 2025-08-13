"""Get refund endpoint implementation"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import get_refund

@register_endpoint('get_refund')
class GetRefundEndpoint(EndpointInterface):
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, refund_id):
        return get_refund(client, acquirer_id, merchant_id, refund_id)
    
    @staticmethod
    def build_request(row, cards=None, address=None, networktokens=None, threeds=None):
        return None  # GET requests don't need request bodies
    
    @staticmethod
    def get_dependencies():
        return ['refund_id']
    
    @staticmethod
    def supports_chaining():
        return True
    
    @staticmethod
    def get_output_keys():
        return []  # Doesn't create new IDs