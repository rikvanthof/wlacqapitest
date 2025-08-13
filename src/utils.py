"""Utility functions with comprehensive logging"""

import uuid
import random
import string
import tempfile
import configparser
import pandas as pd
import logging
from .logging_config import get_main_logger
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

def generate_nonce():
    """Generate a random 6-digit nonce"""
    logger.debug("Generating random nonce")
    nonce = random.randint(100000, 999999)
    logger.debug(f"Generated nonce: {nonce}")
    return nonce

def generate_random_string(length: int) -> str:
    """
    Generate a random string of specified length containing a-z, A-Z, and 0-9.
    
    :param length: The desired length of the random string (must be positive integer).
    :return: A random string of the given length.
    :raises ValueError: If length is not a positive integer.
    """
    logger.debug(f"Generating random string of length: {length}")
    
    if not isinstance(length, int) or length <= 0:
        logger.error(f"Invalid length parameter: {length} (must be positive integer)")
        raise ValueError("Length must be a positive integer.")
    
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    result = ''.join(random.choices(characters, k=length))
    
    # Log first few characters only for security
    preview = result[:min(10, length)] + "..." if length > 10 else result
    logger.debug(f"Generated random string: {preview} (length: {len(result)})")
    
    return result

def generate_uuid():
    """Generate a UUID4 string"""
    logger.debug("Generating UUID")
    uuid_str = str(uuid.uuid4())
    logger.debug(f"Generated UUID: {uuid_str}")
    return uuid_str

def create_temp_config(env_data):
    """Create temporary configuration file for SDK from environment data"""
    logger.info("Creating temporary SDK configuration file")
    logger.debug(f"Environment data keys: {list(env_data.keys()) if hasattr(env_data, 'keys') else 'N/A'}")
    
    try:
        config = configparser.ConfigParser()
        
        # Map CSV columns to SDK expected keys
        sdk_keys = {
            'integrator': 'acquiring.api.integrator',
            'endpoint_host': 'acquiring.api.endpoint.host',
            'authorization_type': 'acquiring.api.authorizationType',
            'oauth2_token_uri': 'acquiring.api.oauth2.tokenUri',
            'connect_timeout': 'acquiring.api.connectTimeout',
            'socket_timeout': 'acquiring.api.socketTimeout',
            'max_connections': 'acquiring.api.maxConnections'
        }
        
        config['AcquiringSDK'] = {}
        config_values_set = []
        
        for csv_key, sdk_key in sdk_keys.items():
            if csv_key in env_data and pd.notna(env_data[csv_key]):
                config_value = str(env_data[csv_key])
                config['AcquiringSDK'][sdk_key] = config_value
                config_values_set.append(f"{sdk_key}={config_value}")
                logger.debug(f"Set config: {sdk_key} = {config_value}")
            else:
                logger.debug(f"Skipping missing/null config: {csv_key}")
        
        logger.info(f"Configuration mapping complete: {len(config_values_set)} values set")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_config:
            config.write(temp_config)
            temp_file_path = temp_config.name
        
        logger.info(f"Temporary config file created: {temp_file_path}")
        logger.debug(f"Config file contains: {config_values_set}")
        
        return temp_file_path
        
    except Exception as e:
        logger.error(f"Failed to create temporary config file: {e}")
        raise

def get_db_engine():
    """Create database engine for results storage"""
    import os
    
    logger = get_main_logger()
    
    # Create outputs directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    
    # Use SQLite for local storage
    db_path = 'outputs/local.db'
    engine = create_engine(f'sqlite:///{db_path}')
    
    logger.info(f"Database engine created: sqlite:///{db_path}")
    return engine

def clean_request(request):
    """Clean request object by removing None values and empty dictionaries"""
    logger.debug(f"Cleaning request object of type: {type(request).__name__}")
    
    if request is None:
        logger.debug("Request is None, returning None")
        return request
    
    original_attrs = len(request.__dict__.keys()) if hasattr(request, '__dict__') else 0
    removed_attrs = []
    
    try:
        for key in list(request.__dict__.keys()):
            value = request.__dict__[key]
            
            if value is None:
                delattr(request, key)
                removed_attrs.append(f"{key}=None")
                logger.debug(f"Removed None attribute: {key}")
                
            elif isinstance(value, dict):
                if all(v is None for v in value.values()):
                    delattr(request, key)
                    removed_attrs.append(f"{key}=empty_dict")
                    logger.debug(f"Removed empty dict attribute: {key}")
        
        final_attrs = len(request.__dict__.keys()) if hasattr(request, '__dict__') else 0
        
        logger.info(f"Request cleaning complete: {original_attrs} -> {final_attrs} attributes")
        if removed_attrs:
            logger.debug(f"Removed attributes: {removed_attrs}")
        else:
            logger.debug("No attributes removed")
        
        return request
        
    except Exception as e:
        logger.error(f"Error cleaning request object: {e}")
        # Return original request if cleaning fails
        return request