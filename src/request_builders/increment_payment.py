"""Build requests for increment_payment API calls"""

import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_increment_request import ApiIncrementRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData
from ..utils import generate_random_string, clean_request

def build_increment_payment_request(row):
    """Build ApiIncrementRequest for increment_payment calls"""
    request = ApiIncrementRequest()
    
    # Set required fields
    request.operation_id = row['test_id'] + '-' + generate_random_string(40-(len(row['test_id'])+1))
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()
    
    # Set amount - increment should always have an amount
    if pd.notna(row.get('amount')) and row.get('amount') != '':
        amount_data = AmountData()
        amount_data.amount = int(float(row['amount']))  # Handle both int and float
        amount_data.currency_code = row['currency']
        amount_data.number_of_decimals = 2
        request.increment_amount = amount_data
    else:
        raise ValueError(f"increment_payment requires amount, but none provided for {row.get('test_id')}")
    
    
    return clean_request(request)