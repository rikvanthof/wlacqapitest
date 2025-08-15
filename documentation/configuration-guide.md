# Configuration Guide

## Overview

The Payment API Testing Framework uses CSV files for configuration, making it easy to manage test data, environments, and scenarios without code changes. The framework supports advanced payment features including Card-on-File, 3D Secure, Network Tokens, Address Verification, SCA Exemptions, Merchant Data, Partial Operations, and Brand Selection.

## Configuration Directory Structure

```
config/
├── credentials/
│   ├── README.md
│   ├── secrets.csv.template    # Template for API credentials
│   └── secrets.csv            # Your actual API credentials (gitignored)
├── static/
│   ├── address.csv            # Address data for AVS testing
│   ├── cardonfile.csv         # Card-on-File configurations
│   ├── cards.csv              # Test card data
│   ├── environments.csv       # API endpoint configurations
│   ├── merchantdata.csv       # Merchant information data
│   ├── merchants.csv          # Merchant account settings
│   ├── networktoken.csv       # Network tokenization data
│   └── threeddata.csv         # 3D Secure authentication & SCA exemptions
└── test_suites/
    ├── custom/                # Custom test scenarios
    └── smoke_tests.csv        # Quick validation tests
```

## Core Configuration Files

### 1. API Credentials (credentials/secrets.csv)

**Purpose:** Secure storage of API credentials separate from other configuration.

**File Location:** `config/credentials/secrets.csv`

**Setup:**
```bash
# Copy template
cp config/credentials/secrets.csv.template config/credentials/secrets.csv

# Edit with your actual credentials
nano config/credentials/secrets.csv
```

**Required Columns:**
- `env` - Environment identifier (matches environments.csv)
- `client_id` - OAuth2 client identifier
- `client_secret` - OAuth2 client secret

**Example:**
```csv
env,client_id,client_secret
dev,your-dev-client-id,your-dev-client-secret
preprod,your-test-client-id,your-test-client-secret
prod,your-prod-client-id,your-prod-client-secret
```

> **🔒 Security Note:** This file is gitignored and contains sensitive credentials. Never commit real credentials to version control.

### 2. Environment Configuration (static/environments.csv)

**Purpose:** API endpoint and connection configuration for different environments.

**Required Columns:**
- `env` - Environment identifier
- `integrator` - Integration name
- `endpoint_host` - API hostname
- `authorization_type` - Authentication method (OAuth2)
- `oauth2_token_uri` - OAuth token endpoint
- `connect_timeout` - Connection timeout (seconds)
- `socket_timeout` - Socket timeout (seconds)
- `max_connections` - Maximum concurrent connections

**Example:**
```csv
env,integrator,endpoint_host,authorization_type,oauth2_token_uri,connect_timeout,socket_timeout,max_connections
dev,Augmented Rik,api.dev.acquiring.worldline-solutions.com,OAuth2,https://auth-test-eu-west-1.aws.bambora.com/connect/token,5,300,10
preprod,Augmented Rik,api.preprod.acquiring.worldline-solutions.com,OAuth2,https://auth-test-eu-west-1.aws.bambora.com/connect/token,5,300,10
prod,Augmented Rik,api.acquiring.worldline-solutions.com,OAuth2,https://auth-eu-west-1.aws.bambora.com/connect/token,5,300,10
```

### 3. Merchant Configuration (static/merchants.csv)

**Purpose:** Maps merchant identifiers to actual acquirer and merchant IDs.

**Required Columns:**
- `merchant` - Friendly merchant identifier
- `env` - Environment this configuration applies to
- `acquirer_id` - Worldline acquirer identifier
- `merchant_id` - Worldline merchant identifier
- `merchant_description` - Descriptive name for reporting

**Example:**
```csv
merchant,env,acquirer_id,merchant_id,merchant_description
merchant1,preprod,100812,520001857,Pre-prod ECOM/DCC Ixopay (520001857)
merchant2,preprod,100812,520002898,Pre-prod ECOM/DCC Yuliia (520002898)
merchant1,prod,100812,520009999,Production ECOM Merchant
```

### 4. Test Card Data (static/cards.csv)

**Purpose:** Defines test payment cards with their properties.

**Required Columns:**
- `card_id` - Unique card identifier
- `card_brand` - Card brand (VISA, MASTERCARD, etc.)
- `card_bin` - Bank Identification Number
- `card_number` - Full card number
- `expiry_date` - Expiry date (MMYYYY format)
- `card_description` - Descriptive name for reporting

