# Developer Guide - Payment API Test Framework

## Table of Contents
- [Overview](#overview)
- [Design Principles](#design-principles)
- [Project Structure](#project-structure)
- [Core Concepts](#core-concepts)
- [Getting Started](#getting-started)
- [Adding New Endpoints](#adding-new-endpoints)
- [DCC Implementation](#dcc-implementation)
- [Testing & Debugging](#testing--debugging)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Overview

This is a Python testing framework for Worldline Acquiring payment APIs. It supports complex payment workflows including:
- Payment creation, increments, captures, and refunds
- Dynamic Currency Conversion (DCC)
- 3D Secure authentication
- Address Verification (AVS)
- Network Tokens
- Card-on-File scenarios

### Key Features
- **Chain-based testing**: Execute sequences of related API calls
- **DCC support**: Automatic currency conversion handling
- **Endpoint registry**: Modular, extensible endpoint management
- **Request builders**: Clean separation of request construction logic
- **Comprehensive logging**: Detailed execution tracking

## Design Principles

### 1. Request Builder Pattern
**Problem**: API request construction was scattered across endpoint files, making it hard to maintain and test.

**Solution**: Centralized request building in dedicated `src/request_builders/` modules.

```python
# ✅ Good: Request builder handles all construction logic
def build_create_payment_request(row, cards, dcc_context=None):
    request = ApiPaymentRequest()
    # All request construction logic here
    return request

# ✅ Good: Endpoint delegates to builder
class CreatePaymentEndpoint:
    @staticmethod
    def build_request(row, **kwargs):
        return build_create_payment_request(row, **kwargs)
```

### 2. Endpoint Registry Pattern
**Problem**: Hard-coded endpoint handling made adding new endpoints difficult.

**Solution**: Dynamic endpoint registration and lookup system.

```python
# ✅ Registration happens automatically via decorator
@register_endpoint('create_payment')
class CreatePaymentEndpoint(EndpointInterface):
    # Implementation here

# ✅ Usage is clean and consistent
endpoint = EndpointRegistry.get_endpoint('create_payment')
request = endpoint.build_request(row)
```

### 3. Separation of Concerns
- **Endpoints**: Handle API calls and basic request routing
- **Request Builders**: Construct API request objects
- **Core Managers**: Handle cross-cutting concerns (DCC, chains)
- **Utils**: Shared functionality (logging, data cleaning)

### 4. DCC Integration Pattern
DCC (Dynamic Currency Conversion) is integrated consistently across all payment endpoints:
1. **Inquiry**: Get conversion rates before main API call
2. **Context**: Store conversion data for the chain
3. **Application**: Use conversion data in request builders

## Project Structure

```
wlacqapitest/
├── src/
│   ├── core/                      # Core system components
│   │   ├── dcc_manager.py         # DCC logic and context management
│   │   ├── endpoint_registry.py   # Endpoint registration system
│   │   └── payment_assertions.py  # Response validation
│   ├── endpoints/                 # API endpoint implementations
│   │   ├── create_payment_endpoint.py
│   │   ├── capture_payment_endpoint.py
│   │   └── ...
│   ├── request_builders/          # Request construction logic
│   │   ├── create_payment.py
│   │   ├── capture_payment.py
│   │   └── ...
│   ├── config/                    # Configuration management
│   ├── api_calls.py               # Low-level API communication
│   ├── main.py                    # Test execution engine
│   └── utils.py                   # Shared utilities
├── config/                        # Test configuration
│   ├── static/                    # Cards, merchants, environments
│   ├── credentials/               # API credentials (gitignored)
│   └── test_suites/               # Test definitions
├── tests/                         # Unit tests
├── documentation/                 # Project documentation
└── debug/                         # Debug tools (gitignored)
```

## Core Concepts

### Test Chains
A **chain** is a sequence of related API calls that share context (like payment IDs).

```csv
chain_id,test_id,call_type,amount,currency
chain7,API0050,create_payment,555,GBP
chain7,API0060,increment_payment,444,GBP
chain7,API0070,capture_payment,222,GBP
chain7,API0080,refund_payment,111,GBP
```

### DCC Context
DCC data is shared across a chain using `DCCContext`:

```python
@dataclass
class DCCContext:
    rate_reference_id: str          # DCC rate ID from inquiry
    original_amount: Dict           # Merchant currency amount
    resulting_amount: Dict          # Customer currency amount  
    inverted_exchange_rate: float   # Conversion rate
```

### Endpoint Interface
All endpoints implement the same interface:

```python
class EndpointInterface:
    @staticmethod
    def call_api(client, *args):
        """Execute the API call"""
        
    @staticmethod  
    def build_request(row, **kwargs):
        """Build the API request object"""
        
    @staticmethod
    def supports_dcc() -> bool:
        """Whether endpoint supports DCC"""
```

## Getting Started

### 1. Environment Setup
```bash
# Clone and setup
git clone <repository>
cd wlacqapitest
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy credentials template
cp config/credentials/secrets.csv.template config/credentials/secrets.csv

# Edit with your API credentials
nano config/credentials/secrets.csv
```

### 3. Run Tests
```bash
# Run all smoke tests
python -m src.main --tests smoke_tests.csv

# Run DCC tests only
python -m src.main --tests smoke_tests.csv --tags dcc --verbose

# Run specific test
python -m src.main --tests smoke_tests.csv --test-ids API0050
```

## Adding New Endpoints

### Step 1: Create Request Builder
Create `src/request_builders/new_endpoint.py`:

```python
"""Build requests for new_endpoint API calls"""
from worldline.acquiring.sdk.v1.domain.api_new_request import ApiNewRequest
from ..utils import clean_request

def build_new_endpoint_request(row, dcc_context=None):
    """Build request for new endpoint"""
    request = ApiNewRequest()
    
    # Set required fields from row data
    request.operation_id = row['test_id'] + ':' + generate_random_string(32)
    
    # Add DCC support if needed
    if dcc_context and dcc_context.rate_reference_id:
        # Apply DCC data (see existing examples)
        pass
        
    return clean_request(request)
```

### Step 2: Create Endpoint Class
Create `src/endpoints/new_endpoint.py`:

```python
"""New Endpoint implementation"""
from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import new_api_call
from ..request_builders.new_endpoint import build_new_endpoint_request

@register_endpoint('new_endpoint')  # ✅ Auto-registration
class NewEndpoint(EndpointInterface):
    
    @staticmethod
    def call_api(client, acquirer_id, merchant_id, request):
        """Execute the API call"""
        return new_api_call(client, acquirer_id, merchant_id, request)
    
    @staticmethod
    def build_request(row, **kwargs):
        """Build request without DCC"""
        return build_new_endpoint_request(row)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, **kwargs):
        """Build request with DCC support"""
        return build_new_endpoint_request(row, dcc_context)
    
    @staticmethod
    def supports_dcc() -> bool:
        """Whether this endpoint supports DCC"""
        return True  # or False
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """Required previous outputs"""
        return ['payment_id']  # or []
```

### Step 3: Add API Call Function
Add to `src/api_calls.py`:

```python
def new_api_call(client, acquirer_id, merchant_id, request):
    """Execute new API call"""
    try:
        logger.info(f"Executing new call - Acquirer: {acquirer_id}")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).new_calls().create(request)
        logger.info(f"New call successful")
        return response
    except Exception as e:
        logger.error(f"New call failed: {e}")
        raise
```

### Step 4: Update Main Logic (if needed)
The endpoint registry automatically handles new endpoints, but you may need to update `src/main.py` if the new endpoint has special argument requirements.

## DCC Implementation

### How DCC Works
1. **Inquiry Phase**: Before main API call, query DCC rates
2. **Context Phase**: Store DCC data in chain context
3. **Application Phase**: Use DCC data in request construction

### DCC in Request Builders
All DCC-enabled request builders follow this pattern:

```python
def build_payment_request(row, dcc_context=None):
    request = ApiPaymentRequest()
    
    # Use DCC resulting amount for main transaction amount
    if dcc_context and dcc_context.resulting_amount:
        amount_data = AmountData()
        amount_data.amount = dcc_context.resulting_amount['amount']
        amount_data.currency_code = dcc_context.resulting_amount['currency_code']
        amount_data.number_of_decimals = dcc_context.resulting_amount['number_of_decimals']
        request.amount = amount_data
    else:
        # Use test amount (merchant currency)
        amount_data = AmountData()
        amount_data.amount = int(row['amount'])
        amount_data.currency_code = row['currency']
        amount_data.number_of_decimals = 2
        request.amount = amount_data
    
    # Add DCC fields if available
    if dcc_context and dcc_context.rate_reference_id:
        dcc_data = DccData()
        dcc_data.amount = int(row['amount'])  # Original merchant amount
        dcc_data.currency_code = row['currency']  # Original merchant currency
        dcc_data.number_of_decimals = 2
        dcc_data.conversion_rate = dcc_context.inverted_exchange_rate
        request.dynamic_currency_conversion = dcc_data
    
    return request
```

### Key DCC Points
- **Main amount**: Use DCC resulting amount (customer currency)
- **DCC object**: Contains original merchant amount and conversion rate
- **Consistency**: All endpoints follow the same pattern

## Testing & Debugging

### Debug Tools
The `debug/` folder contains helpful debugging scripts:

```bash
# Test DCC request structure
python debug/dcc_testing/debug_dcc_request.py

# Test specific request builders
python debug/request_testing/debug_capture_request.py

# Test endpoint connectivity
python debug/request_testing/debug_which_method.py
```

### Unit Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_request_builders/test_create_payment.py

# Run with coverage
pytest --cov=src
```

### Common Debug Patterns
```python
# Add debug prints in request builders
print(f"🔍 DEBUG: DCC context: {dcc_context}")
print(f"🔍 DEBUG: Request dict: {request.to_dictionary()}")

# Add debug prints in endpoints
print(f"🔍 DEBUG: Calling {endpoint.__class__.__name__}")
```

## Common Patterns

### 1. Error Handling
```python
try:
    response = endpoint.call_api(*args)
    # Handle success
except Exception as e:
    logger.error(f"API call failed: {e}")
    # Create error result
    return create_error_result(chain_id, row, call_type, e, duration)
```

### 2. Request Cleaning
```python
from ..utils import clean_request

def build_request(row):
    request = ApiRequest()
    # ... build request
    return clean_request(request)  # ✅ Always clean before returning
```

### 3. Conditional DCC
```python
# In main.py
if dcc_context and endpoint.supports_dcc():
    request = endpoint.build_request_with_dcc(row, dcc_context)
else:
    request = endpoint.build_request(row)
```

### 4. Chain Dependency Validation
```python
# Check if required previous outputs exist
if 'payment_id' not in previous_outputs:
    return create_dependency_error_result(chain_id, row, call_type, 
                                        "payment_id required but not found")
```

## Troubleshooting

### Common Issues

#### 1. Empty DCC Objects
**Symptom**: `"dynamicCurrencyConversion": {}` in request data
**Cause**: Wrong field names in DccData object
**Solution**: Use correct SDK field names: `amount`, `currency_code`, `number_of_decimals`, `conversion_rate`

#### 2. DCC Context Not Found
**Symptom**: `dcc_context is None` in debug output
**Cause**: Endpoint not calling `build_request_with_dcc`
**Solution**: Check main.py logic for DCC-enabled endpoints

#### 3. Request Builder Import Errors
**Symptom**: `ModuleNotFoundError` when importing request builder
**Cause**: Missing `__init__.py` or circular imports
**Solution**: Check import paths and ensure proper module structure

#### 4. Endpoint Not Found
**Symptom**: `Unknown call_type: new_endpoint`
**Cause**: Endpoint not registered or import issue
**Solution**: Ensure `@register_endpoint` decorator is used and module is imported

### Debug Checklist
1. ✅ Check endpoint registration: `EndpointRegistry.get_all_endpoints()`
2. ✅ Verify DCC context: Add debug prints in request builders
3. ✅ Check request structure: Use `.to_dictionary()` method
4. ✅ Validate test data: Ensure CSV has required columns
5. ✅ Check credentials: Verify API credentials are correct

### Getting Help
- Check existing debug scripts in `debug/` folder
- Review unit tests for examples
- Look at working endpoints for patterns
- Add debug prints to trace execution flow

## Best Practices

### Code Organization
- Keep request builders focused on construction only
- Use endpoints only for API calls and routing
- Put business logic in core managers
- Follow existing naming conventions

### Testing
- Write unit tests for new request builders
- Test both DCC and non-DCC scenarios  
- Use debug scripts for integration testing
- Validate request structures with `.to_dictionary()`

### Documentation
- Document new endpoints in this guide
- Add docstrings to all public methods
- Include examples in docstrings
- Update README.md for user-facing changes

---

*This guide covers the core concepts and patterns. For specific implementation details, refer to existing code examples and unit tests.*
