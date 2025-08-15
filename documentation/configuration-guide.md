# Configuration Guide

## Overview

The Payment API Testing Framework uses CSV files for configuration, making it easy to manage test data, environments, and scenarios without code changes. The framework supports advanced payment features including Card-on-File, 3D Secure, Network Tokens, and Address Verification.

## Configuration Directory Structure

```
config/
├── static/
│   ├── environments.csv    # API endpoint configurations
│   ├── merchants.csv       # Merchant account settings
│   ├── cards.csv          # Test card data
│   ├── address.csv        # Address data for AVS testing
│   ├── networktokens.csv  # Network tokenization data
│   ├── threeddata.csv     # 3D Secure authentication data
│   └── cardonfile.csv     # Card-on-File configurations
└── test_suites/
    ├── smoke_tests.csv    # Quick validation tests
    ├── regression.csv     # Comprehensive test scenarios
    ├── ucof_tests.csv     # Card-on-File test scenarios
    └── custom_tests.csv   # Custom test definitions
```

## Core Configuration Files

### 1. Test Suite Files (test_suites/*.csv) - Test Definitions

**Purpose:** Defines the sequence of API calls that make up test chains with advanced payment features.

**Required Columns:**
- `chain_id` - Unique identifier for the test chain
- `step_order` - Order of execution within the chain (1, 2, 3...)
- `call_type` - Type of API call to make
- `test_id` - Unique identifier for this test step
- `tags` - Comma-separated tags for filtering (smoke, regression, ucof, 3ds, etc.)
- `card_id` - Reference to card in cards.csv (for create_payment)
- `merchant_id` - Reference to merchant in merchants.csv
- `env` - Environment to run in (matches environments.csv)
- `amount` - Transaction amount (where applicable)
- `currency` - Currency code (GBP, EUR, USD, etc.)

**Advanced Payment Feature Columns:**
- `address_data` - Reference to address.csv for AVS testing
- `threed_secure_data` - Reference to threeddata.csv for 3D Secure
- `network_token_data` - Reference to networktokens.csv for tokenized payments
- `card_on_file_data` - Reference to cardonfile.csv for UCOF scenarios

**Optional Payment Columns:**
- `authorization_type` - FINAL_AUTHORIZATION, PRE_AUTHORIZATION
- `capture_immediately` - TRUE/FALSE for immediate capture
- `card_entry_mode` - ECOMMERCE, MANUAL, etc.
- `cardholder_verification_method` - THREE_DS, CARD_SECURITY_CODE, etc.
- `dynamic_descriptor` - Merchant descriptor text

**Assertion Columns:**
- `expected_http_status` - Expected HTTP response code (201, 200, etc.)
- `expected_response_code` - Expected API response code (0 = success)
- `expected_total_auth_amount` - Expected authorization amount
- `expected_card_security_result` - Expected CVV result (MATCH, etc.)
- `expected_avs_result` - Expected AVS result (MATCH, NO_MATCH, etc.)

**Supported Call Types:**
- `create_payment` - Create a new payment
- `increment_payment` - Increment payment authorization
- `capture_payment` - Capture a payment
- `refund_payment` - Refund a payment
- `get_payment` - Retrieve payment status
- `get_refund` - Retrieve refund status

**Example:**
```csv
chain_id,step_order,call_type,test_id,tags,card_id,merchant_id,env,amount,currency,authorization_type,capture_immediately,address_data,threed_secure_data,card_on_file_data,expected_http_status,expected_response_code
ucof_chain,1,create_payment,INITIAL_COF,ucof,visa_card,merchant1,preprod,1000,GBP,FINAL_AUTHORIZATION,TRUE,AVS_FULL,VISA_FULL,FIRSTUCOF-CIT,201,0
ucof_chain,2,create_payment,SUBSEQUENT_COF,ucof,visa_card,merchant1,preprod,500,GBP,FINAL_AUTHORIZATION,TRUE,AVS_FULL,VISA_FULL,SUBSEQUENTUCOF-CIT,201,0
```

### 2. environments.csv - API Environments

**Purpose:** Configures API endpoints and authentication for different environments.

**Required Columns:**
- `env` - Environment identifier (used in test files)
- `integrator` - Integration name
- `endpoint_host` - API hostname
- `authorization_type` - Authentication method (OAuth2)
- `oauth2_token_uri` - OAuth token endpoint
- `client_id` - OAuth client identifier
- `client_secret` - OAuth client secret
- `connect_timeout` - Connection timeout (seconds)
- `socket_timeout` - Socket timeout (seconds)
- `max_connections` - Maximum concurrent connections