**Optional Columns:**
- `card_sequence_number` - Card sequence number
- `card_security_code` - CVV/CVC code
- `card_pin` - PIN for chip and PIN transactions

**Example:**
```csv
card_id,card_brand,card_bin,card_number,expiry_date,card_sequence_number,card_security_code,card_pin,card_description
VisaR1,VISA,4176669999,4176669999000104,122031,,012,1234,VISA Test Card R1
card01,MASTERCARD,54133300,5413330089600010,122031,,123,4315,Mastercard PPC_MCD_01
card07,VISA,411111,4111111111111111,122025,,123,,Standard VISA Test Card
```

## Test Suite Configuration

### 5. Test Definitions (test_suites/*.csv)

**Purpose:** Defines the sequence of API calls that make up test chains with advanced payment features.

**Core Required Columns:**
- `chain_id` - Unique identifier for the test chain
- `step_order` - Order of execution within the chain (1, 2, 3...)
- `call_type` - Type of API call to make
- `test_id` - Unique identifier for this test step
- `tags` - Comma-separated tags for filtering
- `card_id` - Reference to card in cards.csv (for card-based operations)
- `merchant_id` - Reference to merchant in merchants.csv
- `env` - Environment to run in (matches environments.csv)
- `amount` - Transaction amount (where applicable)
- `currency` - Currency code (GBP, EUR, USD, etc.)

**Advanced Payment Feature Columns:**
- `address_data` - Reference to address.csv for AVS testing
- `threed_secure_data` - Reference to threeddata.csv for 3D Secure & SCA exemptions
- `network_token_data` - Reference to networktoken.csv for tokenized payments
- `card_on_file_data` - Reference to cardonfile.csv for UCOF scenarios
- `merchant_data` - Reference to merchantdata.csv for merchant information

**API Property Columns:**
- `brand_selector` - Payment brand selection (CARDHOLDER, MERCHANT)
- `is_final` - Final capture flag for partial captures (true, false)
- `capture_sequence_number` - Sequence number for partial captures (1, 2, 3...)
- `defer_execution` - Defer test execution (for complex scenarios)

**DCC Columns:**
- `use_dcc` - Enable Dynamic Currency Conversion
- `dcc_target_currency` - Target currency for conversion

**Payment Control Columns:**
- `authorization_type` - FINAL_AUTHORIZATION, PRE_AUTHORIZATION
- `allow_partial_approval` - Enable partial approval (true, false)
- `capture_immediately` - Immediate capture flag (TRUE, FALSE)
- `card_entry_mode` - Entry method (ECOMMERCE, MANUAL, etc.)
- `cardholder_verification_method` - Verification method (THREE_DS, CARD_SECURITY_CODE, etc.)
- `dynamic_descriptor` - Custom merchant descriptor

**Assertion Columns:**
- `expected_http_status` - Expected HTTP response code (201, 200, etc.)
- `expected_response_code` - Expected API response code (0 = success)
- `expected_total_auth_amount` - Expected authorization amount
- `expected_card_security_result` - Expected CVV result (MATCH, etc.)
- `expected_avs_result` - Expected AVS result (MATCH, NO_MATCH, etc.)
- `expected_merchant_advice_code` - Expected merchant advice code

**Example:**
```csv
chain_id,step_order,call_type,test_id,tags,defer_execution,card_id,merchant_id,env,amount,currency,authorization_type,allow_partial_approval,capture_immediately,card_entry_mode,cardholder_verification_method,dynamic_descriptor,address_data,threed_secure_data,network_token_data,card_on_file_data,merchant_data,brand_selector,is_final,use_dcc,dcc_target_currency,expected_http_status,expected_response_code,expected_total_auth_amount,expected_card_security_result,expected_avs_result,expected_merchant_advice_code
chain1,1,create_payment,TEST001,"smoke,visa,basic",,card07,merchant1,preprod,100,GBP,PRE_AUTHORIZATION,,FALSE,ECOMMERCE,CARD_SECURITY_CODE,,,,,,,MERCHANT,,,201,0,100,MATCH,,
chain1,2,capture_payment,TEST002,"smoke,visa",,,merchant1,preprod,50,EUR,,,,,,,,,,,,,true,,,201,0,,,,
sca_chain,1,create_payment,SCA001,"sca,exemption",,card07,merchant1,preprod,25,EUR,FINAL_AUTHORIZATION,,TRUE,ECOMMERCE,CARD_SECURITY_CODE,,LVP_NO3DS,,,EU_MERCHANT,MERCHANT,,,201,0,25,MATCH,,
```

