"""Balance Inquiry endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import balance_inquiry_call
from ..request_builders.balance_inquiry import build_balance_inquiry_request

@register_endpoint('process_balance_inquiry')
class BalanceInquiryEndpoint(EndpointInterface):
    """Balance inquiry endpoint for zero-amount available balance checks"""
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, request):
        """Execute balance inquiry API call"""
        return balance_inquiry_call(client, acquirer_id, merchant_id, request)
    
    @staticmethod
    def build_request(row, cards_df, **kwargs):
        """Build balance inquiry request without DCC"""
        return build_balance_inquiry_request(row, cards_df)
    
    @staticmethod
    def build_request_with_dcc(row, cards_df, dcc_context=None, **kwargs):
        """Build balance inquiry request with DCC support"""
        # Extract additional parameters for full feature support
        address = kwargs.get('address')
        networktokens = kwargs.get('networktokens') 
        threeds = kwargs.get('threeds')
        cardonfile = kwargs.get('cardonfile')
        previous_outputs = kwargs.get('previous_outputs')
        
        return build_balance_inquiry_request(
            row, cards_df, address, networktokens, threeds, 
            cardonfile, previous_outputs, dcc_context
        )
    
    @staticmethod
    def supports_dcc() -> bool:
        """Balance inquiry supports DCC"""
        return True
    
    @staticmethod
    def get_dependencies() -> list:
        """Balance inquiry requires no dependencies"""
        return []  # Standalone operation like create_payment and account_verification