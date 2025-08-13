# Unit Testing Guide

## Overview

The Payment API Testing Framework includes a comprehensive unit test suite using pytest. The test suite covers all components with 100+ tests ensuring code quality and reliability across all advanced payment features including Card-on-File, 3D Secure, Network Tokens, and Address Verification.

## Quick Start

### Run All Tests

```bash
# Run complete test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src
```

### Test Structure

```
tests/
├── conftest.py                    # pytest configuration and fixtures
├── test_data_loader.py           # Data loading functionality tests
├── test_response_utils.py         # Response processing tests
├── test_results_handler.py        # Result formatting and database tests
├── test_utils.py                 # Utility function tests
├── test_cardonfile.py            # Card-on-File feature tests
├── test_payment_assertions.py    # Assertion engine tests
└── test_request_builders/        # Request builder tests
    ├── test_capture_payment.py
    ├── test_create_payment.py
    ├── test_get_payment.py
    ├── test_get_refund.py
    ├── test_increment_payment.py
    └── test_refund_payment.py
```

## Running Test Subsets

### By Test File

```bash
# Test only data loading
pytest tests/test_data_loader.py

# Test only request builders
pytest tests/test_request_builders/

# Test specific request builder
pytest tests/test_request_builders/test_create_payment.py

# Test Card-on-File functionality
pytest tests/test_cardonfile.py

# Test assertion engine
pytest tests/test_payment_assertions.py
```

### By Test Class

```bash
# Test specific class in a file
pytest tests/test_results_handler.py::TestCreateSuccessResult

# Test specific class in request builders
pytest tests/test_request_builders/test_create_payment.py::TestBuildCreatePaymentRequest

# Test Card-on-File classes
pytest tests/test_cardonfile.py::TestApplyCardonfileData
```

### By Test Method

```bash
# Test specific method
pytest tests/test_utils.py::TestGenerateFunctions::test_generate_uuid

# Test specific request builder method
pytest tests/test_request_builders/test_create_payment.py::TestBuildCreatePaymentRequest::test_build_complete_request

# Test specific Card-on-File scenario
pytest tests/test_cardonfile.py::TestApplyCardonfileData::test_initial_cof_transaction
```

### By Pattern Matching

```bash
# Run tests matching pattern
pytest -k "test_generate"

# Run tests for specific functionality
pytest -k "create_payment"

# Run Card-on-File related tests
pytest -k "cardonfile or cof"

# Run assertion related tests
pytest -k "assertion"

# Exclude tests matching pattern
pytest -k "not slow"
```

### By Markers (if configured)

```bash
# Run only unit tests (if marked)
pytest -m unit

# Run only integration tests (if marked)
pytest -m integration

# Run feature-specific tests
pytest -m cardonfile
pytest -m threed_secure

# Skip slow tests
pytest -m "not slow"
```

## Test Categories

### 1. Data Loading Tests (test_data_loader.py)

Tests comprehensive configuration file loading including advanced payment features:

- File existence validation
- Data type conversion
- Index setting and relationships
- Sorting verification
- Advanced feature configuration loading (COF, 3DS, Network Tokens)

```bash
# Run all data loading tests
pytest tests/test_data_loader.py -v
```

**Key Test Methods:**
- `test_load_enhanced_config_success` - Successful enhanced configuration loading
- `test_load_data_file_not_found` - Missing file handling
- `test_load_data_sorting` - Test order verification
- `test_cardonfile_loading` - Card-on-File configuration loading
- `test_threed_secure_loading` - 3D Secure configuration loading

### 2. Request Builder Tests (test_request_builders/)

Tests API request object construction with advanced payment features:

- Required field validation
- Optional field handling
- Advanced payment feature integration
- Data type conversion
- Request cleaning

```bash
# Test all request builders
pytest tests/test_request_builders/ -v

# Test only create payment requests
pytest tests/test_request_builders/test_create_payment.py -v
```

**Test Coverage per Builder:**
- **Create Payment**: Complete request building, card data, Card-on-File, 3DS, AVS, Network Tokens
- **Increment Payment**: Amount handling, operation ID generation
- **Capture Payment**: Amount validation, timestamp generation
- **Refund Payment**: Optional amount handling, request cleaning
- **Get Payment/Refund**: Validation for GET requests (no request body)

**Advanced Feature Coverage:**
- Card-on-File data application (initial and subsequent)
- 3D Secure authentication data integration
- Address Verification Service (AVS) data
- Network Token payment processing

### 3. Card-on-File Tests (test_cardonfile.py)

Tests comprehensive Card-on-File (UCOF) functionality:

- Initial COF transaction handling
- Subsequent COF transaction processing
- Scheme transaction ID tracking
- Chain dependency management
- Error handling for missing configurations

```bash
# Test Card-on-File functionality
pytest tests/test_cardonfile.py -v
```

