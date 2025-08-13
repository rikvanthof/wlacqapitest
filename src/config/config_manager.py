"""Enhanced configuration management with credential separation and tags support"""

import pandas as pd
import os
from pathlib import Path
from typing import Tuple, List, Optional
from dataclasses import dataclass

from ..logging_config import get_data_loader_logger

@dataclass
class ConfigPaths:
    """Configuration file paths"""
    static_dir: str = "config/static"
    credentials_dir: str = "config/credentials" 
    test_suites_dir: str = "config/test_suites"
    
    def __post_init__(self):
        # Ensure directories exist
        Path(self.static_dir).mkdir(parents=True, exist_ok=True)
        Path(self.credentials_dir).mkdir(parents=True, exist_ok=True)
        Path(self.test_suites_dir).mkdir(parents=True, exist_ok=True)

@dataclass
class ConfigSet:
    """Container for all configuration data"""
    environments: pd.DataFrame
    cards: pd.DataFrame
    merchants: pd.DataFrame
    address: pd.DataFrame
    networktokens: pd.DataFrame
    threeds: pd.DataFrame
    cardonfile: pd.DataFrame  # ← Added cardonfile support
    tests: pd.DataFrame
    credentials: pd.DataFrame

class ConfigurationManager:
    """Enhanced configuration management with credential separation"""
    
    def __init__(self, config_paths: Optional[ConfigPaths] = None):
        self.paths = config_paths or ConfigPaths()
        self.logger = get_data_loader_logger()
    
    def load_all_configs(self, tests_file: str = 'smoke_tests.csv') -> ConfigSet:
        """Load all configuration with enhanced structure"""
        self.logger.info("🚀 Starting enhanced configuration loading")
        
        try:
            # Load static configuration (shareable)
            environments = self._load_environments()
            cards = self._load_cards()
            merchants = self._load_merchants()
            address = self._load_address()
            networktokens = self._load_networktokens()
            threeds = self._load_threeds()
            cardonfile = self._load_cardonfile()  # ← Added cardonfile loading
            
            # Load credentials (private)
            credentials = self._load_credentials()
            
            # Merge environments with credentials
            environments = self._merge_environments_with_credentials(environments, credentials)
            
            # Load test suite
            tests = self._load_test_suite(tests_file)
            
            # Validate configuration consistency
            self._validate_configuration_consistency(
                environments, cards, merchants, address, 
                networktokens, threeds, cardonfile, tests  # ← Added cardonfile to validation
            )
            
            config_set = ConfigSet(
                environments=environments,
                cards=cards,
                merchants=merchants, 
                address=address,
                networktokens=networktokens,
                threeds=threeds,
                cardonfile=cardonfile,  # ← Added cardonfile to ConfigSet
                tests=tests,
                credentials=credentials
            )
            
            self.logger.info("✅ Enhanced configuration loading completed")
            return config_set
            
        except Exception as e:
            self.logger.error(f"❌ Configuration loading failed: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _load_environments(self) -> pd.DataFrame:
        """Load environment configuration (without credentials)"""
        file_path = f"{self.paths.static_dir}/environments.csv"
        self.logger.debug(f"Loading environments from: {file_path}")
        
        environments = pd.read_csv(file_path).set_index('env')
        self.logger.info(f"🏦 Environments loaded: {len(environments)} environments")
        self.logger.debug(f"Available environments: {list(environments.index)}")
        return environments
    
    def _load_cards(self) -> pd.DataFrame:
        """Load cards configuration"""
        file_path = f"{self.paths.static_dir}/cards.csv"
        self.logger.debug(f"Loading cards from: {file_path}")
        
        cards = pd.read_csv(file_path, dtype={
            'card_brand': str,
            'card_bin': str,
            'card_number': str,
            'expiry_date': str,
            'card_sequence_number': str,
            'card_security_code': str,
            'card_pin': str,
            'card_description': str
        }).set_index('card_id')
        
        self.logger.info(f"💳 Cards loaded: {len(cards)} cards")
        
        # Log card brand distribution
        if 'card_brand' in cards.columns:
            brand_counts = cards['card_brand'].value_counts()
            self.logger.debug(f"Card brands: {dict(brand_counts)}")
        
        return cards
    
    def _load_merchants(self) -> pd.DataFrame:
        """Load merchants configuration"""
        file_path = f"{self.paths.static_dir}/merchants.csv"
        self.logger.debug(f"Loading merchants from: {file_path}")
        
        merchants = pd.read_csv(file_path, dtype={
            'acquirer_id': str,
            'merchant_id': str,
            'merchant_description': str
        }).set_index(['env', 'merchant'])
        
        self.logger.info(f"🏪 Merchants loaded: {len(merchants)} merchants")
        
        # Log merchant distribution by environment
        if len(merchants) > 0:
            env_counts = merchants.reset_index()['env'].value_counts()
            self.logger.debug(f"Merchants per environment: {dict(env_counts)}")
        
        return merchants
    
    def _load_address(self) -> pd.DataFrame:
        """Load address configuration"""
        file_path = f"{self.paths.static_dir}/address.csv"
        self.logger.debug(f"Loading address from: {file_path}")
        
        address = pd.read_csv(file_path, dtype={
            'cardholder_postal_code': str,
            'cardholder_address': str
        }).set_index('address_id')
        
        self.logger.info(f"📍 Addresses loaded: {len(address)} addresses")
        self.logger.debug(f"Available address IDs: {list(address.index)}")
        return address
    
    def _load_networktokens(self) -> pd.DataFrame:
        """Load network tokens configuration"""
        file_path = f"{self.paths.static_dir}/networktoken.csv"
        self.logger.debug(f"Loading network tokens from: {file_path}")
        
        networktokens = pd.read_csv(file_path, dtype={
            'wallet_id': str,
            'network_token_cryptogram': str,
            'network_token_eci': str
        }).set_index('networktoken_id')
        
        self.logger.info(f"🔐 Network Tokens loaded: {len(networktokens)} tokens")
        self.logger.debug(f"Available network token IDs: {list(networktokens.index)}")
        
        # Log network token wallet distribution
        if 'wallet_id' in networktokens.columns:
            wallet_counts = networktokens['wallet_id'].value_counts()
            self.logger.debug(f"Network tokens per wallet: {dict(wallet_counts)}")
        
        return networktokens
    
    def _load_threeds(self) -> pd.DataFrame:
        """Load 3D Secure configuration"""
        file_path = f"{self.paths.static_dir}/threeddata.csv"
        self.logger.debug(f"Loading 3D Secure from: {file_path}")
        
        threeds = pd.read_csv(file_path, dtype={
            'three_d_secure_type': str,
            'authentication_value': str,
            'eci': str,
            'version': str
        }).set_index('three_d_id')
        
        self.logger.info(f"🔒 3D Secure data loaded: {len(threeds)} configurations")
        self.logger.debug(f"Available 3D Secure IDs: {list(threeds.index)}")
        
        # Log 3D Secure type distribution
        if 'three_d_secure_type' in threeds.columns:
            type_counts = threeds['three_d_secure_type'].value_counts()
            self.logger.debug(f"3D Secure types: {dict(type_counts)}")
        
        return threeds
    
    def _load_cardonfile(self) -> pd.DataFrame:
        """Load card-on-file configuration"""
        file_path = f"{self.paths.static_dir}/cardonfile.csv"
        self.logger.debug(f"Loading card-on-file data from: {file_path}")
        
        cardonfile = pd.read_csv(file_path, dtype={
            'is_initial_transaction': str,  # ← Updated column name
            'transaction_type': str,        # ← Updated column name  
            'card_on_file_initiator': str,  # ← Updated column name
            'future_use': str               # ← Updated column name
        }).set_index('card_on_file_id')
        
        self.logger.info(f"🔄 Card-on-file data loaded: {len(cardonfile)} configurations")
        self.logger.debug(f"Available card-on-file IDs: {list(cardonfile.index)}")
        
        # Log transaction type distribution
        if 'transaction_type' in cardonfile.columns:
            type_counts = cardonfile['transaction_type'].value_counts()
            self.logger.debug(f"Card-on-file transaction types: {dict(type_counts)}")
        
        # Log initial vs subsequent transactions
        if 'is_initial_transaction' in cardonfile.columns:
            initial_counts = cardonfile['is_initial_transaction'].value_counts()
            self.logger.debug(f"Initial transaction distribution: {dict(initial_counts)}")
        
        return cardonfile
    
    def _load_credentials(self) -> pd.DataFrame:
        """Load credentials separately"""
        file_path = f"{self.paths.credentials_dir}/secrets.csv"
        
        if not os.path.exists(file_path):
            self.logger.warning(f"⚠️ Credentials file not found: {file_path}")
            self.logger.info("💡 Create config/credentials/secrets.csv with client_id,client_secret")
            # Return empty DataFrame with correct structure
            return pd.DataFrame(columns=['env', 'client_id', 'client_secret']).set_index('env')
        
        self.logger.debug(f"Loading credentials from: {file_path}")
        credentials = pd.read_csv(file_path).set_index('env')
        self.logger.info(f"🔐 Credentials loaded for {len(credentials)} environments")
        return credentials
    
    def _merge_environments_with_credentials(self, environments: pd.DataFrame, credentials: pd.DataFrame) -> pd.DataFrame:
        """Merge environment config with credentials"""
        self.logger.debug("Merging environments with credentials")
        
        # Merge on environment index
        merged = environments.join(credentials, how='left')
        
        # Check for missing credentials
        missing_creds = merged[merged['client_id'].isna()]
        if not missing_creds.empty:
            missing_envs = list(missing_creds.index)
            self.logger.warning(f"⚠️ Missing credentials for environments: {missing_envs}")
        
        return merged
    
    def _load_test_suite(self, tests_file: str) -> pd.DataFrame:
        """Load test suite with enhanced structure and tag support"""
        # Try test_suites directory first, then fallback to old location
        test_paths = [
            f"{self.paths.test_suites_dir}/{tests_file}",
            f"config/{tests_file}",  # Backward compatibility
            tests_file  # Direct path
        ]
        
        for file_path in test_paths:
            if os.path.exists(file_path):
                self.logger.debug(f"Loading tests from: {file_path}")
                
                try:
                    # Try with robust CSV parsing
                    tests = pd.read_csv(file_path, 
                                    skipinitialspace=True,  # Remove leading whitespace
                                    quotechar='"',          # Handle quoted fields
                                    escapechar='\\',        # Handle escapes
                                    on_bad_lines='warn'     # Warn about bad lines
                                    ).sort_values(['chain_id', 'step_order'])
                    
                except pd.errors.ParserError as e:
                    self.logger.error(f"❌ CSV parsing error in {file_path}: {e}")
                    self.logger.info("💡 Trying with more flexible parsing...")
                    
                    # Fallback: more flexible parsing
                    try:
                        tests = pd.read_csv(file_path, 
                                        sep=',',
                                        engine='python',     # Use Python engine (more flexible)
                                        skipinitialspace=True,
                                        quotechar='"',
                                        on_bad_lines='skip'  # Skip bad lines
                                        ).sort_values(['chain_id', 'step_order'])
                        
                        self.logger.warning(f"⚠️ Used flexible parsing for {file_path}")
                        
                    except Exception as e2:
                        self.logger.error(f"❌ Even flexible parsing failed: {e2}")
                        raise ConfigurationError(f"Cannot parse CSV file {file_path}: {e}")
                
                # Add default tags if column doesn't exist
                if 'tags' not in tests.columns:
                    tests['tags'] = ''
                    self.logger.info("ℹ️ Added empty tags column (consider adding tags to your CSV)")
                
                # Add default defer_execution if column doesn't exist  
                if 'defer_execution' not in tests.columns:
                    tests['defer_execution'] = None
                    self.logger.info("ℹ️ Added empty defer_execution column")
                
                self.logger.info(f"📋 Tests loaded: {len(tests)} test steps from {file_path}")
                
                # Analyze test data
                chain_count = tests['chain_id'].nunique()
                self.logger.info(f"📊 Test chains: {chain_count}")
                
                # Log tag analysis
                if 'tags' in tests.columns:
                    self._analyze_tags(tests)
                
                # Log test chain details (keeping existing functionality)
                chain_analysis = tests.groupby('chain_id').agg({
                    'step_order': 'count',
                    'call_type': lambda x: list(x.unique())
                }).rename(columns={'step_order': 'step_count'})
                
                for chain_id, row in chain_analysis.iterrows():
                    self.logger.debug(f"Chain {chain_id}: {row['step_count']} steps, types: {row['call_type']}")
                
                # Log call type distribution
                call_type_counts = tests['call_type'].value_counts()
                self.logger.debug(f"Call type distribution: {dict(call_type_counts)}")
                
                return tests
        
        raise FileNotFoundError(f"Test file not found in any location: {tests_file}")
    
    def _analyze_tags(self, tests: pd.DataFrame):
        """Analyze and log tag usage"""
        all_tags = set()
        for tags_str in tests['tags'].fillna(''):
            if tags_str:
                tags = [tag.strip() for tag in tags_str.split(',')]
                all_tags.update(tags)
        
        if all_tags:
            self.logger.info(f"🏷️ Found tags: {sorted(all_tags)}")
            
            # Count tag usage
            tag_counts = {}
            for tags_str in tests['tags'].fillna(''):
                if tags_str:
                    tags = [tag.strip() for tag in tags_str.split(',')]
                    for tag in tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            self.logger.debug(f"Tag usage: {tag_counts}")
        else:
            self.logger.info("ℹ️ No tags found in test data")
    
    def _validate_configuration_consistency(self, environments, cards, merchants, 
                                          address, networktokens, threeds, cardonfile, tests):
        """Validate data relationships (keeping existing validation logic)"""
        self.logger.debug("Validating data relationships...")
        
        # Check for missing card references
        if 'card_id' in tests.columns:
            test_card_ids = set(tests['card_id'].dropna().unique())
            available_card_ids = set(cards.index)
            missing_cards = test_card_ids - available_card_ids
            if missing_cards:
                self.logger.warning(f"Tests reference missing cards: {missing_cards}")
            else:
                self.logger.debug("All test card references are valid")
        
        # Check for missing environment references
        if 'env' in tests.columns:
            test_envs = set(tests['env'].dropna().unique())
            available_envs = set(environments.index)
            missing_envs = test_envs - available_envs
            if missing_envs:
                self.logger.warning(f"Tests reference missing environments: {missing_envs}")
            else:
                self.logger.debug("All test environment references are valid")
        
        # Check for missing merchant references
        if 'merchant_id' in tests.columns and 'env' in tests.columns:
            test_merchants = set()
            for _, row in tests.iterrows():
                if pd.notna(row.get('merchant_id')) and pd.notna(row.get('env')):
                    test_merchants.add((row['env'], row['merchant_id']))
            
            available_merchants = set(merchants.index)
            missing_merchants = test_merchants - available_merchants
            if missing_merchants:
                self.logger.warning(f"Tests reference missing merchants: {missing_merchants}")
            else:
                self.logger.debug("All test merchant references are valid")
        
        # Check for missing address references
        if 'address_data' in tests.columns:
            test_addresses = set(tests['address_data'].dropna().unique())
            available_addresses = set(address.index)
            missing_addresses = test_addresses - available_addresses
            if missing_addresses:
                self.logger.warning(f"Tests reference missing addresses: {missing_addresses}")
            else:
                self.logger.debug("All test address references are valid")
        
        # Check for missing network token references
        if 'network_token_data' in tests.columns:
            test_tokens = set(tests['network_token_data'].dropna().unique())
            available_tokens = set(networktokens.index)
            missing_tokens = test_tokens - available_tokens
            if missing_tokens:
                self.logger.warning(f"Tests reference missing network tokens: {missing_tokens}")
            else:
                self.logger.debug("All test network token references are valid")
        
        # Check for missing 3D Secure references
        if 'threed_secure_data' in tests.columns:
            test_threeds = set(tests['threed_secure_data'].dropna().unique())
            available_threeds = set(threeds.index)
            missing_threeds = test_threeds - available_threeds
            if missing_threeds:
                self.logger.warning(f"Tests reference missing 3D Secure data: {missing_threeds}")
            else:
                self.logger.debug("All test 3D Secure references are valid")
        
        # ← NEW: Check for missing card-on-file references
        if 'card_on_file_data' in tests.columns:
            test_cardonfiles = set(tests['card_on_file_data'].dropna().unique())
            available_cardonfiles = set(cardonfile.index)
            missing_cardonfiles = test_cardonfiles - available_cardonfiles
            if missing_cardonfiles:
                self.logger.warning(f"Tests reference missing card-on-file data: {missing_cardonfiles}")
            else:
                self.logger.debug("All test card-on-file references are valid")
    
    def list_available_test_suites(self) -> List[str]:
        """List all available test suite files"""
        test_dir = Path(self.paths.test_suites_dir)
        if test_dir.exists():
            csv_files = list(test_dir.glob("**/*.csv"))
            return [str(f.relative_to(test_dir)) for f in csv_files]
        return []
    
    def get_all_tags(self, tests_df: pd.DataFrame) -> List[str]:
        """Extract all unique tags from tests"""
        all_tags = set()
        for tags_str in tests_df['tags'].fillna(''):
            if tags_str:
                tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                all_tags.update(tags)
        return sorted(all_tags)

class ConfigurationError(Exception):
    """Configuration loading/validation errors"""
    pass