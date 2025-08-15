"""Build requests for balance inquiry API calls"""
import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_balance_inquiry_request import ApiBalanceInquiryRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData
from worldline.acquiring.sdk.v1.domain.card_payment_data import CardPaymentData
from worldline.acquiring.sdk.v1.domain.plain_card_data import PlainCardData
from worldline.acquiring.sdk.v1.domain.payment_references import PaymentReferences
from worldline.acquiring.sdk.v1.domain.dcc_data import DccData
from ..utils import generate_random_string, clean_request
from ..avs import apply_avs_data
from ..network_token import apply_network_token_data
from ..threed_secure import apply_threed_secure_data
from ..cardonfile import apply_cardonfile_data
from ..merchant_data import apply_merchant_data
from ..core.dcc_manager import DCCContext

def apply_dcc_data_to_balance_inquiry(request, dcc_context, row):
    """Apply DCC (Dynamic Currency Conversion) data to balance inquiry request"""
    if not dcc_context or not dcc_context.rate_reference_id:
        return request
    
    # Create dynamic currency conversion data object
    dcc_data = DccData()
    
    # For balance inquiry, we use zero amount in merchant currency
    dcc_data.amount = 0  # Always zero for balance inquiry
    dcc_data.currency_code = row['currency']     # Original merchant currency
    dcc_data.number_of_decimals = 2
    dcc_data.conversion_rate = dcc_context.inverted_exchange_rate
    
    # Apply to request root level
    request.dynamic_currency_conversion = dcc_data
    
    return request

def build_balance_inquiry_request(row, cards, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None, dcc_context=None):
    """Build ApiBalanceInquiryRequest for balance inquiry calls with full feature support including DCC"""
    card_row = cards.loc[row['card_id']]
    request = ApiBalanceInquiryRequest()

    # Add Merchant data if specified
    if pd.notna(row.get('merchant_data')) and merchantdata is not None:
        apply_merchant_data(request, row, merchantdata)
    
    # Build card data (same as create_payment/account_verification)
    card_data = PlainCardData()
    card_data.card_number = str(card_row['card_number'])
    card_data.expiry_date = str(card_row['expiry_date'])
    if 'card_security_code' in card_row and pd.notna(card_row['card_security_code']):
        card_data.card_security_code = str(card_row['card_security_code'])
    if 'card_sequence_number' in card_row and pd.notna(card_row['card_sequence_number']):
        card_data.card_sequence_number = str(card_row['card_sequence_number'])
    
    # Build card payment data
    card_payment_data = CardPaymentData()
    card_payment_data.card_data = card_data
    card_payment_data.brand = card_row['card_brand']
    
    # Set optional card payment fields
    if pd.notna(row.get('card_entry_mode')):
        card_payment_data.card_entry_mode = row['card_entry_mode']
    else:
        card_payment_data.card_entry_mode = 'ECOMMERCE'  # Default for balance inquiry
        
    if pd.notna(row.get('cardholder_verification_method')):
        card_payment_data.cardholder_verification_method = row['cardholder_verification_method']
    else:
        card_payment_data.cardholder_verification_method = 'CARD_SECURITY_CODE'  # Default
    
    if pd.notna(row.get('brand_selector')):
        card_payment_data.brand_selector = row['brand_selector']
    
    # Set card payment data on request first (needed for advanced features)
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
    
    # Add DCC data if available
    if dcc_context and dcc_context.inverted_exchange_rate:
        apply_dcc_data_to_balance_inquiry(request, dcc_context, row)
    
    # Create References object
    references = PaymentReferences()
    
    # Set other request fields
    if pd.notna(row.get('dynamic_descriptor')):
        references.dynamic_descriptor = row['dynamic_descriptor']
    
    # Set amount - always zero for balance inquiry, but use DCC resulting currency if available
    if dcc_context and dcc_context.resulting_amount:
        # Use DCC resulting currency but zero amount
        amount_data = AmountData()
        amount_data.amount = 0  # Always zero for balance inquiry
        amount_data.currency_code = dcc_context.resulting_amount['currency_code']
        amount_data.number_of_decimals = dcc_context.resulting_amount['number_of_decimals']
        request.amount = amount_data
    else:
        # Use merchant currency with zero amount
        amount_data = AmountData()
        amount_data.amount = 0  # Always zero for balance inquiry
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