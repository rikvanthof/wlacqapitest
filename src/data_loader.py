"""Data loading functionality with comprehensive logging"""
import pandas as pd
from .logging_config import get_data_loader_logger

def load_data(tests_file='config/tests.csv'):
    """Load configuration data with configurable tests file and comprehensive logging"""
    logger = get_data_loader_logger()
    
    logger.info(f"🚀 Starting data loading process")
    logger.debug(f"Tests file: {tests_file}")
    
    try:
        # Load environments
        logger.debug("Loading environments configuration...")
        environments = pd.read_csv('config/environments.csv').set_index('env')
        logger.info(f"🏦 Environments loaded: {len(environments)} environments")
        logger.debug(f"Available environments: {list(environments.index)}")
        
        # Load cards
        logger.debug("Loading cards configuration...")
        cards = pd.read_csv('config/cards.csv', dtype={
            'card_brand': str,
            'card_bin': str,
            'card_number': str,
            'expiry_date': str,
            'card_sequence_number': str,
            'card_security_code': str,
            'card_pin': str,
            'card_description': str
        }).set_index('card_id')
        logger.info(f"💳 Cards loaded: {len(cards)} cards")
        
        # Log card brand distribution
        if 'card_brand' in cards.columns:
            brand_counts = cards['card_brand'].value_counts()
            logger.debug(f"Card brands: {dict(brand_counts)}")
        
        # Load merchants
        logger.debug("Loading merchants configuration...")
        merchants = pd.read_csv('config/merchants.csv', dtype={
            'acquirer_id': str,
            'merchant_id': str,
            'merchant_description': str
        }).set_index(['env', 'merchant'])
        logger.info(f"🏪 Merchants loaded: {len(merchants)} merchants")
        
        # Log merchant distribution by environment
        if len(merchants) > 0:
            env_counts = merchants.reset_index()['env'].value_counts()
            logger.debug(f"Merchants per environment: {dict(env_counts)}")
        
        # Load address data
        logger.debug("Loading address configuration...")
        address = pd.read_csv('config/address.csv', dtype={
            'cardholder_postal_code': str,
            'cardholder_address': str
        }).set_index('address_id')
        logger.info(f"📍 Addresses loaded: {len(address)} addresses")
        logger.debug(f"Available address IDs: {list(address.index)}")
        
        # Load network tokens
        logger.debug("Loading network tokens configuration...")
        networktokens = pd.read_csv('config/networktoken.csv', dtype={
            'wallet_id': str,
            'network_token_cryptogram': str,
            'network_token_eci': str
        }).set_index('networktoken_id')
        logger.info(f"🔐 Network Tokens loaded: {len(networktokens)} tokens")
        logger.debug(f"Available network token IDs: {list(networktokens.index)}")
        
        # Log network token wallet distribution
        if 'wallet_id' in networktokens.columns:
            wallet_counts = networktokens['wallet_id'].value_counts()
            logger.debug(f"Network tokens per wallet: {dict(wallet_counts)}")

        # Load 3D Secure data
        logger.debug("Loading 3D Secure configuration...")
        threeds = pd.read_csv('config/threeddata.csv', dtype={
            'three_d_secure_type': str,
            'authentication_value': str,
            'eci': str,
            'version': str
        }).set_index('three_d_id')
        logger.info(f"🔒 3D Secure data loaded: {len(threeds)} configurations")
        logger.debug(f"Available 3D Secure IDs: {list(threeds.index)}")
        
        # Log 3D Secure type distribution
        if 'three_d_secure_type' in threeds.columns:
            type_counts = threeds['three_d_secure_type'].value_counts()
            logger.debug(f"3D Secure types: {dict(type_counts)}")

        # Load and process tests
        logger.debug(f"Loading tests from: {tests_file}")
        tests = pd.read_csv(tests_file).sort_values(['chain_id', 'step_order'])
        logger.info(f"📋 Tests loaded: {len(tests)} test steps")
        
        # Analyze test data
        chain_count = tests['chain_id'].nunique()
        logger.info(f"📊 Test chains: {chain_count}")
        
        # Log test chain details
        chain_analysis = tests.groupby('chain_id').agg({
            'step_order': 'count',
            'call_type': lambda x: list(x.unique())
        }).rename(columns={'step_order': 'step_count'})
        
        for chain_id, row in chain_analysis.iterrows():
            logger.debug(f"Chain {chain_id}: {row['step_count']} steps, types: {row['call_type']}")
        
        # Log call type distribution
        call_type_counts = tests['call_type'].value_counts()
        logger.debug(f"Call type distribution: {dict(call_type_counts)}")
        
        # Validate data relationships
        logger.debug("Validating data relationships...")
        
        # Check for missing card references
        if 'card_id' in tests.columns:
            test_card_ids = set(tests['card_id'].dropna().unique())
            available_card_ids = set(cards.index)
            missing_cards = test_card_ids - available_card_ids
            if missing_cards:
                logger.warning(f"Tests reference missing cards: {missing_cards}")
            else:
                logger.debug("All test card references are valid")
        
        # Check for missing environment references
        if 'env' in tests.columns:
            test_envs = set(tests['env'].dropna().unique())
            available_envs = set(environments.index)
            missing_envs = test_envs - available_envs
            if missing_envs:
                logger.warning(f"Tests reference missing environments: {missing_envs}")
            else:
                logger.debug("All test environment references are valid")
        
        # Check for missing merchant references
        if 'merchant_id' in tests.columns and 'env' in tests.columns:
            test_merchants = set()
            for _, row in tests.iterrows():
                if pd.notna(row.get('merchant_id')) and pd.notna(row.get('env')):
                    test_merchants.add((row['env'], row['merchant_id']))
            
            available_merchants = set(merchants.index)
            missing_merchants = test_merchants - available_merchants
            if missing_merchants:
                logger.warning(f"Tests reference missing merchants: {missing_merchants}")
            else:
                logger.debug("All test merchant references are valid")
        
        # Check for missing address references
        if 'address_data' in tests.columns:
            test_addresses = set(tests['address_data'].dropna().unique())
            available_addresses = set(address.index)
            missing_addresses = test_addresses - available_addresses
            if missing_addresses:
                logger.warning(f"Tests reference missing addresses: {missing_addresses}")
            else:
                logger.debug("All test address references are valid")
        
        # Check for missing network token references
        if 'network_token_data' in tests.columns:
            test_tokens = set(tests['network_token_data'].dropna().unique())
            available_tokens = set(networktokens.index)
            missing_tokens = test_tokens - available_tokens
            if missing_tokens:
                logger.warning(f"Tests reference missing network tokens: {missing_tokens}")
            else:
                logger.debug("All test network token references are valid")
        
        # Check for missing 3D Secure references
        if 'threed_secure_data' in tests.columns:
            test_threeds = set(tests['threed_secure_data'].dropna().unique())
            available_threeds = set(threeds.index)
            missing_threeds = test_threeds - available_threeds
            if missing_threeds:
                logger.warning(f"Tests reference missing 3D Secure data: {missing_threeds}")
            else:
                logger.debug("All test 3D Secure references are valid")
        
        # Log summary statistics
        logger.info(f"✅ Data loading completed successfully")
        logger.info(f"📊 Summary: {len(environments)} envs, {len(cards)} cards, {len(merchants)} merchants, {len(address)} addresses, {len(networktokens)} tokens, {len(threeds)} 3D Secure")
        
        # Console output for backward compatibility
        print(f"📁 Loaded tests from: {tests_file}")
        print(f"📊 Test chains: {chain_count}")
        print(f"📋 Total test steps: {len(tests)}")
        print(f"🏦 Environments: {len(environments)}")
        print(f"💳 Cards: {len(cards)}")
        print(f"🏪 Merchants: {len(merchants)}")
        print(f"📍 Addresses: {len(address)}")
        print(f"🔐 Network Tokens: {len(networktokens)}")
        print(f"🔒 3D Secure: {len(threeds)}")
        
        return environments, cards, merchants, address, networktokens, threeds, tests
        
    except FileNotFoundError as e:
        logger.error(f"❌ Configuration file not found: {e}")
        logger.info("💡 Ensure all required configuration files exist:")
        logger.info("   - config/environments.csv")
        logger.info("   - config/cards.csv") 
        logger.info("   - config/merchants.csv")
        logger.info("   - config/address.csv")
        logger.info("   - config/networktoken.csv")
        logger.info("   - config/threeddata.csv")
        logger.info(f"   - {tests_file}")
        raise
        
    except pd.errors.EmptyDataError as e:
        logger.error(f"❌ Empty configuration file: {e}")
        raise
        
    except pd.errors.ParserError as e:
        logger.error(f"❌ CSV parsing error: {e}")
        logger.info("💡 Check CSV file format and encoding")
        raise
        
    except KeyError as e:
        logger.error(f"❌ Missing required column in configuration: {e}")
        logger.info("💡 Verify all required columns are present in configuration files")
        raise
        
    except Exception as e:
        logger.error(f"❌ Unexpected error during data loading: {e}", exc_info=True)
        raise