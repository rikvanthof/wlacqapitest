# Command Line Interface Reference

## Synopsis

```bash
python -m src.main [OPTIONS]
```

## Description

Execute payment API test chains with configurable parallelism, test files, and advanced filtering. Supports comprehensive payment features including Card-on-File, 3D Secure, Network Tokens, Address Verification, SCA Exemptions, Merchant Data, Partial Operations, and Brand Selection.

## Options

### `--threads`, `-t`

**Type:** Integer  
**Default:** `1`  
**Description:** Number of parallel threads for chain execution

```bash
# Sequential execution (default)
python -m src.main --threads 1

# Parallel execution with 3 threads
python -m src.main --threads 3

# Maximum parallelism (use with caution)
python -m src.main --threads 10
```

**Notes:**
- `--threads 1` = Sequential execution (chains run one after another)
- `--threads N` = Parallel execution (up to N chains run simultaneously)
- Steps within each chain always execute sequentially
- Higher thread counts may hit API rate limits
- Partial operations and SCA exemptions work correctly across all thread counts

### `--tests`, `-f`

**Type:** String (file path)  
**Default:** `config/tests.csv`  
**Description:** Path to the test CSV file

```bash
# Use default test file
python -m src.main

# Use custom test file
python -m src.main --tests smoke_tests.csv

# Use test file from test_suites directory
python -m src.main --tests config/test_suites/regression.csv
```

**File Format Requirements:**
- Must be valid CSV with headers
- Required columns: `chain_id`, `step_order`, `call_type`, `test_id`
- Must be sorted by `chain_id` and `step_order`
- Supports advanced payment features and API properties via optional columns

### `--tags`

**Type:** String (comma-separated)  
**Default:** All tests  
**Description:** Filter tests by tags for targeted execution

```bash
# Run only Card-on-File tests
python -m src.main --tags ucof

# Run SCA exemption scenarios
python -m src.main --tags sca

# Run partial operations tests
python -m src.main --tags partial

# Run merchant data integration tests
python -m src.main --tags merchant

# Run brand selection tests
python -m src.main --tags brand

# Run 3D Secure and Network Token tests
python -m src.main --tags 3ds,applepay

# Multiple feature testing
python -m src.main --tags sca,partial,merchant
```

**Available Tags:**
- `ucof` - Card-on-File scenarios
- `3ds` - 3D Secure authentication
- `sca` - SCA exemption scenarios (LOW_VALUE_PAYMENT, TRANSACTION_RISK_ANALYSIS, etc.)
- `partial` - Partial operation tests (captures, reversals)
- `merchant` - Merchant data integration tests
- `brand` - Brand selection tests (CARDHOLDER/MERCHANT)
- `avs` - Address verification
- `applepay`, `googlepay` - Network token payments
- `visa`, `mastercard` - Card brand specific
- `smoke`, `regression` - Test type classification

### `--verbose`, `-v`

**Type:** Flag (no value)  
**Default:** `False`  
**Description:** Enable verbose output for debugging

```bash
# Standard output
python -m src.main

# Verbose output
python -m src.main --verbose
```

**Verbose Output Includes:**
- Step-by-step chain execution progress
- Advanced payment feature application (AVS, 3DS, SCA exemptions, merchant data)
- API property enhancement details (partial operations, brand selection)
- Detailed API call information
- Request/response debugging details
- Thread execution status
- Card-on-File data application
- Scheme transaction ID tracking

## Examples

### Basic Usage

```bash
# Run all tests sequentially with default settings
python -m src.main

# Run tests in parallel with 3 threads
python -m src.main --threads 3
```

### Test Suite Execution

```bash
# Smoke test suite
python -m src.main --tests smoke_tests.csv

# Regression test suite with parallelism
python -m src.main --tests regression.csv --threads 5

# UCOF-specific testing
python -m src.main --tests ucof_tests.csv --verbose
```

