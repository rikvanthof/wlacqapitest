"""Build requests for create_payment API calls"""
import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_payment_request import ApiPaymentRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData
from worldline.acquiring.sdk.v1.domain.card_payment_data import CardPaymentData
from worldline.acquiring.sdk.v1.domain.plain_card_data import PlainCardData
from worldline.acquiring.sdk.v1.domain.payment_references import PaymentReferences
from worldline.acquiring.sdk.v1.domain.dcc_data import DccData  # ✅ NEW IMPORT

from ..utils import generate_random_string, clean_request
from ..avs import apply_avs_data
from ..network_token import apply_network_token_data
from ..threed_secure import apply_threed_secure_data
from ..cardonfile import apply_cardonfile_data
from ..core.dcc_manager import DCCContext
from ..merchant_data import apply_merchant_data  

def apply_dcc_data(request, dcc_context, row):
    """Apply DCC (Dynamic Currency Conversion) data to payment request"""
    if not dcc_context or not dcc_context.rate_reference_id:
        return request
    
    # Create dynamic currency conversion data object
    dcc_data = DccData()
    
    # ✅ Use correct DccData field names from SDK
    dcc_data.amount = int(row['amount'])         # Original merchant amount
    dcc_data.currency_code = row['currency']     # Original merchant currency
    dcc_data.number_of_decimals = 2
    dcc_data.conversion_rate = dcc_context.inverted_exchange_rate
    
    # ✅ Apply to request root level (not cardPaymentData)
    request.dynamic_currency_conversion = dcc_data
    
    return request

def build_create_payment_request(row, cards, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None, dcc_context=None):
    """Build ApiPaymentRequest for create_payment calls with full feature support including DCC"""
    card_row = cards.loc[row['card_id']]
    request = ApiPaymentRequest()
    
    # Add Merchant data if specified
    if pd.notna(row.get('merchant_data')) and merchantdata is not None:
        apply_merchant_data(request, row, merchantdata)

    # Build card data
    card_data = PlainCardData()
    card_data.card_number = str(card_row['card_number'])
    card_data.expiry_date = str(card_row['expiry_date'])
    if pd.notna(card_row['card_security_code']):
        card_data.card_security_code = str(card_row['card_security_code'])
    if pd.notna(card_row['card_sequence_number']):
        card_data.card_sequence_number = str(card_row['card_sequence_number'])
    
    # Build card payment data
    card_payment_data = CardPaymentData()
    card_payment_data.card_data = card_data
    card_payment_data.brand = card_row['card_brand']
    
    # Set optional card payment fields
    if pd.notna(row.get('allow_partial_approval')):
        card_payment_data.allow_partial_approval = str(row['allow_partial_approval']).upper() == 'TRUE'
    if pd.notna(row.get('capture_immediately')):
        card_payment_data.capture_immediately = str(row['capture_immediately']).upper() == 'TRUE'
    if pd.notna(row.get('card_entry_mode')):
        card_payment_data.card_entry_mode = row['card_entry_mode']
    if pd.notna(row.get('cardholder_verification_method')):
        card_payment_data.cardholder_verification_method = row['cardholder_verification_method']
    if pd.notna(row.get('brand_selector')):
        card_payment_data.brand_selector = row['brand_selector']
    
    # Set card payment data on request first (needed for network tokens and DCC)
    request.card_payment_data = card_payment_data
    
    # Add AVS data if specified
    if pd.notna(row.get('address_data')) and address is not None:
        apply_avs_data(request, row, address)
    
    # Add Network Token data if specified  
    if pd.notna(row.get('network_token_data')) and networktokens is not None:
        apply_network_token_data(request, row, networktokens)
    
    # Add 3D Secure data if specified
    if pd.notna(row.get('threed_secure_data')) and threeds is not None:
        apply_threed_secure_data(request, row, threeds)
    
    # Add Card-on-File data if specified
    if pd.notna(row.get('card_on_file_data')) and cardonfile is not None:
        apply_cardonfile_data(request, row, cardonfile, previous_outputs)
    
    # ✅ Add DCC data if available
    if dcc_context and dcc_context.inverted_exchange_rate:
        apply_dcc_data(request, dcc_context, row)
    
    # Create References object first
    references = PaymentReferences()
    
    # Set other request fields
    if pd.notna(row.get('authorization_type')):
        request.authorization_type = row['authorization_type']
    if pd.notna(row.get('dynamic_descriptor')):
        references.dynamic_descriptor = row['dynamic_descriptor']
    
    # ✅ Set amount - use DCC resulting amount if available, otherwise test amount
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
    
    # Set operation ID and timestamp
    request.operation_id = row['test_id'] + ':' + generate_random_string(40-(len(row['test_id'])+1))
    references.merchant_reference = row['test_id'] + ':' + generate_random_string(50-(len(row['test_id'])+1))
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()
    
    # Assign references to request
    request.references = references
    
    return clean_request(request)