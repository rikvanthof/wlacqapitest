# Payment API Testing Framework - User Guide

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Configuration Files](#configuration-files)
- [Advanced Payment Features](#advanced-payment-features)
- [API Properties and Enhancements](#api-properties-and-enhancements)
- [Threading Behavior](#threading-behavior)
- [Tag-Based Filtering](#tag-based-filtering)
- [Error Handling](#error-handling)
- [Output Format](#output-format)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Payment API Testing Framework is a comprehensive tool for testing Worldline Acquiring API endpoints. It supports end-to-end payment scenarios with chained API calls, parallel execution, advanced payment features (Card-on-File, 3D Secure, Network Tokens, AVS), API property enhancements (partial operations, SCA compliance, merchant data, brand selection), and detailed result tracking with comprehensive assertion validation.

## Quick Start

### Basic Test Execution

Run tests with default settings (sequential execution):

```bash
python -m src.main
```

### Common Usage Patterns

**Parallel execution with 3 threads:**
```bash
python -m src.main --threads 3
```

**Use custom test file:**
```bash
python -m src.main --tests smoke_tests.csv
```

**Verbose output for debugging:**
```bash
python -m src.main --verbose
```

**Tag-based filtering:**
```bash
python -m src.main --tags ucof,3ds,sca,partial
```

**Combined options:**
```bash
python -m src.main --tests smoke_tests.csv --threads 5 --tags ucof,partial --verbose
```

### Feature-Specific Testing

**Test Card-on-File scenarios:**
```bash
python -m src.main --tags ucof
```

**Test 3D Secure authentication:**
```bash
python -m src.main --tags 3ds
```

**Test SCA exemption scenarios:**
```bash
python -m src.main --tags sca
```

**Test partial operations:**
```bash
python -m src.main --tags partial
```

**Test merchant data integration:**
```bash
python -m src.main --tags merchant
```

**Test brand selection:**
```bash
python -m src.main --tags brand
```

**Test Address Verification:**
```bash
python -m src.main --tags avs
```

**Test Network Token payments:**
```bash
python -m src.main --tags applepay,googlepay
```

## How It Works

### 1. Test Chain Execution

The framework organizes tests into **chains** - sequences of related API calls that depend on each other:

```
Chain Example:
1. create_payment  → generates payment_id and scheme_transaction_id
2. increment_payment → uses payment_id from step 1
3. capture_payment → uses payment_id from step 1  
4. refund_payment  → uses payment_id, generates refund_id
5. get_refund      → uses refund_id from step 4

UCOF Chain Example:
1. create_payment (initial COF) → generates payment_id and scheme_transaction_id
2. create_payment (subsequent COF) → uses scheme_transaction_id from step 1

Partial Operations Chain Example:
1. create_payment (pre-auth) → generates payment_id
2. capture_payment (partial 1) → uses payment_id, is_final=false, sequence=1
3. capture_payment (partial 2) → uses payment_id, is_final=false, sequence=2
4. capture_payment (final) → uses payment_id, is_final=true, sequence=3
5. reverse_authorization (partial) → uses payment_id, with specific amount
```

### 2. Advanced Payment Feature Integration

The framework seamlessly integrates advanced payment features:

**Card-on-File (UCOF):**
- Initial transactions set up future Card-on-File usage
- Subsequent transactions automatically reference initial scheme transaction IDs
- Supports both Cardholder Initiated (CIT) and Merchant Initiated (MIT) transactions

**3D Secure Authentication:**
- Applies 3D Secure authentication data to payment requests
- Supports full authentication and attempted authentication scenarios
- Integrates with eCommerce data for comprehensive security testing

**SCA Exemptions:**
- Supports European SCA compliance exemption requests
- Handles exemption-only scenarios (no 3DS data required)
- Combines 3DS authentication with exemption requests
- Supports all exemption types: LOW_VALUE_PAYMENT, TRANSACTION_RISK_ANALYSIS, etc.

**Merchant Data:**
- Comprehensive merchant information integration
- Merchant Category Code (MCC) classification
- Complete address and location data
- Applied across all card-based endpoints

**Partial Operations:**
- Partial capture control with `isFinal` flag
- Capture sequence numbering for multiple partial captures
- Partial authorization reversals with specific amounts
- Smart full vs. partial operation handling

**Brand Selection:**
- Payment brand selection control (CARDHOLDER/MERCHANT)
- Applied across payment, refund, verification, and inquiry operations
- Merchant-controlled vs. cardholder-controlled brand selection

**Network Token Payments:**
- Supports Apple Pay, Google Pay, and other network tokenization
- Applies wallet-specific cryptogram and ECI data
- Handles tokenized payment flows end-to-end

**Address Verification Service (AVS):**
- Applies cardholder address data to payment requests
- Tests various address matching scenarios
- Validates AVS results in response assertions

### 3. Dependency Management

- Each chain maintains `previous_outputs` to pass IDs between steps
- Scheme transaction IDs are tracked for Card-on-File chains
- If a required dependency is missing, the step is skipped with an error
- Chains are independent - one chain's failure doesn't affect others
- Advanced features automatically handle complex dependencies
- Partial operations maintain sequence state across captures

### 4. Comprehensive Assertion Engine

Every API call undergoes comprehensive validation:

- HTTP status code validation
- Business response code assertions  
- Amount validation (including totalAuthorizedAmount)
- Card security result validation (CVV checks)
- Address verification result validation
- Custom business logic assertions
- Partial operation sequence validation

### 5. Result Collection

Every API call generates a detailed result record containing:

- Request and response JSON bodies with advanced payment data
- HTTP status codes and business status
- Execution duration in milliseconds
- Comprehensive assertion results and details
- Advanced payment feature application logs
- API property enhancement details
- Trace IDs for debugging
- Error details and structured error parsing

### 6. Output

Results are saved to:

- `outputs/results.csv` - CSV format with assertion details for analysis
- `outputs/local.db` - SQLite database for querying historical results
- Console output with real-time progress and feature application logs

## Configuration Files

The framework uses CSV files in the `/config` directory:

| File | Purpose | Required Fields |
|------|---------|----------------|
| `secrets.csv` | API credentials (secure) | `env`, `client_id`, `client_secret` |
| `environments.csv` | API environments | `env`, `endpoint_host`, `authorization_type` |
| `merchants.csv` | Merchant configurations | `merchant`, `env`, `acquirer_id`, `merchant_id` |
| `cards.csv` | Test card data | `card_id`, `card_number`, `expiry_date`, `card_brand` |
| `address.csv` | Address data for AVS | `address_id`, `cardholder_address`, `cardholder_postal_code` |
| `networktoken.csv` | Network tokenization data | `networktoken_id`, `wallet_id`, `network_token_cryptogram` |
| `threeddata.csv` | 3D Secure & SCA exemptions | `three_d_id`, `three_d_secure_type`, `sca_exemption_requested` |
| `cardonfile.csv` | Card-on-File configurations | `card_on_file_id`, `is_initial_transaction`, `transaction_type` |
| `merchantdata.csv` | Merchant information | `merchant_id`, `merchant_category_code`, `name` |

### Test Definition Structure

**Core Test Fields:**
- `chain_id` - Groups related API calls
- `step_order` - Execution sequence within chain
- `call_type` - API endpoint to call
- `test_id` - Unique identifier for this test step
- `tags` - Comma-separated tags for filtering

**Advanced Payment Feature Fields:**
- `address_data` - Reference to address.csv for AVS testing
- `threed_secure_data` - Reference to threeddata.csv for 3D Secure & SCA exemptions
- `network_token_data` - Reference to networktoken.csv for tokenized payments
- `card_on_file_data` - Reference to cardonfile.csv for UCOF scenarios
- `merchant_data` - Reference to merchantdata.csv for merchant information

**API Property Fields:**
- `brand_selector` - Payment brand selection (CARDHOLDER, MERCHANT)
- `is_final` - Final capture flag for partial captures (true, false)
- `capture_sequence_number` - Sequence number for partial captures (1, 2, 3...)
- `defer_execution` - Defer test execution (for complex scenarios)

**DCC Fields:**
- `use_dcc` - Enable Dynamic Currency Conversion
- `dcc_target_currency` - Target currency for conversion

**Assertion Fields:**
- `expected_http_status` - Expected HTTP response code
- `expected_response_code` - Expected API response code
- `expected_total_auth_amount` - Expected authorization amount
- `expected_card_security_result` - Expected CVV result
- `expected_avs_result` - Expected AVS result

**Supported Call Types:**
- `create_payment` - Create a new payment
- `capture_payment` - Capture a payment (supports partial captures)
- `increment_payment` - Increment payment authorization
- `refund_payment` - Refund a payment
- `standalone_refund` - Standalone refund operation
- `reverse_authorization` - Reverse authorization (supports partial reversals)
- `reverse_refund_authorization` - Reverse refund authorization
- `account_verification` - Verify account without payment
- `balance_inquiry` - Check account balance
- `capture_refund` - Capture a refund
- `technical_reversal` - Technical reversal operation
- `get_payment` - Retrieve payment status
- `get_refund` - Retrieve refund status
- `get_dcc_rate` - Get DCC exchange rates
- `ping` - Health check endpoint

## Advanced Payment Features

### Card-on-File (UCOF) Testing

**Initial COF Transaction:**
```csv
chain_id,step_order,call_type,test_id,tags,card_on_file_data,expected_http_status
ucof_chain,1,create_payment,INITIAL_COF,ucof,FIRSTUCOF-CIT,201
```

**Subsequent COF Transaction:**
```csv
chain_id,step_order,call_type,test_id,tags,card_on_file_data,expected_http_status
ucof_chain,2,create_payment,SUBSEQUENT_COF,ucof,SUBSEQUENTUCOF-CIT,201
```

The framework automatically:
- Extracts `schemeTransactionId` from initial COF responses
- Links subsequent transactions via `initialSchemeTransactionId`
- Handles both CIT and MIT transaction flows

### 3D Secure Integration

**3D Secure Authentication:**
```csv
chain_id,step_order,call_type,test_id,tags,threed_secure_data,cardholder_verification_method
3ds_chain,1,create_payment,3DS_AUTH,3ds,VISA_FULL,THREE_DS
```

**Features:**
- Full authentication and attempted authentication
- Version 2.2.0 compliance
- Card brand specific configurations

### Network Token Payments

**Apple Pay Transaction:**
```csv
chain_id,step_order,call_type,test_id,tags,network_token_data
applepay_chain,1,create_payment,APPLEPAY_001,applepay,APPLE_PAY_VISA
```

**Google Pay Transaction:**
```csv
chain_id,step_order,call_type,test_id,tags,network_token_data
googlepay_chain,1,create_payment,GOOGLEPAY_001,googlepay,GOOGLE_PAY_VISA
```

### Address Verification Service (AVS)

**AVS Testing:**
```csv
chain_id,step_order,call_type,test_id,tags,address_data,expected_avs_result
avs_chain,1,create_payment,AVS_MATCH,avs,AVS_FULL,MATCH
avs_chain,2,create_payment,AVS_NOMATCH,avs,AVS_NOMATCH,NO_MATCH
```

## API Properties and Enhancements

### SCA Exemption Support

**Exemption-Only Scenarios (No 3DS):**
```csv
chain_id,step_order,call_type,test_id,tags,threed_secure_data,expected_http_status
sca_lvp_chain,1,create_payment,LVP_PAY,sca,LVP_NO3DS,201
sca_tra_chain,1,create_payment,TRA_PAY,sca,TRA_NO3DS,201
```

**Combined 3DS + Exemption:**
```csv
chain_id,step_order,call_type,test_id,tags,threed_secure_data,expected_http_status
sca_delegation_chain,1,create_payment,3DS_DELEGATION,sca,VISA_FULL_DELEGATION,201
```

**Supported Exemption Types:**
- `LOW_VALUE_PAYMENT` - For transactions under €30
- `TRANSACTION_RISK_ANALYSIS` - Based on fraud risk assessment
- `TRUSTED_BENEFICIARY` - Whitelisted merchant scenarios
- `SECURE_CORPORATE_PAYMENT` - Corporate payment exemptions
- `SCA_DELEGATION` - SCA handling delegated to issuer

### Merchant Data Integration

**Merchant Information:**
```csv
chain_id,step_order,call_type,test_id,tags,merchant_data,expected_http_status
merchant_chain,1,create_payment,MERCH_PAY,merchant,RESTAURANT_EU,201
merchant_chain,2,standalone_refund,MERCH_REF,merchant,RESTAURANT_EU,201
merchant_chain,3,account_verification,MERCH_VERIFY,merchant,DEFAULT_MERCHANT,201
```

**Supported Endpoints:**
- `create_payment` - Payment creation with merchant data
- `standalone_refund` - Standalone refunds with merchant context
- `account_verification` - Account verification with merchant information
- `balance_inquiry` - Balance inquiries with merchant data

### Brand Selection Control

**Merchant-Controlled Brand Selection:**
```csv
chain_id,step_order,call_type,test_id,tags,brand_selector,expected_http_status
brand_chain,1,create_payment,MERCHANT_BRAND,brand,MERCHANT,201
brand_chain,2,standalone_refund,MERCHANT_REF,brand,MERCHANT,201
```

**Cardholder-Controlled Brand Selection:**
```csv
chain_id,step_order,call_type,test_id,tags,brand_selector,expected_http_status
brand_chain,3,create_payment,CARDHOLDER_BRAND,brand,CARDHOLDER,201
brand_chain,4,account_verification,CARDHOLDER_VERIFY,brand,CARDHOLDER,201
```

### Partial Operations

**Partial Capture Workflow:**
```csv
chain_id,step_order,call_type,test_id,tags,amount,currency,authorization_type,capture_immediately,is_final,capture_sequence_number,expected_http_status
partial_chain,1,create_payment,PARTIAL_AUTH,partial,1000,EUR,PRE_AUTHORIZATION,FALSE,,,201
partial_chain,2,capture_payment,PARTIAL_CAP1,partial,300,EUR,,,false,1,201
partial_chain,3,capture_payment,PARTIAL_CAP2,partial,400,EUR,,,false,2,201
partial_chain,4,capture_payment,PARTIAL_CAP3,partial,300,EUR,,,true,3,201
```

**Partial Authorization Reversal:**
```csv
chain_id,step_order,call_type,test_id,tags,amount,currency,expected_http_status
partial_chain,5,reverse_authorization,PARTIAL_REV,partial,100,EUR,201
```

**Key Features:**
- `is_final` flag controls whether capture is final or allows further captures
- `capture_sequence_number` provides ordering for multiple partial captures
- Partial reversals specify exact amount to reverse
- Full reversals omit amount (reverses entire authorized amount)

## Threading Behavior

### Sequential Execution (--threads 1)

- Chains execute one after another
- Predictable execution order
- Easier debugging of advanced payment features and API properties
- Lower resource usage
- Ideal for Card-on-File chain debugging and partial operations testing

### Parallel Execution (--threads N)

- Multiple chains run simultaneously
- Faster overall execution
- Thread-safe result collection
- Steps within each chain remain sequential
- Advanced payment feature application remains thread-safe
- API property enhancements work correctly across threads

> **ℹ️ Thread Safety:** The framework uses thread-local storage and locks for trace IDs, HTTP status codes, advanced payment feature application, and API property handling, ensuring proper isolation between parallel chains.

## Tag-Based Filtering

Use tags to run specific subsets of tests:

### Common Tags

- `smoke` - Quick validation tests
- `regression` - Comprehensive test scenarios
- `ucof` - Card-on-File scenarios
- `3ds` - 3D Secure authentication tests
- `sca` - SCA exemption scenarios
- `partial` - Partial operation tests (captures, reversals)
- `merchant` - Merchant data integration tests
- `brand` - Brand selection tests
- `avs` - Address verification tests
- `applepay`, `googlepay` - Network token payments
- `visa`, `mastercard` - Card brand specific tests
- `basic` - Basic payment flows

### Tag Usage Examples

```bash
# Run only smoke tests
python -m src.main --tags smoke

# Run Card-on-File and 3D Secure tests
python -m src.main --tags ucof,3ds

# Run SCA exemption scenarios
python -m src.main --tags sca

# Run partial operations tests
python -m src.main --tags partial

# Run merchant data tests
python -m src.main --tags merchant

# Run brand selection tests
python -m src.main --tags brand

# Run all network token tests
python -m src.main --tags applepay,googlepay

# Combine multiple feature tests
python -m src.main --tags "partial,sca,merchant"

# Combine with other options
python -m src.main --tags regression --threads 3 --verbose
```

## Error Handling

The framework handles several types of errors gracefully:

1. **Dependency Errors**: Missing payment_id or refund_id - step skipped with clear error message
2. **Feature Configuration Errors**: Missing Card-on-File, 3DS, SCA exemption, or merchant data configurations
3. **API Property Errors**: Invalid partial operation sequences, invalid brand selector values
4. **API Errors**: HTTP errors from Worldline API - captured with full error details
5. **Configuration Errors**: Missing merchants, cards, or environments - chain fails with descriptive error
6. **Network Errors**: Connection issues - retry behavior depends on SDK configuration
7. **Assertion Failures**: Business logic validation failures with detailed assertion results

### Advanced Feature Error Handling

- **Card-on-File Errors**: Missing COF configurations, invalid scheme transaction IDs
- **3D Secure Errors**: Invalid authentication data, missing 3DS configurations
- **SCA Exemption Errors**: Invalid exemption types, conflicting 3DS/exemption configurations
- **Merchant Data Errors**: Missing merchant configurations, invalid MCC codes
- **Partial Operation Errors**: Invalid sequence numbers, conflicting `is_final` flags
- **Brand Selection Errors**: Invalid brand selector values, unsupported endpoints
- **Network Token Errors**: Invalid cryptograms, unsupported wallet types
- **AVS Errors**: Missing address configurations, invalid address formats

## Output Format

### CSV Results (outputs/results.csv)

Key columns in the results:

**Core Test Data:**
- `chain_id`, `step_order`, `call_type`, `test_id`, `tags`
- `pass` - Boolean success indicator (includes assertion results)
- `assertion_message` - Summary of all assertion results
- `assertion_details` - Detailed assertion breakdown

**Transaction Data:**
- `transaction_id` - Payment ID, refund ID, etc.
- `payment_id`, `refund_id` - Specific transaction identifiers
- `response_status` - Business status (AUTHORIZED, CAPTURED, etc.)
- `http_status` - HTTP response code (200, 201, 400, etc.)

**Performance Data:**
- `duration_ms` - Execution time in milliseconds
- `timestamp` - Execution timestamp

**Advanced Payment Data:**
- Card description and advanced payment feature application
- Request and response JSON with advanced payment data
- Scheme transaction ID for Card-on-File tracking
- API property enhancement details (partial operations, SCA exemptions, etc.)
- Merchant data application logs
- Brand selection application details

**Error Data:**
- `error_message`, `error_type`, `error_details` - Structured error information

### Assertion Results Format

```json
{
  "HTTP status: 201": {"expected": 201, "actual": 201, "status": "PASS"},
  "responseCode: 0": {"expected": "0", "actual": "0", "status": "PASS"},
  "totalAuthorizationAmount: 1000": {"expected": "1000", "actual": "1000", "status": "PASS"},
  "cardSecurityResult: MATCH": {"expected": "MATCH", "actual": "MATCH", "status": "PASS"},
  "addressVerificationResult: MATCH": {"expected": "MATCH", "actual": "NO_MATCH", "status": "FAIL"},
  "partialCaptureSequence: 1": {"expected": "1", "actual": "1", "status": "PASS"},
  "scaExemptionApplied: LOW_VALUE_PAYMENT": {"expected": "LOW_VALUE_PAYMENT", "actual": "LOW_VALUE_PAYMENT", "status": "PASS"}
}
```

### Database Storage

SQLite database at `outputs/local.db` with table `results` containing all result data. Query examples:

```sql
-- Failed transactions with assertion details
SELECT test_id, assertion_message FROM results WHERE pass = 0;

-- Average response times by call type
SELECT call_type, AVG(duration_ms) FROM results GROUP BY call_type;

-- Card-on-File test results
SELECT test_id, pass, assertion_message FROM results WHERE tags LIKE '%ucof%';

-- SCA exemption test results
SELECT test_id, pass, assertion_message FROM results WHERE tags LIKE '%sca%';

-- Partial operation test results
SELECT test_id, pass, assertion_message FROM results WHERE tags LIKE '%partial%';

-- Merchant data test results
SELECT test_id, pass, assertion_message FROM results WHERE tags LIKE '%merchant%';

-- Advanced payment feature usage
SELECT test_id, card_description FROM results WHERE card_description LIKE '%COF%' OR card_description LIKE '%3DS%';
```

## Best Practices

### General Testing

1. **Start Sequential**: Begin with `--threads 1` for debugging, then scale up
2. **Use Tags**: Organize tests with meaningful tags for targeted execution
3. **Monitor Assertions**: Check assertion results for business logic validation
4. **Environment Separation**: Use different test files for different environments

### Advanced Payment Features

5. **UCOF Testing**: Test both initial and subsequent Card-on-File scenarios
6. **3DS Integration**: Verify both successful and attempted authentication
7. **SCA Compliance**: Test exemption-only scenarios and combined 3DS+exemption flows
8. **Network Tokens**: Test different wallet types and card brands
9. **AVS Validation**: Test various address matching scenarios

### API Properties and Enhancements

10. **Partial Operations**: Test complete partial capture workflows with proper sequencing
11. **Merchant Data**: Verify merchant information across all supported endpoints
12. **Brand Selection**: Test both merchant and cardholder-controlled scenarios
13. **Exemption Scenarios**: Test all SCA exemption types for compliance coverage

### Performance and Monitoring

14. **Monitor Results**: Check `pass` rate and `duration_ms` for performance insights
15. **Use Trace IDs**: Include trace IDs in support requests for faster debugging
16. **Assertion Analysis**: Review assertion details for specific failure patterns
17. **Error Categorization**: Analyze error types for systematic issues

### Configuration Management

18. **Feature Configuration**: Keep advanced payment configurations organized by feature
19. **API Property Management**: Maintain consistent API property usage across test scenarios
20. **Data Consistency**: Ensure test data relationships are maintained across files
21. **Version Control**: Track configuration changes for advanced payment features and API properties

## Troubleshooting

### Common Issues

#### "payment_id not set for call_type"
**Solution:** Ensure previous `create_payment` step succeeded  
**Check:** Previous step's `pass` field should be `True`

#### "Environment X not defined"
**Solution:** Add missing environment to `environments.csv`  
**Check:** `env` values in test files match `environments.csv`

#### "Merchant Y not defined"
**Solution:** Add merchant configuration to `merchants.csv`  
**Check:** Merchant exists for the specified environment

#### "secrets.csv not found"
**Solution:** Copy credentials template and add your credentials  
**Check:** `cp config/credentials/secrets.csv.template config/credentials/secrets.csv`

#### "Card-on-file ID not found"
**Solution:** Add missing COF configuration to `cardonfile.csv`  
**Check:** Referenced COF IDs exist in configuration

#### "Merchant data ID not found"
**Solution:** Add missing merchant data to `merchantdata.csv`  
**Check:** Referenced merchant IDs exist in configuration

#### Import/Module Errors
**Solution:** Run from project root: `python -m src.main`  
**Check:** Virtual environment is activated with all dependencies

### Advanced Feature Issues

#### "No scheme transaction ID found in response"
**Cause:** API response doesn't contain scheme transaction ID (common in test environments)  
**Solution:** Check if using test cards that authorize successfully

#### "3D Secure authentication data not applied"
**Cause:** Missing or invalid 3DS configuration  
**Solution:** Verify threeddata.csv contains referenced 3DS IDs

#### "SCA exemption not applied"
**Cause:** Missing or invalid SCA exemption configuration  
**Solution:** Verify threeddata.csv contains proper `sca_exemption_requested` values

#### "Address verification data not found"
**Cause:** Missing AVS configuration  
**Solution:** Verify address.csv contains referenced address IDs

#### "Merchant data not applied"
**Cause:** Missing merchant data configuration  
**Solution:** Verify merchantdata.csv contains referenced merchant IDs

#### "Invalid partial operation sequence"
**Cause:** Incorrect `is_final` flag or `capture_sequence_number` usage  
**Solution:** Review partial capture workflow and sequence numbering

#### "Brand selector not applied"
**Cause:** Invalid brand selector value or unsupported endpoint  
**Solution:** Verify `brand_selector` is CARDHOLDER or MERCHANT for supported endpoints

#### "Network token configuration not found"
**Cause:** Missing network token configuration  
**Solution:** Verify networktoken.csv contains referenced token IDs

#### Assertion Failures
**Cause:** Business logic not matching expected values  
**Solution:** Review assertion_details for specific failure reasons

### Performance Tuning

- **Threading**: Start with 3-5 threads, monitor resource usage
- **Batch Size**: Split large test files into smaller batches for better control
- **Timeout Settings**: Adjust SDK timeouts in `environments.csv`
- **Database**: Use SQLite for analysis, CSV for data exchange
- **Tag Filtering**: Use tags to run specific test subsets for faster feedback

### Debugging Advanced Features

```bash
# Debug Card-on-File with verbose output
python -m src.main --tags ucof --verbose

# Debug SCA exemptions
python -m src.main --tags sca --verbose

# Debug partial operations
python -m src.main --tags partial --verbose

# Debug merchant data
python -m src.main --tags merchant --verbose

# Debug brand selection
python -m src.main --tags brand --verbose

# Debug specific feature combinations
python -m src.main --tags "ucof,3ds,sca" --threads 1 --verbose

# Debug assertion failures
python -m src.main --tags smoke --verbose
```

### Feature-Specific Debugging

**Card-on-File Issues:**
- Check cardonfile.csv configuration
- Verify scheme transaction ID extraction
- Review previous_outputs tracking

**3D Secure Issues:**
- Verify threeddata.csv configuration  
- Check authentication value format
- Review eCommerce data application

**SCA Exemption Issues:**
- Verify threeddata.csv `sca_exemption_requested` column
- Check exemption type validity
- Review exemption-only vs. combined scenarios

**Merchant Data Issues:**
- Verify merchantdata.csv configuration
- Check merchant category code (MCC) validity
- Review merchant data application across endpoints

**Partial Operation Issues:**
- Verify `is_final` flag usage
- Check `capture_sequence_number` ordering
- Review partial vs. full operation logic

**Brand Selection Issues:**
- Verify `brand_selector` values (CARDHOLDER/MERCHANT)
- Check endpoint support for brand selection
- Review brand selector application

**Network Token Issues:**
- Verify networktoken.csv configuration
- Check cryptogram format and ECI values
- Review wallet ID mappings

**AVS Issues:**
- Verify address.csv configuration
- Check address format requirements
- Review postal code formats

The Payment API Testing Framework provides comprehensive testing capabilities for modern payment scenarios with full support for advanced payment features, API property enhancements, and detailed validation. Use this guide to maximize the framework's potential for your payment testing needs, including the latest SCA compliance, merchant data integration, partial operations, and brand selection capabilities.