### Feature-Specific Testing

```bash
# Test only Card-on-File scenarios
python -m src.main --tags ucof

# Test SCA exemption scenarios
python -m src.main --tags sca --verbose

# Test partial operations
python -m src.main --tags partial --verbose

# Test merchant data integration
python -m src.main --tags merchant

# Test brand selection
python -m src.main --tags brand

# Test 3D Secure flows
python -m src.main --tags 3ds --verbose

# Test Network Token payments
python -m src.main --tags applepay,googlepay

# Combined feature testing
python -m src.main --tags sca,partial,merchant --threads 2
```

### API Property Enhancement Testing

```bash
# Test SCA compliance scenarios
python -m src.main --tags sca --verbose

# Test partial capture workflows
python -m src.main --tags partial --threads 2

# Test merchant data across endpoints
python -m src.main --tags merchant --verbose

# Test brand selection control
python -m src.main --tags brand

# Combined API property testing
python -m src.main --tags "partial,sca,brand" --threads 3
```

### Development & Debugging

```bash
# Debug single-threaded execution
python -m src.main --verbose

# Debug specific payment features
python -m src.main --tags avs --verbose

# Debug new API properties
python -m src.main --tags "sca,partial" --verbose --threads 1

# Performance testing with high parallelism
python -m src.main --tests load_test.csv --threads 8
```

### Production Usage

```bash
# Scheduled regression testing
python -m src.main --tests nightly_regression.csv --threads 5

# Environment validation
python -m src.main --tags smoke --threads 2

# Compliance testing (SCA exemptions)
python -m src.main --tags sca --threads 3

# Card-on-File validation
python -m src.main --tags ucof --threads 3

# Partial operations validation
python -m src.main --tags partial --threads 2
```

## Advanced Features

### Chain Execution

The framework supports complex payment scenarios through chained execution:

```bash
# Execute multi-step payment chains
python -m src.main --tests payment_chains.csv --verbose
```

**Chain Features:**
- Initial Card-on-File followed by subsequent transactions
- Authorization → Increment → Capture flows with partial operations
- Payment → Refund scenarios
- Partial capture sequences with `isFinal` flag control
- SCA exemption handling across chain steps
- Automatic dependency tracking

### Payment Feature Support

```bash
# Test Address Verification (AVS)
python -m src.main --tags avs

# Test 3D Secure authentication
python -m src.main --tags 3ds

# Test SCA exemption scenarios
python -m src.main --tags sca

# Test Apple Pay / Google Pay
python -m src.main --tags applepay,googlepay

# Test Card-on-File scenarios
python -m src.main --tags ucof

# Test partial operations
python -m src.main --tags partial

# Test merchant data integration
python -m src.main --tags merchant

# Test brand selection
python -m src.main --tags brand
```

### API Property Enhancement Support

