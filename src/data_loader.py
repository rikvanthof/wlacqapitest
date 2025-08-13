"""Data loading functionality with comprehensive logging - Enhanced with new config structure"""
from .config.config_manager import ConfigurationManager
from .logging_config import get_data_loader_logger

def load_data(tests_file='smoke_tests.csv'):
    """Enhanced data loading with new configuration structure"""
    logger = get_data_loader_logger()
    logger.info("🔄 Using enhanced configuration loading")
    
    # Use new ConfigurationManager
    config_manager = ConfigurationManager()
    config_set = config_manager.load_all_configs(tests_file)
    
    # Console output for backward compatibility
    print(f"📁 Loaded tests from: {tests_file}")
    print(f"📊 Test chains: {config_set.tests['chain_id'].nunique()}")
    print(f"📋 Total test steps: {len(config_set.tests)}")
    print(f"🏦 Environments: {len(config_set.environments)}")
    print(f"💳 Cards: {len(config_set.cards)}")
    print(f"🏪 Merchants: {len(config_set.merchants)}")
    print(f"📍 Addresses: {len(config_set.address)}")
    print(f"🔐 Network Tokens: {len(config_set.networktokens)}")
    print(f"🔒 3D Secure: {len(config_set.threeds)}")
    print(f"🔄 Card-on-file: {len(config_set.cardonfile)}")
    
    # Return in original format for backward compatibility
    return (
        config_set.environments,
        config_set.cards, 
        config_set.merchants,
        config_set.address,
        config_set.networktokens,
        config_set.threeds,
        config_set.cardonfile,
        config_set.tests
    )