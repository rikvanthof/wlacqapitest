"""Get DCC Rate endpoint with empty object removal"""

from worldline.acquiring.sdk.v1.domain.get_dcc_rate_request import GetDCCRateRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData
from worldline.acquiring.sdk.v1.domain.card_data_for_dcc import CardDataForDcc
from worldline.acquiring.sdk.v1.domain.point_of_sale_data_for_dcc import PointOfSaleDataForDcc
from worldline.acquiring.sdk.v1.domain.transaction_data_for_dcc import TransactionDataForDcc
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..utils import generate_random_string, clean_request
import pandas as pd
import datetime
from typing import List

@register_endpoint('get_dcc_rate')
class GetDCCRateEndpoint(EndpointInterface):
    """Get DCC Rate endpoint for Dynamic Currency Conversion"""
    
    @staticmethod
    def call_api(client, acquirer_id: str, merchant_id: str, request: GetDCCRateRequest):
        """Execute DCC Rate API call with correct method name"""
        return client.v1().acquirer(acquirer_id).merchant(merchant_id).dynamic_currency_conversion().request_dcc_rate(request)
    
    @staticmethod
    def build_request(row, transaction_type: str = 'PAYMENT', existing_rate_reference_id: str = None, cards=None):
        """✅ FINAL FIX: Build GetDCCRateRequest without empty objects"""
        request = GetDCCRateRequest()
        
        # Set operation ID with DCC indicator
        random_suffix = generate_random_string(25)
        request.operation_id = f"{row['test_id']}:dcc:{random_suffix}"
        
        # Set target currency
        request.target_currency = row.get('dcc_target_currency', 'EUR')
        
        # Set rate reference ID if we have one from previous DCC call in chain
        if existing_rate_reference_id:
            request.rate_reference_id = existing_rate_reference_id
        
        # ✅ Create proper TransactionDataForDcc object
        transaction_data = TransactionDataForDcc()
        
        # Set transaction amount
        amount_data = AmountData()
        amount_data.amount = int(row['amount'])
        amount_data.currency_code = row['currency']
        amount_data.number_of_decimals = 2
        transaction_data.amount = amount_data
        
        # Set transaction type and timestamp
        transaction_data.transaction_type = transaction_type
        transaction_data.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()
        
        # Set the transaction object on the request
        request.transaction = transaction_data
        
        # ✅ Build card payment data with cardEntryMode
        if pd.notna(row.get('card_id')) and cards is not None:
            try:
                card_row = cards.loc[row['card_id']]
                
                # Create card data object
                card_data = CardDataForDcc()
                card_data.brand = card_row['card_brand']
                
                # Set BIN (first 6-8 digits)
                if pd.notna(card_row.get('card_bin')):
                    card_data.bin = str(card_row['card_bin'])
                elif pd.notna(card_row.get('card_number')):
                    card_data.bin = str(card_row['card_number'])[:8]
                
                # Set cardEntryMode in card data
                if pd.notna(row.get('card_entry_mode')):
                    card_data.card_entry_mode = row['card_entry_mode']
                
                # Set the card payment data
                request.card_payment_data = card_data
                
            except Exception as e:
                print(f"Warning: Could not set card data for DCC: {e}")
        
        # ✅ REMOVED: Don't create pointOfSaleData at all
        # The empty object was causing the 400 error
        
        # ✅ IMPORTANT: Apply clean_request to remove any empty objects/properties
        cleaned_request = clean_request(request)
        
        return cleaned_request
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """DCC rate inquiry has no dependencies"""
        return []
    
    @staticmethod
    def supports_chaining() -> bool:
        """DCC rate can be used in chains"""
        return True
    
    @staticmethod
    def get_output_keys() -> List[str]:
        """DCC rate inquiry provides rate reference ID"""
        return ['dcc_rate_reference_id']
    
    @staticmethod
    def supports_dcc() -> bool:
        """This endpoint is specifically for DCC"""
        return True

def build_get_dcc_rate_request(row: pd.Series, transaction_type: str, existing_rate_reference_id: str = None, cards=None) -> GetDCCRateRequest:
    """Helper function for building DCC rate request"""
    return GetDCCRateEndpoint.build_request(row, transaction_type, existing_rate_reference_id, cards)

def get_dcc_rate(client, acquirer_id: str, merchant_id: str, request: GetDCCRateRequest):
    """Helper function for DCC rate API call"""
    return GetDCCRateEndpoint.call_api(client, acquirer_id, merchant_id, request)