**Example:**
```csv
env,integrator,endpoint_host,authorization_type,oauth2_token_uri,connect_timeout,socket_timeout,max_connections,client_id,client_secret
preprod,Test Integration,api.preprod.acquiring.worldline-solutions.com,OAuth2,https://auth-test-eu-west-1.aws.bambora.com/connect/token,5,300,10,your-client-id,your-client-secret
prod,Prod Integration,api.acquiring.worldline-solutions.com,OAuth2,https://auth-eu-west-1.aws.bambora.com/connect/token,5,300,10,your-prod-client-id,your-prod-client-secret
```

### 3. merchants.csv - Merchant Configurations

**Purpose:** Maps merchant identifiers to actual acquirer and merchant IDs.

**Required Columns:**
- `merchant` - Friendly merchant identifier (used in test files)
- `env` - Environment this configuration applies to
- `acquirer_id` - Worldline acquirer identifier
- `merchant_id` - Worldline merchant identifier
- `merchant_description` - Descriptive name for reporting

**Example:**
```csv
merchant,env,acquirer_id,merchant_id,merchant_description
merchant1,preprod,100812,520001857,Pre-prod ECOM/DCC Test Merchant
merchant1,prod,100812,520009999,Production ECOM Merchant
merchant2,preprod,100812,520001858,Pre-prod POS Test Merchant
```

### 4. cards.csv - Test Card Data

**Purpose:** Defines test payment cards with their properties.

**Required Columns:**
- `card_id` - Unique card identifier (used in test files)
- `card_brand` - Card brand (VISA, MASTERCARD, etc.)
- `card_number` - Full card number
- `expiry_date` - Expiry date (MMYYYY format)
- `card_description` - Descriptive name for reporting

**Optional Columns:**
- `card_bin` - Bank Identification Number
- `card_sequence_number` - Card sequence number
- `card_security_code` - CVV/CVC code
- `card_pin` - PIN for chip and PIN transactions

**Example:**
```csv
card_id,card_brand,card_bin,card_number,expiry_date,card_sequence_number,card_security_code,card_pin,card_description
visa_card,VISA,411111,4111111111111111,122025,,123,,VISA Test Card
mc_card,MASTERCARD,522222,5222222222222222,122025,,456,,Mastercard Test Card
visa_seq,VISA,411111,4111111111111111,122025,001,123,1234,VISA with Sequence
```

## Advanced Payment Feature Configuration

### 5. address.csv - Address Verification Service (AVS)

**Purpose:** Address data for AVS testing scenarios.

**Columns:**
- `address_id` - Unique address identifier
- `cardholder_postal_code` - Postal/ZIP code
- `cardholder_address` - Street address

**Usage:** Reference `address_id` in test files using `address_data` column.

**Example:**
```csv
address_id,cardholder_postal_code,cardholder_address
AVS_FULL,8021,Hardturmstrasse 201
AVS_PARTIAL,SW1A 1AA,123 Test Street
AVS_NOMATCH,00000,Invalid Address
```

### 6. networktokens.csv - Network Tokenization

**Purpose:** Network token data for Apple Pay, Google Pay, and other tokenized transactions.

**Columns:**
- `networktoken_id` - Unique token identifier
- `wallet_id` - Wallet identifier (103 = Apple Pay, etc.)
- `network_token_cryptogram` - Token cryptogram
- `network_token_eci` - Electronic Commerce Indicator

**Example:**
```csv
networktoken_id,wallet_id,network_token_cryptogram,network_token_eci
APPLE_PAY_VISA,103,/wAAAAEACwuDlYgAAAAAgIRgE4A=,05
APPLE_PAY_MASTERCARD,103,/wAAAAEACwuDlYgAAAAAgIRgE4A=,02
GOOGLE_PAY_VISA,104,AgAAABceBFogEAAAgAAAYwEAAA==,05
```

### 7. threeddata.csv - 3D Secure Authentication

**Purpose:** 3D Secure authentication data for enhanced security testing.

**Columns:**
- `three_d_id` - Unique 3DS identifier
- `three_d_secure_type` - Type of 3DS authentication
- `authentication_value` - Authentication value
- `eci` - Electronic Commerce Indicator
- `version` - 3DS version

