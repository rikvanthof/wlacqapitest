"""Build requests for reverse authorization API calls"""
from worldline.acquiring.sdk.v1.domain.api_payment_reversal_request import ApiPaymentReversalRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData
from worldline.acquiring.sdk.v1.domain.dcc_data import DccData
from ..utils import clean_request, generate_random_string
import pandas as pd
import datetime

def build_reverse_authorization_request(row, dcc_context=None):
    """Build reverse authorization request
    
    Args:
        row: Test data row with reversal information
        dcc_context: DCC context for currency conversion (optional)
    
    Returns:
        ApiPaymentReversalRequest: Complete request object
    """
    request = ApiPaymentReversalRequest()
    
    # Set required fields
    request.operation_id = row['test_id'] + ':' + generate_random_string(32)
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()
    
    # ✅ ENHANCED: Set reversal amount if specified (consistent with other builders)
    if pd.notna(row.get('amount')) and row.get('amount') != '' and float(row['amount']) > 0:
        # Use DCC resulting amount for main transaction amount if available
        if dcc_context and dcc_context.resulting_amount:
            amount_data = AmountData()
            amount_data.amount = dcc_context.resulting_amount['amount']
            amount_data.currency_code = dcc_context.resulting_amount['currency_code']
            amount_data.number_of_decimals = dcc_context.resulting_amount['number_of_decimals']
            request.reversal_amount = amount_data
        else:
            # Use test amount (merchant currency)
            amount_data = AmountData()
            amount_data.amount = int(float(row['amount']))  # ✅ Added float() conversion
            amount_data.currency_code = row['currency']
            amount_data.number_of_decimals = 2
            request.reversal_amount = amount_data
    
    # Add DCC fields if available
    if dcc_context and dcc_context.rate_reference_id:
        dcc_data = DccData()
        # ✅ ENHANCED: Better amount handling for DCC
        if pd.notna(row.get('amount')) and row.get('amount') != '':
            dcc_data.amount = int(float(row['amount']))
            dcc_data.currency_code = row['currency']
            dcc_data.number_of_decimals = 2
            dcc_data.conversion_rate = dcc_context.inverted_exchange_rate
            request.dynamic_currency_conversion = dcc_data
    
    return clean_request(request)