## Advanced Payment Feature Configuration

### 6. Address Verification (static/address.csv)

**Purpose:** Address data for AVS testing scenarios.

**Columns:**
- `address_id` - Unique address identifier
- `cardholder_postal_code` - Postal/ZIP code
- `cardholder_address` - Street address

**Example:**
```csv
address_id,cardholder_postal_code,cardholder_address
AVS_FULL,8021,Hardturmstrasse 201
AVS_PARTIAL,SW1A 1AA,123 Test Street
AVS_NOMATCH,00000,Invalid Address
```

### 7. Network Tokenization (static/networktoken.csv)

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

### 8. 3D Secure & SCA Exemptions (static/threeddata.csv)

**Purpose:** 3D Secure authentication data and SCA exemption requests for enhanced security and compliance testing.

**Columns:**
- `three_d_id` - Unique 3DS/exemption identifier
- `three_d_secure_type` - Type of 3DS authentication (optional for exemption-only)
- `authentication_value` - Authentication value (optional for exemption-only)
- `eci` - Electronic Commerce Indicator (optional for exemption-only)
- `version` - 3DS version (optional for exemption-only)
- `sca_exemption_requested` - SCA exemption type (optional)

**SCA Exemption Values:**
- `LOW_VALUE_PAYMENT` - For transactions under €30
- `TRANSACTION_RISK_ANALYSIS` - Based on fraud risk assessment
- `TRUSTED_BENEFICIARY` - Whitelisted merchant scenarios
- `SECURE_CORPORATE_PAYMENT` - Corporate payment exemptions
- `SCA_DELEGATION` - SCA handling delegated to issuer

**Example:**
```csv
three_d_id,three_d_secure_type,authentication_value,eci,version,sca_exemption_requested
VISA_FULL,THREE_DS,AAABBEg0VhI0VniQEjRWAAAAAAA=,05,2.2.0,
MASTERCARD_FULL,THREE_DS,AAABBEg0VhI0VniQEjRWAAAAAAA=,02,2.2.0,
VISA_ATTEMPTED,THREE_DS_ATTEMPTED,AAABBEg0VhI0VniQEjRWAAAAAAA=,06,2.2.0,
LVP_NO3DS,,,,,LOW_VALUE_PAYMENT
TRA_NO3DS,,,,,TRANSACTION_RISK_ANALYSIS
TRUSTED_NO3DS,,,,,TRUSTED_BENEFICIARY
CORP_NO3DS,,,,,SECURE_CORPORATE_PAYMENT
VISA_FULL_DELEGATION,THREE_DS,AAABBEg0VhI0VniQEjRWAAAAAAA=,05,2.2.0,SCA_DELEGATION
```

### 9. Card-on-File Configuration (static/cardonfile.csv)

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

### 10. Merchant Information (static/merchantdata.csv)

**Purpose:** Comprehensive merchant information for enhanced payment processing and compliance.

**Required Columns:**
- `merchant_id` - Unique merchant identifier
- `merchant_category_code` - Merchant Category Code (MCC) 0-9999
- `name` - Merchant business name

**Optional Columns:**
- `address` - Merchant street address
- `postal_code` - Merchant postal/ZIP code
- `city` - Merchant city
- `state_code` - State/province code (for US/CA)
- `country_code` - ISO 3166-1 alpha-2 country code

**Example:**
```csv
merchant_id,merchant_category_code,name,address,postal_code,city,state_code,country_code
DEFAULT_MERCHANT,5812,Test Restaurant Ltd,123 Main Street,12345,New York,NY,US
EU_MERCHANT,5411,European Grocery Store,456 High Street,SW1A 1AA,London,,GB
CA_MERCHANT,5999,Canadian Test Store,789 Maple Ave,K1A 0A6,Ottawa,ON,CA
MINIMAL_MERCHANT,7999,Minimal Data Merchant,,,,,
RESTAURANT_US,5812,American Diner,111 Food Street,10001,New York,NY,US
RESTAURANT_EU,5812,French Bistro,222 Rue de la Paix,75001,Paris,,FR
```

## Configuration Best Practices

### 1. Security Management

**Credentials Separation:**
- Keep credentials in `config/credentials/secrets.csv` (gitignored)
- Store environment configurations separately in `config/static/environments.csv`
- Use different credentials for each environment (dev/preprod/prod)

**Test Data Security:**
- Use only Worldline-provided test card numbers
- Never use real customer data
- Use realistic but fake merchant information
- Rotate test credentials regularly

### 2. File Organization

