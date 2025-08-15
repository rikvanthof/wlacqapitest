"""Account Verification endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import account_verification_call
from ..request_builders.account_verification import build_account_verification_request

@register_endpoint('process_account_verification')
class AccountVerificationEndpoint(EndpointInterface):
    """Account verification endpoint for zero-amount card validity checks"""
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, request):
        """Execute account verification API call"""
        return account_verification_call(client, acquirer_id, merchant_id, request)
    
    @staticmethod
    def build_request(row, cards_df, **kwargs):
        """Build account verification request without DCC"""
        return build_account_verification_request(row, cards_df)
    
    @staticmethod
    def build_request_with_dcc(row, cards_df, dcc_context=None, **kwargs):
        """Build account verification request with DCC support"""
        # Extract additional parameters for full feature support
        address = kwargs.get('address')
        networktokens = kwargs.get('networktokens') 
        threeds = kwargs.get('threeds')
        cardonfile = kwargs.get('cardonfile')
        previous_outputs = kwargs.get('previous_outputs')
        
        return build_account_verification_request(
            row, cards_df, address, networktokens, threeds, 
            cardonfile, previous_outputs, dcc_context
        )
    
    @staticmethod
    def supports_dcc() -> bool:
        """Account verification supports DCC"""
        return True
    
    @staticmethod
    def get_dependencies() -> list:
        """Account verification requires no dependencies"""
        return []  # Standalone operation like create_payment