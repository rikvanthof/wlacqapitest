"""Build requests for technical reversal API calls"""
import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_technical_reversal_request import ApiTechnicalReversalRequest
from ..utils import generate_random_string, clean_request

def build_technical_reversal_request(row):
    """Build ApiTechnicalReversalRequest for technical reversal calls
    
    Technical reversals are used when the original transaction response was not received
    due to timeout, network issues, etc. They allow "blind reversal" of operations.
    
    The original operation_id is passed as path parameter, not in request body.
    Request body is minimal - just new operation_id, timestamp, and optional reason.
    
    Args:
        row: Test data row with reversal information
        
    Returns:
        ApiTechnicalReversalRequest: Complete request object
    """
    request = ApiTechnicalReversalRequest()
    
    # Set required fields - very minimal!
    request.operation_id = row['test_id'] + ':' + generate_random_string(32)
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()
    
    # Set reason for technical reversal (optional but recommended)
    if 'reversal_reason' in row and pd.notna(row['reversal_reason']):
        request.reason = row['reversal_reason']
    else:
        request.reason = 'TIMEOUT'  # Default reason for technical reversals
    
    # NO references - technical reversals don't support them!
    # NO dynamic descriptors - technical reversals don't support them!
    # The operationId to reverse comes from previous call and goes in URL path
    
    return clean_request(request)