**Naming Conventions:**
```
Card IDs: card01, card07, VisaR1, etc.
Merchant IDs: merchant1, merchant2, etc.
Chain IDs: chain1, sca_chain, partial_chain, etc.
Test IDs: TEST001, SCA001, PARTIAL001, etc.
Feature IDs: FIRSTUCOF-CIT, VISA_FULL, AVS_MATCH, DEFAULT_MERCHANT
```

**Environment Consistency:**
- Ensure environment names match between files
- Use consistent merchant configurations per environment
- Maintain separate test suites for different environments

### 3. Advanced Feature Configuration

**SCA Exemptions:**
- Use exemption-only scenarios for compliance testing
- Combine 3DS + exemption for complex flows
- Test all exemption types for regulatory coverage

**Partial Operations:**
- Design sequences with proper `is_final` flag usage
- Use sequential capture numbering (1, 2, 3...)
- Test both partial and full operation scenarios

**Merchant Data:**
- Use appropriate MCC codes for business types
- Include complete address data where possible
- Test minimal data scenarios for edge cases

## Common Configuration Patterns

### Basic Payment Flow
```csv
chain_id,step_order,call_type,test_id,tags,card_id,merchant_id,env,amount,currency,expected_http_status
basic_flow,1,create_payment,CREATE_001,smoke,card07,merchant1,preprod,1000,GBP,201
basic_flow,2,capture_payment,CAPTURE_001,smoke,,,preprod,1000,GBP,201
```

### SCA Exemption Flow
```csv
chain_id,step_order,call_type,test_id,tags,threed_secure_data,merchant_data,expected_http_status
sca_lvp_flow,1,create_payment,LVP_PAY,sca,LVP_NO3DS,EU_MERCHANT,201
sca_tra_flow,1,create_payment,TRA_PAY,sca,TRA_NO3DS,DEFAULT_MERCHANT,201
```

### Partial Operations Flow
```csv
chain_id,step_order,call_type,test_id,tags,amount,authorization_type,capture_immediately,is_final,capture_sequence_number,expected_http_status
partial_flow,1,create_payment,PARTIAL_AUTH,partial,1000,PRE_AUTHORIZATION,FALSE,,,201
partial_flow,2,capture_payment,PARTIAL_CAP1,partial,300,,,false,1,201
partial_flow,3,capture_payment,PARTIAL_CAP2,partial,700,,,true,2,201
```

### Brand Selection Flow
```csv
chain_id,step_order,call_type,test_id,tags,brand_selector,merchant_data,expected_http_status
brand_flow,1,create_payment,MERCHANT_BRAND,brand,MERCHANT,DEFAULT_MERCHANT,201
brand_flow,2,standalone_refund,CARDHOLDER_REF,brand,CARDHOLDER,DEFAULT_MERCHANT,201
```

## Validation and Troubleshooting

### Configuration Validation

```bash
# Test configuration loading
python -c "
from src.config.config_manager import ConfigurationManager
config_manager = ConfigurationManager()
config_set = config_manager.load_all_configs('config/test_suites/smoke_tests.csv')
print('✅ Configuration validation successful')
print(f'Tests: {len(config_set.tests)}')
print(f'Cards: {len(config_set.cards)}')
print(f'Merchants: {len(config_set.merchants)}')
print(f'Environments: {len(config_set.environments)}')
"
```

### Common Issues

**"Environment X not defined"**
- Check environments.csv contains the referenced environment
- Verify credentials exist in secrets.csv for that environment

**"Merchant Y not defined"**
- Ensure merchants.csv has entry for merchant+environment combination
- Check for typos in merchant or environment names

**"Network token configuration not found"**
- Verify networktoken.csv (not networktokens.csv) contains referenced IDs
- Check token configuration format

**"Invalid SCA exemption configuration"**
- Verify sca_exemption_requested values match supported exemptions
- Check exemption-only scenarios have no 3DS data

### Debug Configuration

```bash
# Enable verbose logging
python -m src.main --tests smoke_tests.csv --verbose

# Test specific configurations
python -c "import pandas as pd; print(pd.read_csv('config/static/cards.csv').head())"
python -c "import pandas as pd; print(pd.read_csv('config/static/merchantdata.csv').head())"
```

> **✅ Configuration Complete:** With these configuration files properly set up, your payment API testing framework will be ready to execute comprehensive test scenarios across different environments and advanced payment features including Card-on-File, 3D Secure, Network Tokens, Address Verification, SCA Exemptions, Merchant Data, Partial Operations, and Brand Selection.