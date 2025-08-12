"""AVS (Address Verification Service) data handling with comprehensive logging"""

import pandas as pd
import logging
from worldline.acquiring.sdk.v1.domain.address_verification_data import AddressVerificationData

logger = logging.getLogger(__name__)

def apply_avs_data(request, row, address):
    """Apply AVS data to the request if specified in the row"""
    
    if not pd.notna(row.get('address_data')):
        logger.debug("No AVS data specified in test row")
        return
    
    address_id = row['address_data']
    logger.debug(f"Applying AVS data: {address_id}")
    
    if address_id not in address.index:
        logger.error(f"Address ID {address_id} not found in configuration")
        raise ValueError(f"Address ID {address_id} not found in address.csv")
    
    address_row = address.loc[address_id]
    logger.debug(f"Found address config: {dict(address_row)}")
    
    # Create AddressVerificationData object
    avs_data = AddressVerificationData()
    
    if pd.notna(address_row['cardholder_address']):
        avs_data.cardholder_address = str(address_row['cardholder_address'])
        logger.debug(f"Set cardholder_address: {str(address_row['cardholder_address'])}")
    
    if pd.notna(address_row['cardholder_postal_code']):
        avs_data.cardholder_postal_code = str(address_row['cardholder_postal_code'])
        logger.debug(f"Set cardholder_postal_code: {str(address_row['cardholder_postal_code'])}")
    
     # FIXED: Ensure eCommerceData exists on the CardPaymentData (not the request)
    if not hasattr(request.card_payment_data, 'ecommerce_data') or request.card_payment_data.ecommerce_data is None:
        from worldline.acquiring.sdk.v1.domain.e_commerce_data import ECommerceData
        request.card_payment_data.ecommerce_data = ECommerceData()
        logger.debug("Created new ECommerceData object on CardPaymentData")
    
    # FIXED: Set the 3D Secure data on CardPaymentData
    request.card_payment_data.ecommerce_data.address_verification_data = avs_data
    logger.info(f"AVS data applied: {address_id}")