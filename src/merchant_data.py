"""Merchant data handling for API requests"""

import pandas as pd
import logging
from worldline.acquiring.sdk.v1.domain.merchant_data import MerchantData

logger = logging.getLogger(__name__)

def apply_merchant_data(request, row, merchantdata):
    """Apply merchant data to the request if specified in the row"""
    
    if not pd.notna(row.get('merchant_data')):
        logger.debug("No merchant data specified in test row")
        return
    
    merchant_id = row['merchant_data']
    logger.debug(f"Applying merchant data: {merchant_id}")
    
    if merchant_id not in merchantdata.index:
        logger.error(f"Merchant ID {merchant_id} not found in configuration")
        raise ValueError(f"Merchant ID {merchant_id} not found in merchantdata.csv")
    
    merchant_row = merchantdata.loc[merchant_id]
    logger.debug(f"Found merchant config: name={merchant_row['name']}, mcc={merchant_row['merchant_category_code']}")
    
    # Create MerchantData object
    merchant_data = MerchantData()
    
    # Set required fields
    if pd.notna(merchant_row['merchant_category_code']):
        merchant_data.merchant_category_code = int(merchant_row['merchant_category_code'])
        logger.debug(f"Set merchant_category_code: {merchant_row['merchant_category_code']}")
    
    if pd.notna(merchant_row['name']):
        merchant_data.name = str(merchant_row['name'])
        logger.debug(f"Set name: {merchant_row['name']}")
    
    # Set optional fields
    if pd.notna(merchant_row['address']):
        merchant_data.address = str(merchant_row['address'])
        logger.debug(f"Set address: {merchant_row['address']}")
    
    if pd.notna(merchant_row['postal_code']):
        merchant_data.postal_code = str(merchant_row['postal_code'])
        logger.debug(f"Set postal_code: {merchant_row['postal_code']}")
    
    if pd.notna(merchant_row['city']):
        merchant_data.city = str(merchant_row['city'])
        logger.debug(f"Set city: {merchant_row['city']}")
    
    if pd.notna(merchant_row['state_code']):
        merchant_data.state_code = str(merchant_row['state_code'])
        logger.debug(f"Set state_code: {merchant_row['state_code']}")
    
    if pd.notna(merchant_row['country_code']):
        merchant_data.country_code = str(merchant_row['country_code'])
        logger.debug(f"Set country_code: {merchant_row['country_code']}")
    
    # Apply to request
    request.merchant_data = merchant_data
    
    logger.info(f"Merchant data applied: {merchant_id}, name={merchant_row['name']}, mcc={merchant_row['merchant_category_code']}")