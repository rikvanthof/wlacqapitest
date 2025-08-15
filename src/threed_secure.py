"""3D Secure data handling with comprehensive logging"""

import pandas as pd
import uuid
import logging
from worldline.acquiring.sdk.v1.domain.three_d_secure import ThreeDSecure

logger = logging.getLogger(__name__)

def apply_threed_secure_data(request, row, threeds):
    """Apply 3D Secure data and/or SCA exemptions to the request if specified in the row"""
    
    if not pd.notna(row.get('threed_secure_data')):
        logger.debug("No 3D Secure data specified in test row")
        return
    
    threed_secure_id = row['threed_secure_data']
    logger.debug(f"Applying 3D Secure/eCommerce data: {threed_secure_id}")
    
    if threed_secure_id not in threeds.index:
        logger.error(f"3D Secure ID {threed_secure_id} not found in configuration")
        raise ValueError(f"3D Secure ID {threed_secure_id} not found in threeddata.csv")
    
    threed_row = threeds.loc[threed_secure_id]
    logger.debug(f"Found config: type={threed_row.get('three_d_secure_type')}, version={threed_row.get('version')}, exemption={threed_row.get('sca_exemption_requested')}")
    
    # ✅ ALWAYS ensure eCommerceData exists (needed for both 3DS and exemptions)
    if not hasattr(request.card_payment_data, 'ecommerce_data') or request.card_payment_data.ecommerce_data is None:
        from worldline.acquiring.sdk.v1.domain.e_commerce_data import ECommerceData
        request.card_payment_data.ecommerce_data = ECommerceData()
        logger.debug("Created new ECommerceData object on CardPaymentData")
    
    # ✅ Handle 3D Secure data (if present)
    has_3ds_data = (pd.notna(threed_row.get('authentication_value')) or 
                   pd.notna(threed_row.get('eci')) or 
                   pd.notna(threed_row.get('three_d_secure_type')))
    
    if has_3ds_data:
        # Create ThreeDSecure object
        threed_secure = ThreeDSecure()
        
        # Map CSV fields to SDK properties
        if pd.notna(threed_row['authentication_value']):
            threed_secure.authentication_value = str(threed_row['authentication_value'])
            logger.debug(f"Set authentication_value: {str(threed_row['authentication_value'])[:20]}...")
        
        if pd.notna(threed_row['eci']):
            threed_secure.eci = str(threed_row['eci'])
            logger.debug(f"Set eci: {threed_row['eci']}")
        
        if pd.notna(threed_row['three_d_secure_type']):
            threed_secure.three_d_secure_type = str(threed_row['three_d_secure_type'])
            logger.debug(f"Set three_d_secure_type: {threed_row['three_d_secure_type']}")
        
        if pd.notna(threed_row['version']):
            threed_secure.version = str(threed_row['version'])
            logger.debug(f"Set version: {threed_row['version']}")
        
        # Generate UUID for directoryServerTransactionId
        directory_server_transaction_id = str(uuid.uuid4())
        threed_secure.directory_server_transaction_id = directory_server_transaction_id
        logger.debug(f"Generated directory_server_transaction_id: {directory_server_transaction_id}")
        
        # Set the 3D Secure data on eCommerceData
        request.card_payment_data.ecommerce_data.three_d_secure = threed_secure
        logger.info(f"3D Secure data applied: {threed_secure_id}, type={threed_row['three_d_secure_type']}, eci={threed_row['eci']}")
    
    # ✅ Handle SCA Exemption (if present)
    if pd.notna(threed_row.get('sca_exemption_requested')):
        exemption_value = str(threed_row['sca_exemption_requested'])
        request.card_payment_data.ecommerce_data.sca_exemption_request = exemption_value
        logger.info(f"SCA exemption applied: {threed_secure_id}, exemption={exemption_value}")
    
    # ✅ Log what we accomplished
    if has_3ds_data and pd.notna(threed_row.get('sca_exemption_requested')):
        logger.info(f"Applied both 3DS and SCA exemption for: {threed_secure_id}")
    elif has_3ds_data:
        logger.info(f"Applied 3DS only for: {threed_secure_id}")
    elif pd.notna(threed_row.get('sca_exemption_requested')):
        logger.info(f"Applied SCA exemption only for: {threed_secure_id}")
    else:
        logger.warning(f"No 3DS or exemption data found for: {threed_secure_id}")