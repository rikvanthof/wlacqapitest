"""Technical Reversal endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import technical_reversal_call
from ..request_builders.technical_reversal import build_technical_reversal_request

@register_endpoint('technical_reversal')
class TechnicalReversalEndpoint(EndpointInterface):
    """Technical reversal endpoint for blind reversals of operations"""
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, original_operation_id, request):
        """Execute technical reversal API call
        
        Args:
            client: API client
            acquirer_id: Acquirer identifier
            merchant_id: Merchant identifier  
            original_operation_id: The operationId from the previous call to be reversed
            request: Technical reversal request object
        """
        return technical_reversal_call(client, acquirer_id, merchant_id, original_operation_id, request)
    
    @staticmethod
    def build_request(row, **kwargs):
        """Build technical reversal request"""
        return build_technical_reversal_request(row)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, **kwargs):
        """Build technical reversal request - no DCC support"""
        return build_technical_reversal_request(row)
    
    @staticmethod
    def supports_dcc() -> bool:
        """Technical reversal does not support DCC"""
        return False
    
    @staticmethod
    def get_dependencies() -> list:
        """Technical reversal requires operation_id from previous operations"""
        return ['operation_id']  # The operationId to be reversed (from previous call)