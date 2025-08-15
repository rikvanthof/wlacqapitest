"""Build requests for standalone refund API calls"""
import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_refund_request import ApiRefundRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData
from worldline.acquiring.sdk.v1.domain.card_payment_data_for_refund import CardPaymentDataForRefund
from worldline.acquiring.sdk.v1.domain.plain_card_data import PlainCardData
from worldline.acquiring.sdk.v1.domain.payment_references import PaymentReferences
from worldline.acquiring.sdk.v1.domain.dcc_data import DccData
from ..utils import generate_random_string, clean_request
from ..network_token import apply_network_token_data

def apply_dcc_data_to_standalone_refund(request, dcc_context, row):
    """Apply DCC data to standalone refund request"""
    if not dcc_context or not dcc_context.rate_reference_id:
        return request
    
    dcc_data = DccData()
    dcc_data.amount = int(row['amount'])         # Original merchant amount
    dcc_data.currency_code = row['currency']     # Original merchant currency
    dcc_data.number_of_decimals = 2
    dcc_data.conversion_rate = dcc_context.inverted_exchange_rate
    
    request.dynamic_currency_conversion = dcc_data
    return request

def build_standalone_refund_request(row, cards_df, dcc_context=None):
    """Build ApiRefundRequest for standalone refund calls with DCC support"""
    card_row = cards_df.loc[row['card_id']]
    request = ApiRefundRequest()
    
    # Build card data
    card_data = PlainCardData()
    card_data.card_number = str(card_row['card_number'])
    card_data.expiry_date = str(card_row['expiry_date'])
    
    # ✅ Safe handling of optional card fields
    if 'card_security_code' in card_row and pd.notna(card_row['card_security_code']):
        card_data.card_security_code = str(card_row['card_security_code'])
    
    if 'card_sequence_number' in card_row and pd.notna(card_row['card_sequence_number']):
        card_data.card_sequence_number = str(card_row['card_sequence_number'])
    
    # Build card payment data for refund
    card_payment_data = CardPaymentDataForRefund()
    card_payment_data.card_data = card_data
    card_payment_data.brand = card_row['card_brand']
    
    # Set required refund fields
    if pd.notna(row.get('capture_immediately')):
        card_payment_data.capture_immediately = str(row['capture_immediately']).upper() == 'TRUE'
    else:
        card_payment_data.capture_immediately = True  # Default for standalone refunds
        
    if pd.notna(row.get('card_entry_mode')):
        card_payment_data.card_entry_mode = row['card_entry_mode']
    else:
        card_payment_data.card_entry_mode = 'ECOMMERCE'  # Default
        
    if pd.notna(row.get('cardholder_verification_method')):
        card_payment_data.cardholder_verification_method = row['cardholder_verification_method']
    else:
        card_payment_data.cardholder_verification_method = 'CARD_SECURITY_CODE'  # Default
    
    request.card_payment_data = card_payment_data
    
    # Add Network Token data if specified (only relevant advanced feature for standalone refunds)
    if pd.notna(row.get('network_token_data')):
        try:
            apply_network_token_data(request, row, None)  # Pass None for networktokens if not available
        except (ImportError, Exception):
            pass  # Skip if function doesn't exist or fails
    
    # Create References object
    references = PaymentReferences()
    if pd.notna(row.get('merchant_reference')):
        references.merchant_reference = row['merchant_reference']
    else:
        references.merchant_reference = row['test_id'] + ':' + generate_random_string(32)
    
    if pd.notna(row.get('dynamic_descriptor')):
        references.dynamic_descriptor = row['dynamic_descriptor']
    
    request.references = references
    
    # Set required fields
    request.operation_id = row['test_id'] + ':' + generate_random_string(32)
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()
    
    # Set amount - required for standalone refunds
    if dcc_context and dcc_context.resulting_amount:
        # Use DCC resulting amount (customer currency amount)
        amount_data = AmountData()
        amount_data.amount = dcc_context.resulting_amount['amount']
        amount_data.currency_code = dcc_context.resulting_amount['currency_code']
        amount_data.number_of_decimals = dcc_context.resulting_amount['number_of_decimals']
        request.amount = amount_data
    else:
        # Use test amount (merchant currency)
        amount_data = AmountData()
        amount_data.amount = int(row['amount'])
        amount_data.currency_code = row['currency']
        amount_data.number_of_decimals = 2
        request.amount = amount_data
    
    # Add DCC data if available
    if dcc_context and dcc_context.rate_reference_id:
        apply_dcc_data_to_standalone_refund(request, dcc_context, row)
    
    return clean_request(request)