**Example:**
```csv
three_d_id,three_d_secure_type,authentication_value,eci,version
VISA_FULL,THREE_DS,AAABBEg0VhI0VniQEjRWAAAAAAA=,05,2.2.0
MASTERCARD_FULL,THREE_DS,AAABBEg0VhI0VniQEjRWAAAAAAA=,02,2.2.0
VISA_ATTEMPTED,THREE_DS_ATTEMPTED,AAABBEg0VhI0VniQEjRWAAAAAAA=,06,2.2.0
```

### 8. cardonfile.csv - Card-on-File (UCOF) Configuration

**Purpose:** Card-on-File configurations for initial and subsequent UCOF transactions.

**Columns:**
- `card_on_file_id` - Unique COF identifier
- `is_initial_transaction` - TRUE for initial, FALSE for subsequent
- `transaction_type` - UNSCHEDULED_CARD_ON_FILE, RECURRING, etc.
- `card_on_file_initiator` - CARDHOLDER or MERCHANT (for subsequent only)
- `future_use` - CARDHOLDER_INITIATED, MERCHANT_INITIATED (for initial only)

**Example:**
```csv
card_on_file_id,is_initial_transaction,transaction_type,card_on_file_initiator,future_use
FIRSTUCOF-CIT,TRUE,UNSCHEDULED_CARD_ON_FILE,,CARDHOLDER_INITIATED
SUBSEQUENTUCOF-CIT,FALSE,UNSCHEDULED_CARD_ON_FILE,CARDHOLDER,
SUBSEQUENTUCOF-MIT,FALSE,UNSCHEDULED_CARD_ON_FILE,MERCHANT,
FIRSTRECURRING,TRUE,RECURRING,,MERCHANT_INITIATED
```

## Configuration Best Practices

### 1. Data Organization

**Separate by Environment:**
- Use different merchant entries for each environment
- Maintain separate client credentials per environment
- Use descriptive merchant names including environment

**Logical Grouping:**
- Group related test cards together
- Use consistent naming conventions
- Include descriptive names for easier debugging

**Feature-Based Organization:**
- Create separate test suites for different features (UCOF, 3DS, etc.)
- Use tags to categorize tests (ucof, 3ds, avs, smoke, regression)
- Maintain feature-specific configuration data

### 2. Security Considerations

> **⚠️ Sensitive Data:**
> - Store client secrets securely
> - Use environment-specific credentials
> - Consider using environment variables for production secrets
> - Never commit real production credentials to version control

> **🔒 Test Data:**
> - Use only test card numbers provided by Worldline
> - Ensure test data doesn't contain real customer information
> - Use realistic but fake address data
> - Rotate test credentials regularly

### 3. Maintainability

**Naming Conventions:**
```
Card IDs: visa_card, mc_card, visa_premium, mc_corporate
Merchant IDs: merchant1, ecom_merchant, pos_merchant
Chain IDs: basic_flow, ucof_chain, 3ds_flow, regression_001
Test IDs: PAY001, CAP001, REF001 (consistent within chains)
Feature IDs: FIRSTUCOF-CIT, VISA_FULL, AVS_MATCH
```

**Documentation:**
- Use descriptive names in description fields
- Comment complex test scenarios in separate documentation
- Maintain a mapping document for complex setups
- Document business logic behind test scenarios

### 4. Validation

**Required Field Validation:**
- Ensure all required columns are present
- Validate data types and formats
- Check foreign key relationships between files
- Verify enum values (card brands, transaction types, etc.)

**Data Consistency:**
- Verify merchant/environment combinations exist
- Ensure card data is valid for the intended tests
- Check that chain dependencies are properly ordered
- Validate feature-specific configurations

## Environment-Specific Configuration

### Development Environment
```csv
env,integrator,endpoint_host,client_id,client_secret
dev,Dev Testing,api.dev.acquiring.worldline-solutions.com,dev-client-id,dev-secret
```

### Staging/Pre-production
```csv
env,integrator,endpoint_host,client_id,client_secret
preprod,Staging Tests,api.preprod.acquiring.worldline-solutions.com,preprod-client-id,preprod-secret
```

### Production
```csv
env,integrator,endpoint_host,client_id,client_secret
prod,Production,api.acquiring.worldline-solutions.com,prod-client-id,prod-secret
```

## Common Configuration Patterns

### Basic Payment Flow
```csv
chain_id,step_order,call_type,test_id,tags,amount,currency,expected_http_status
basic_flow,1,create_payment,CREATE_001,smoke,1000,GBP,201
basic_flow,2,capture_payment,CAPTURE_001,smoke,1000,GBP,201
basic_flow,3,get_payment,GET_001,smoke,,,200
```