**Key Test Areas:**
- `TestApplyCardonfileData` - Core COF data application logic
- `TestInitialCofTransactions` - Initial transaction setup
- `TestSubsequentCofTransactions` - Subsequent transaction linking
- `TestCofChainExecution` - Multi-step COF scenarios
- `TestCofErrorHandling` - Missing configuration handling

### 4. Response Processing Tests (test_response_utils.py)

Tests API response handling with advanced payment features:

- Transaction ID extraction
- Scheme transaction ID tracking
- Status code processing
- Previous output updates for chains
- Card description retrieval

```bash
# Test response utilities
pytest tests/test_response_utils.py -v
```

**Key Test Areas:**
- `TestGetTransactionId` - ID extraction from different response types
- `TestGetSchemeTransactionId` - Scheme transaction ID extraction for COF
- `TestGetResponseStatus` - Status field extraction
- `TestUpdatePreviousOutputs` - Chain dependency management
- `TestGetCardDescription` - Card information retrieval

### 5. Payment Assertion Tests (test_payment_assertions.py)

Tests comprehensive response validation engine:

- HTTP status code validation
- Response code assertions
- Amount validation (including totalAuthorizedAmount)
- Card security result validation
- Address verification result validation
- Error response parsing

```bash
# Test payment assertions
pytest tests/test_payment_assertions.py -v
```

**Key Test Classes:**
- `TestPaymentAssertionEngine` - Core assertion engine functionality
- `TestAmountAssertions` - Amount validation including totalAuthorizedAmount
- `TestSecurityAssertions` - Card security and AVS result validation
- `TestErrorHandling` - Error response parsing and handling

### 6. Results Handling Tests (test_results_handler.py)

Tests result formatting and database operations:

- Success result creation with advanced payment data
- Error result creation and parsing
- Database operations and schema
- CSV export functionality

```bash
# Test results handling
pytest tests/test_results_handler.py -v
```

**Test Classes:**
- `TestCreateSuccessResult` - Successful API call result formatting
- `TestCreateErrorResult` - Failed API call result formatting
- `TestParseErrorResponse` - Error message parsing
- `TestSaveResults` - Database and CSV operations
- `TestAdvancedPaymentResults` - Results with COF, 3DS, and other features

### 7. Utility Tests (test_utils.py)

Tests utility functions and helper methods:

- Random string generation
- UUID generation
- Configuration file creation
- Request cleaning
- Advanced feature utilities

```bash
# Test utilities
pytest tests/test_utils.py -v
```

**Key Utilities Tested:**
- `generate_nonce()` - Random number generation
- `generate_random_string()` - String generation with validation
- `generate_uuid()` - UUID format validation
- `create_temp_config()` - SDK configuration file creation
- `clean_request()` - Request object cleaning and validation

## Advanced Testing Options

### Coverage Reporting

```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# Coverage with missing lines
pytest --cov=src --cov-report=term-missing

# Coverage for specific module
pytest --cov=src.request_builders tests/test_request_builders/

# Coverage for advanced features
pytest --cov=src.cardonfile tests/test_cardonfile.py
pytest --cov=src.core.payment_assertions tests/test_payment_assertions.py
```

### Parallel Test Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with specific number of workers
pytest -n 4

# Parallel execution for specific test categories
pytest tests/test_request_builders/ -n 3
```

### Output Control

```bash
# Capture output (default)
pytest

# Don't capture output (see print statements)
pytest -s

# Show local variables in tracebacks
pytest -l

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Verbose output with test names
pytest -v --tb=short
```

### Debugging Tests

```bash
# Drop into debugger on failures
pytest --pdb

# Drop into debugger immediately
pytest --pdb-trace

# Trace pytest execution
pytest --trace

# Debug specific feature tests
pytest tests/test_cardonfile.py --pdb -s
```

### Performance Testing

```bash
# Run tests with duration reporting
pytest --durations=10

# Profile test execution
pytest --profile

# Memory usage monitoring
pytest --memprof

# Test timeout configuration
pytest --timeout=300
```

## Test Fixtures

The test suite uses several fixtures defined in `conftest.py`:

### Mock Fixtures

- `mock_cards_df` - Sample card data DataFrame with various card types
- `mock_environments_df` - Sample environment configurations
- `mock_merchants_df` - Sample merchant data for different environments
- `mock_cardonfile_df` - Sample Card-on-File configurations
- `mock_threeddata_df` - Sample 3D Secure authentication data
- `mock_address_df` - Sample address data for AVS testing

### API Response Fixtures

- `mock_api_payment_response` - Sample successful payment response
- `mock_api_increment_response` - Sample increment payment response
- `mock_api_refund_response` - Sample refund response
- `mock_cof_payment_response` - Sample COF payment response with scheme transaction ID

### Configuration Fixtures

- `temp_csv_file` - Temporary CSV file creation for testing
- `mock_previous_outputs` - Previous chain outputs for dependency testing
- `sample_test_data` - Comprehensive test data for various scenarios

## Writing New Tests

### Test Naming Convention

```python
# Test classes
class TestYourFeature:
    """Test your specific feature"""
    pass

