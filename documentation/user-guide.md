# Payment API Testing Framework - User Guide

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Configuration Files](#configuration-files)
- [Advanced Payment Features](#advanced-payment-features)
- [Threading Behavior](#threading-behavior)
- [Tag-Based Filtering](#tag-based-filtering)
- [Error Handling](#error-handling)
- [Output Format](#output-format)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Payment API Testing Framework is a comprehensive tool for testing Worldline Acquiring API endpoints. It supports end-to-end payment scenarios with chained API calls, parallel execution, advanced payment features (Card-on-File, 3D Secure, Network Tokens, AVS), and detailed result tracking with comprehensive assertion validation.

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
python -m src.main --tags ucof,3ds
```

**Combined options:**
```bash
python -m src.main --tests regression.csv --threads 5 --tags ucof --verbose
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

### 4. Comprehensive Assertion Engine

Every API call undergoes comprehensive validation:

- HTTP status code validation
- Business response code assertions  
- Amount validation (including totalAuthorizedAmount)
- Card security result validation (CVV checks)
- Address verification result validation
- Custom business logic assertions

### 5. Result Collection

Every API call generates a detailed result record containing:

- Request and response JSON bodies with advanced payment data
- HTTP status codes and business status
- Execution duration in milliseconds
- Comprehensive assertion results and details
- Advanced payment feature application logs
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
| `tests.csv` | Test step definitions | `chain_id`, `step_order`, `call_type`, `test_id`, `tags` |
| `environments.csv` | API environments | `env`, `endpoint_host`, `client_id`, `client_secret` |
| `merchants.csv` | Merchant configurations | `merchant`, `env`, `acquirer_id`, `merchant_id` |
| `cards.csv` | Test card data | `card_id`, `card_number`, `expiry_date`, `card_brand` |
| `address.csv` | Address data for AVS | `address_id`, `cardholder_address`, `cardholder_postal_code` |
| `networktokens.csv` | Network tokenization data | `networktoken_id`, `wallet_id`, `network_token_cryptogram` |
| `threeddata.csv` | 3D Secure authentication | `three_d_id`, `three_d_secure_type`, `authentication_value` |
| `cardonfile.csv` | Card-on-File configurations | `card_on_file_id`, `is_initial_transaction`, `transaction_type` |

### Test Definition Structure

**Core Test Fields:**
- `chain_id` - Groups related API calls
- `step_order` - Execution sequence within chain
- `call_type` - API endpoint to call
- `test_id` - Unique identifier for this test step
- `tags` - Comma-separated tags for filtering

**Advanced Payment Feature Fields:**
- `address_data` - Reference to address.csv for AVS testing
- `threed_secure_data` - Reference to threeddata.csv for 3D Secure
- `network_token_data` - Reference to networktokens.csv for tokenized payments
- `card_on_file_data` - Reference to cardonfile.csv for UCOF scenarios

**Assertion Fields:**
- `expected_http_status` - Expected HTTP response code
- `expected_response_code` - Expected API response code
- `expected_total_auth_amount` - Expected authorization amount
- `expected_card_security_result` - Expected CVV result
- `expected_avs_result` - Expected AVS result

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

## Threading Behavior

### Sequential Execution (--threads 1)

- Chains execute one after another
- Predictable execution order
- Easier debugging of advanced payment features
- Lower resource usage
- Ideal for Card-on-File chain debugging

### Parallel Execution (--threads N)

- Multiple chains run simultaneously
- Faster overall execution
- Thread-safe result collection
- Steps within each chain remain sequential
- Advanced payment feature application remains thread-safe

> **ℹ️ Thread Safety:** The framework uses thread-local storage and locks for trace IDs, HTTP status codes, and advanced payment feature application, ensuring proper isolation between parallel chains.

## Tag-Based Filtering

Use tags to run specific subsets of tests:

### Common Tags

- `smoke` - Quick validation tests
- `regression` - Comprehensive test scenarios
- `ucof` - Card-on-File scenarios
- `3ds` - 3D Secure authentication tests
- `avs` - Address verification tests
- `applepay`, `googlepay` - Network token payments
- `visa`, `mastercard` - Card brand specific tests

### Tag Usage Examples

```bash
# Run only smoke tests
python -m src.main --tags smoke

# Run Card-on-File and 3D Secure tests
python -m src.main --tags ucof,3ds

# Run all network token tests
python -m src.main --tags applepay,googlepay

# Combine with other options
python -m src.main --tags regression --threads 3 --verbose
```

## Error Handling

The framework handles several types of errors gracefully:

1. **Dependency Errors**: Missing payment_id or refund_id - step skipped with clear error message
2. **Feature Configuration Errors**: Missing Card-on-File, 3DS, or other feature configurations
3. **API Errors**: HTTP errors from Worldline API - captured with full error details
4. **Configuration Errors**: Missing merchants, cards, or environments - chain fails with descriptive error
5. **Network Errors**: Connection issues - retry behavior depends on SDK configuration
6. **Assertion Failures**: Business logic validation failures with detailed assertion results

### Advanced Feature Error Handling

- **Card-on-File Errors**: Missing COF configurations, invalid scheme transaction IDs
- **3D Secure Errors**: Invalid authentication data, missing 3DS configurations
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

**Error Data:**
- `error_message`, `error_type`, `error_details` - Structured error information

### Assertion Results Format

```json
{
  "HTTP status: 201": {"expected": 201, "actual": 201, "status": "PASS"},
  "responseCode: 0": {"expected": "0", "actual": "0", "status": "PASS"},
  "totalAuthorizationAmount: 1000": {"expected": "1000", "actual": "1000", "status": "PASS"},
  "cardSecurityResult: MATCH": {"expected": "MATCH", "actual": "MATCH", "status": "PASS"},
  "addressVerificationResult: MATCH": {"expected": "MATCH", "actual": "NO_MATCH", "status": "FAIL"}
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

-- Advanced payment feature usage
SELECT test_id, card_description FROM results WHERE card_description LIKE '%COF%';
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
7. **Network Tokens**: Test different wallet types and card brands
8. **AVS Validation**: Test various address matching scenarios

### Performance and Monitoring

9. **Monitor Results**: Check `pass` rate and `duration_ms` for performance insights
10. **Use Trace IDs**: Include trace IDs in support requests for faster debugging
11. **Assertion Analysis**: Review assertion details for specific failure patterns
12. **Error Categorization**: Analyze error types for systematic issues

### Configuration Management

13. **Feature Configuration**: Keep advanced payment configurations organized by feature
14. **Data Consistency**: Ensure test data relationships are maintained across files
15. **Version Control**: Track configuration changes for advanced payment features

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

#### "Card-on-file ID not found"
**Solution:** Add missing COF configuration to `cardonfile.csv`  
**Check:** Referenced COF IDs exist in configuration

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

#### "Address verification data not found"
**Cause:** Missing AVS configuration  
**Solution:** Verify address.csv contains referenced address IDs

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

# Debug specific feature combinations
python -m src.main --tags "ucof,3ds" --threads 1 --verbose

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

**Network Token Issues:**
- Verify networktokens.csv configuration
- Check cryptogram format and ECI values
- Review wallet ID mappings

**AVS Issues:**
- Verify address.csv configuration
- Check address format requirements
- Review postal code formats

The Payment API Testing Framework provides comprehensive testing capabilities for modern payment scenarios with full support for advanced payment features and detailed validation. Use this guide to maximize the framework's potential for your payment testing needs.