### Card-on-File (UCOF) Flow
```csv
chain_id,step_order,call_type,test_id,tags,amount,currency,card_on_file_data,expected_http_status
ucof_flow,1,create_payment,INITIAL_COF,ucof,1000,GBP,FIRSTUCOF-CIT,201
ucof_flow,2,create_payment,SUBSEQUENT_COF,ucof,500,GBP,SUBSEQUENTUCOF-CIT,201
```

### 3D Secure Flow
```csv
chain_id,step_order,call_type,test_id,tags,amount,currency,threed_secure_data,cardholder_verification_method,expected_http_status
3ds_flow,1,create_payment,3DS_PAY,3ds,2000,EUR,VISA_FULL,THREE_DS,201
3ds_flow,2,capture_payment,3DS_CAP,3ds,2000,EUR,,,201
```

### Authorization and Capture
```csv
chain_id,step_order,call_type,test_id,tags,amount,currency,authorization_type,capture_immediately,expected_http_status
auth_capture,1,create_payment,AUTH_001,regression,5000,EUR,PRE_AUTHORIZATION,FALSE,201
auth_capture,2,increment_payment,INC_001,regression,1000,EUR,,,201
auth_capture,3,capture_payment,CAP_001,regression,6000,EUR,,,201
```

### Network Token Flow
```csv
chain_id,step_order,call_type,test_id,tags,amount,currency,network_token_data,expected_http_status
applepay_flow,1,create_payment,APPLEPAY_001,applepay,1500,USD,APPLE_PAY_VISA,201
applepay_flow,2,get_payment,APPLEPAY_GET,applepay,,,200
```

### Address Verification Flow
```csv
chain_id,step_order,call_type,test_id,tags,amount,currency,address_data,expected_avs_result,expected_http_status
avs_flow,1,create_payment,AVS_MATCH,avs,1000,GBP,AVS_FULL,MATCH,201
avs_flow,2,create_payment,AVS_NOMATCH,avs,1000,GBP,AVS_NOMATCH,NO_MATCH,201
```

## Troubleshooting Configuration

### Common Issues

**"Environment X not defined"**
- Check environments.csv contains the referenced environment
- Verify environment name matches exactly (case-sensitive)
- Ensure credentials are properly configured

**"Merchant Y not defined for env Z"**
- Ensure merchants.csv has entry for merchant+environment combination
- Check for typos in merchant or environment names
- Verify acquirer_id and merchant_id are correct

**"Card ID not found"**
- Verify card exists in cards.csv
- Check card_id reference in test files matches exactly
- Ensure card data is properly formatted

**"Feature configuration not found"**
- Check cardonfile.csv for card-on-file references
- Verify threeddata.csv for 3D Secure references
- Ensure address.csv for AVS references
- Validate networktokens.csv for tokenized payment references

**Invalid CSV Format**
- Ensure proper CSV formatting with quoted fields containing commas
- Check for missing headers or extra columns
- Validate that required columns are present
- Check for special characters or encoding issues

### Validation Commands

```bash
# Validate all configuration files can be loaded
python -c "
from src.config.config_manager import ConfigurationManager
config_manager = ConfigurationManager()
config_set = config_manager.load_all_configs('config/test_suites/smoke_tests.csv')
print('✅ Configuration validation successful')
"

# Check specific test file
python -c "
from src.config.config_manager import ConfigurationManager
config_manager = ConfigurationManager()
config_set = config_manager.load_all_configs('config/test_suites/your_test_file.csv')
print(f'Tests loaded: {len(config_set.tests)}')
print(f'Cards loaded: {len(config_set.cards)}')
print(f'COF configs: {len(config_set.cardonfile)}')
"

# Test configuration integrity
python -m src.main --tests smoke_tests.csv --verbose
```

### Debug Configuration Issues

```bash
# Enable verbose logging to see configuration loading
python -m src.main --tests your_test.csv --verbose

# Test with minimal configuration
python -m src.main --tags smoke --verbose

# Validate specific features
python -m src.main --tags ucof --verbose
python -m src.main --tags 3ds --verbose
```

> **✅ Configuration Complete:** With these configuration files properly set up, your payment API testing framework will be ready to execute comprehensive test scenarios across different environments and advanced payment features including Card-on-File, 3D Secure, Network Tokens, and Address Verification.