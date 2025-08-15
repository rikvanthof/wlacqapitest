"""Build requests for reverse refund authorization API calls"""
import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_refund_reversal_request import ApiRefundReversalRequest
from ..utils import generate_random_string, clean_request

def build_reverse_refund_authorization_request(row):
    """Build ApiRefundReversalRequest for reverse refund authorization calls"""
    request = ApiRefundReversalRequest()
    
    # Set required fields - very simple!
    request.operation_id = row['test_id'] + ':' + generate_random_string(32)
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()
    
    # That's it! No amount, no DCC, no card data - just operation ID and timestamp
    
    return clean_request(request)