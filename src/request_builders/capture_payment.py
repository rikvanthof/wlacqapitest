"""Build requests for capture payment API calls"""

import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_capture_request import ApiCaptureRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData
from worldline.acquiring.sdk.v1.domain.payment_references import PaymentReferences
from worldline.acquiring.sdk.v1.domain.dcc_data import DccData
from ..utils import generate_random_string, clean_request

def apply_dcc_data_to_capture(request, dcc_context, row):
    """Apply DCC data to capture payment request"""
    if not dcc_context or not dcc_context.rate_reference_id:
        return request
    
    dcc_data = DccData()
    
    # ✅ Use correct DccData field names from SDK
    dcc_data.amount = int(float(row['amount']))  # Original merchant amount
    dcc_data.currency_code = row['currency']     # Original merchant currency
    dcc_data.number_of_decimals = 2
    dcc_data.conversion_rate = dcc_context.inverted_exchange_rate
    
    request.dynamic_currency_conversion = dcc_data
    return request

def build_capture_payment_request(row, dcc_context=None):
    """Build ApiCaptureRequest for capture payment calls with DCC support"""
    request = ApiCaptureRequest()

    # Create References object first
    references = PaymentReferences()

    if pd.notna(row.get('dynamic_descriptor')):
        references.dynamic_descriptor = row['dynamic_descriptor']

    # Set required fields
    request.operation_id = row['test_id'] + ':' + generate_random_string(40-(len(row['test_id'])+1))
    references.merchant_reference = row['test_id'] + ':' + generate_random_string(50-(len(row['test_id'])+1))
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()

    # Assign references to request
    request.references = references
    
    # Set amount
    if pd.notna(row.get('amount')) and row.get('amount') != '':
        # ✅ Use DCC resulting amount if available, otherwise test amount
        if dcc_context and dcc_context.resulting_amount:
            amount_data = AmountData()
            amount_data.amount = dcc_context.resulting_amount['amount']
            amount_data.currency_code = dcc_context.resulting_amount['currency_code']
            amount_data.number_of_decimals = dcc_context.resulting_amount['number_of_decimals']
            request.amount = amount_data
        else:
            amount_data = AmountData()
            amount_data.amount = int(float(row['amount']))
            amount_data.currency_code = row['currency']
            amount_data.number_of_decimals = 2
            request.amount = amount_data
    
    # ✅ FIXED: Add DCC data with row parameter
    if dcc_context and dcc_context.rate_reference_id:
        apply_dcc_data_to_capture(request, dcc_context, row)
    
    return clean_request(request)