```bash
# Test partial capture workflows
python -m src.main --tags partial --verbose

# Test SCA compliance
python -m src.main --tags sca --verbose

# Test merchant data across endpoints
python -m src.main --tags merchant --verbose

# Test brand selection control
python -m src.main --tags brand --verbose
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all tests completed (may include failed API calls) |
| 1 | Error - configuration issue, file not found, or system error |

> **Note:** The exit code indicates whether the test *execution* succeeded, not whether all API calls passed. Check the results CSV or console output for API call success rates.

## Environment Variables

Currently, the framework doesn't use environment variables. All configuration is file-based through CSV files in the `/config` directory:

- `config/static/` - Static configuration files
- `config/test_suites/` - Test scenario definitions

## Output Files

Every execution creates/updates:

- `outputs/results.csv` - Latest test results with comprehensive assertions
- `outputs/local.db` - SQLite database with all historical results
- Console logs - Real-time execution feedback

## Configuration Files

### Required Configuration Files

| File | Purpose |
|------|---------|
| `environments.csv` | API endpoints and credentials |
| `cards.csv` | Test card configurations |
| `merchants.csv` | Merchant account details |

### Optional Configuration Files

| File | Purpose |
|------|---------|
| `address.csv` | AVS test addresses |
| `networktokens.csv` | Apple Pay/Google Pay tokens |
| `threeddata.csv` | 3D Secure test data & SCA exemptions |
| `cardonfile.csv` | Card-on-File configurations |
| `merchantdata.csv` | Merchant information data |

## Performance Considerations

### Thread Count Recommendations

| Test Scenario | Recommended Threads | Rationale |
|---------------|-------------------|-----------|
| Development/Debugging | 1 | Easier to trace issues |
| Smoke Testing | 2-3 | Fast feedback, low load |
| Regression Testing | 3-5 | Balanced speed/stability |
| Load Testing | 5-10 | Maximum throughput |
| Card-on-File Testing | 2-3 | Chain dependencies require careful timing |
| Partial Operations Testing | 2-4 | Sequence dependencies need coordination |
| SCA Exemption Testing | 3-5 | Independent exemption scenarios |

### Memory Usage

- Each thread requires ~10-50MB depending on test complexity
- Large test files increase memory usage regardless of thread count
- Advanced payment features (3DS, Network Tokens, SCA exemptions) may increase memory usage
- API property enhancements (partial operations, merchant data) add minimal overhead
- Monitor system resources when using high thread counts

### API Rate Limits

- Worldline APIs may have rate limiting
- Higher thread counts may trigger rate limits
- Use `--verbose` to monitor for HTTP 429 responses
- Reduce thread count if rate limiting occurs
- Card-on-File testing may have additional rate considerations
- Partial operations and SCA exemptions respect API rate limits

## Troubleshooting

### Common Issues

**Configuration Errors:**
```bash
# Verify configuration loading
python -m src.main --verbose --tags smoke
```

**Rate Limiting:**
```bash
# Reduce parallelism
python -m src.main --threads 1 --verbose
```

**Feature-Specific Issues:**
```bash
# Test individual features
python -m src.main --tags 3ds --verbose
python -m src.main --tags ucof --verbose
python -m src.main --tags sca --verbose
python -m src.main --tags partial --verbose
python -m src.main --tags merchant --verbose
python -m src.main --tags brand --verbose
```

**API Property Issues:**
```bash
# Test specific API properties
python -m src.main --tags "partial,sca" --threads 1 --verbose
python -m src.main --tags "merchant,brand" --verbose
```

### Debug Mode

For comprehensive debugging:
```bash
python -m src.main --tests debug.csv --verbose --threads 1
```

This enables:
- Detailed request/response logging
- Step-by-step execution tracking
- Advanced payment feature application logs
- API property enhancement details
- Chain dependency resolution details
- SCA exemption application logs
- Merchant data integration details
- Partial operation sequence tracking

### Feature-Specific Debugging

```bash
# Debug SCA exemption scenarios
python -m src.main --tags sca --verbose --threads 1

# Debug partial operations
python -m src.main --tags partial --verbose --threads 1

# Debug merchant data integration
python -m src.main --tags merchant --verbose

# Debug brand selection
python -m src.main --tags brand --verbose

# Debug combined features
python -m src.main --tags "sca,partial,merchant" --verbose --threads 1
```
```

**Key Updates Made:**
1. ✅ **Added new tags**: `sca`, `partial`, `merchant`, `brand`
2. ✅ **Added merchantdata.csv** to optional configuration files
3. ✅ **Updated examples** with v2.2.0 features
4. ✅ **Enhanced verbose output** description
5. ✅ **Added API property enhancement sections**
6. ✅ **Updated troubleshooting** with new feature debugging
7. ✅ **Enhanced performance considerations** for new features
8. ✅ **Updated thread recommendations** for new test types

The CLI reference now fully reflects all v2.2.0 capabilities! 🚀