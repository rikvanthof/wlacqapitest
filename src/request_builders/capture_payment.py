"""Build requests for capture payment API calls"""

import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_capture_request import ApiCaptureRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData
from worldline.acquiring.sdk.v1.domain.payment_references import PaymentReferences
from ..utils import generate_random_string, clean_request

def build_capture_payment_request(row):
    """Build ApiCaptureRequest for capture payment calls"""
    request = ApiCaptureRequest()

    # Create References object first
    references = PaymentReferences()

    if pd.notna(row.get('dynamic_descriptor')):
        references.dynamic_descriptor = row['dynamic_descriptor']

    # Set required fields
    request.operation_id = row['test_id'] + '-' + generate_random_string(40-(len(row['test_id'])+1))
    references.merchant_reference = row['test_id'] + '-' + generate_random_string(50-(len(row['test_id'])+1))
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()

    # Assign references to request
    request.references = references
    
    # Set amount
    amount_data = AmountData()
    amount_data.amount = int(row['amount'])
    amount_data.currency_code = row['currency']
    amount_data.number_of_decimals = 2
    request.amount = amount_data
    
    return clean_request(request)