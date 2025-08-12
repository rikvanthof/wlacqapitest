"""Network Token data handling with comprehensive logging"""

import pandas as pd
import logging
from worldline.acquiring.sdk.v1.domain.network_token_data import NetworkTokenData
#from worldline.acquiring.sdk.v1.domain.card_payment_data import CardPaymentData

logger = logging.getLogger(__name__)

def apply_network_token_data(request, row, networktokens):
    """Apply Network Token data to the request if specified in the row"""
    
    if not pd.notna(row.get('network_token_data')):
        logger.debug("No Network Token data specified in test row")
        return
    
    network_token_id = row['network_token_data']
    logger.debug(f"Applying Network Token data: {network_token_id}")
    
    if network_token_id not in networktokens.index:
        logger.error(f"Network Token ID {network_token_id} not found in configuration")
        raise ValueError(f"Network Token ID {network_token_id} not found in networktoken.csv")
    
    token_row = networktokens.loc[network_token_id]
    logger.debug(f"Found network token config: wallet_id={token_row['wallet_id']}")
    
    # Create NetworkTokenData object
    network_token_data = NetworkTokenData()
    
    # Set network token data properties (cryptogram and eci)
    if pd.notna(token_row['network_token_cryptogram']):
        network_token_data.cryptogram = str(token_row['network_token_cryptogram'])
        logger.debug(f"Set cryptogram: {str(token_row['network_token_cryptogram'])[:20]}...")
    
    if pd.notna(token_row['network_token_eci']):
        network_token_data.eci = str(token_row['network_token_eci'])
        logger.debug(f"Set eci: {token_row['network_token_eci']}")
    
    # Set the network token data and wallet_id on card_payment_data
    if hasattr(request, 'card_payment_data') and request.card_payment_data is not None:
        # Set the network token data object
        request.card_payment_data.network_token_data = network_token_data
        
        # Set the wallet_id directly on card_payment_data
        if pd.notna(token_row['wallet_id']):
            request.card_payment_data.wallet_id = str(token_row['wallet_id'])
            logger.debug(f"Set wallet_id on card_payment_data: {token_row['wallet_id']}")
        
        logger.info(f"Network token applied: {network_token_id}, wallet_id={token_row['wallet_id']}")
        
        # DEBUG: Verify it was actually assigned
        logger.debug(f"NetworkTokenData object: cryptogram={getattr(network_token_data, 'cryptogram', 'NOT_SET')[:20] if hasattr(network_token_data, 'cryptogram') else 'NOT_SET'}..., eci={getattr(network_token_data, 'eci', 'NOT_SET')}")
        logger.debug(f"CardPaymentData wallet_id: {getattr(request.card_payment_data, 'wallet_id', 'NOT_SET')}")
            
    else:
        logger.error("Cannot apply network token data: card_payment_data not found on request")
        raise ValueError("Cannot apply network token data: card_payment_data not found on request")