# Test methods
def test_your_specific_case(self):
    """Test specific functionality"""
    pass

# Test files
test_your_module.py
```

### Example Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from src.your_module import your_function

class TestYourFunction:
    """Test suite for your_function"""
    
    def test_successful_case(self):
        """Test the happy path"""
        result = your_function(valid_input)
        assert result == expected_output
    
    def test_error_case(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            your_function(invalid_input)
    
    @patch('src.your_module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependencies"""
        mock_dependency.return_value = mock_value
        result = your_function(input_data)
        assert result == expected_result
        mock_dependency.assert_called_once_with(expected_args)
    
    def test_advanced_payment_feature(self, mock_cardonfile_df):
        """Test with advanced payment features"""
        result = your_function(
            input_data, 
            cardonfile=mock_cardonfile_df,
            previous_outputs={'scheme_transaction_id': 'test123'}
        )
        assert result.cardonfile_applied is True
```

### Testing Advanced Payment Features

```python
class TestAdvancedPaymentFeatures:
    """Test advanced payment functionality"""
    
    def test_cardonfile_initial_transaction(self, mock_cardonfile_df):
        """Test initial Card-on-File transaction"""
        result = apply_cardonfile_data(
            request, 
            {'card_on_file_data': 'FIRSTUCOF-CIT'}, 
            mock_cardonfile_df
        )
        assert result.card_payment_data.card_on_file_data.is_initial_transaction is True
    
    def test_threed_secure_integration(self, mock_threeddata_df):
        """Test 3D Secure data application"""
        result = apply_threed_secure_data(
            request,
            {'threed_secure_data': 'VISA_FULL'},
            mock_threeddata_df
        )
        assert result.card_payment_data.ecommerce_data.three_d_secure.eci == '05'
    
    def test_assertion_engine(self):
        """Test payment assertion engine"""
        engine = PaymentAssertionEngine()
        result = engine.evaluate_payment_assertions(
            test_row, mock_response, 201, 'create_payment'
        )
        assert result.passed is True
        assert 'totalAuthorizationAmount: 1000' in result.passed_assertions
```

## Continuous Integration

The test suite is designed to run in CI environments:

```bash
# CI-friendly test run
pytest --tb=short --junit-xml=test-results.xml

# With coverage for CI
pytest --cov=src --cov-report=xml --cov-report=term

# Parallel execution in CI
pytest -n auto --dist=loadfile

# Feature-specific CI testing
pytest -m "not slow" --cov=src --junit-xml=results.xml
```

### GitHub Actions Example

```yaml
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml --junit-xml=test-results.xml
    
- name: Run advanced feature tests
  run: |
    pytest tests/test_cardonfile.py -v
    pytest tests/test_payment_assertions.py -v
```

### Coverage Targets

| Component | Target Coverage | Current Coverage |
|-----------|----------------|------------------|
| Core Framework | 95%+ | 98% |
| Request Builders | 95%+ | 97% |
| Card-on-File | 90%+ | 95% |
| Payment Assertions | 95%+ | 96% |
| Response Processing | 90%+ | 94% |
| Utilities | 85%+ | 92% |

## Test Performance Optimization

### Fast Test Execution

```bash
# Run only fast tests
pytest -m "not slow"

# Skip integration tests
pytest -m "not integration"

# Run tests in parallel
pytest -n auto

# Cache test results
pytest --cache-clear  # Clear cache
pytest                # Use cached results
```

### Memory Optimization

```bash
# Monitor memory usage
pytest --memprof

# Limit test memory usage
pytest --maxfail=1 --tb=no  # Fail fast, minimal output

# Run specific test categories
pytest tests/test_utils.py  # Lightweight tests first
```

## Troubleshooting Tests

### Common Test Issues

**Import Errors:**
```bash
# Ensure PYTHONPATH is correct
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/

# Or use pytest from project root
python -m pytest tests/
```

**Fixture Issues:**
```bash
# Debug fixture loading
pytest --fixtures tests/test_your_module.py

# Verbose fixture output
pytest tests/test_your_module.py -v -s
```

**Mock-related Issues:**
```bash
# Debug mock calls
pytest tests/test_your_module.py -v -s --tb=long
```

### Test Debugging Commands

```bash
# Debug specific test
pytest tests/test_cardonfile.py::TestApplyCardonfileData::test_initial_cof_transaction -v -s --pdb

# Run with maximum verbosity
pytest tests/test_payment_assertions.py -vvv

# Show test execution time
pytest tests/ --durations=0
```

> **✅ Test Suite Status:** All 100+ tests are currently passing, ensuring the framework's reliability and code quality across all advanced payment features including Card-on-File, 3D Secure, Network Tokens, and comprehensive assertion validation.

The test suite provides comprehensive coverage of the Payment API Testing Framework, ensuring robust functionality across all payment scenarios and advanced features.