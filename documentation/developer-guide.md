# Developer Guide

## Overview

This guide covers extending and modifying the Payment API Testing Framework. The framework uses a plugin-based architecture with automatic endpoint discovery, request builder patterns, and feature composition for advanced payment capabilities including SCA exemptions, merchant data, partial operations, and brand selection.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Adding New Endpoints](#adding-new-endpoints)
- [Creating Request Builders](#creating-request-builders)
- [Advanced Payment Features](#advanced-payment-features)
- [API Property Enhancements](#api-property-enhancements)
- [Configuration Management](#configuration-management)
- [Testing Your Extensions](#testing-your-extensions)
- [Best Practices](#best-practices)
- [Debugging and Troubleshooting](#debugging-and-troubleshooting)

## Architecture Overview

### Project Structure

```
src/
├── core/                           # Core framework components
│   ├── endpoint_registry.py       # Plugin system for endpoints
│   ├── dcc_manager.py             # DCC functionality
│   ├── payment_assertions.py      # Response validation
│   └── tag_filter.py              # Test filtering
├── endpoints/                      # API endpoint implementations
│   ├── create_payment_endpoint.py
│   ├── capture_payment_endpoint.py
│   ├── standalone_refund_endpoint.py
│   └── ...                        # 14 total endpoints
├── request_builders/               # Request construction logic
│   ├── create_payment.py
│   ├── capture_payment.py
│   ├── standalone_refund.py
│   └── ...                        # 13 total builders
├── config/                         # Configuration management
│   └── config_manager.py
├── avs.py                         # Address verification
├── cardonfile.py                  # Card-on-File functionality
├── merchant_data.py               # Merchant data integration
├── threed_secure.py               # 3D Secure & SCA exemptions
├── network_token.py               # Network tokenization
├── utils.py                       # Utility functions
├── api_calls.py                   # HTTP client interactions
├── response_utils.py              # Response processing
└── results_handler.py             # Result formatting
```

### Key Design Patterns

1. **Plugin Architecture**: Endpoints auto-register using decorators
2. **Builder Pattern**: Request construction with feature composition
3. **Chain of Responsibility**: Sequential feature application
4. **Registry Pattern**: Centralized endpoint and capability management
5. **Strategy Pattern**: Endpoint-specific implementations with common interfaces

## Adding New Endpoints

### Step 1: Create Endpoint Implementation

Create `src/endpoints/your_endpoint.py`:

```python
"""Your new endpoint with enhanced features"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import your_api_call
from ..request_builders.your_endpoint import build_your_request
from typing import List

@register_endpoint('your_endpoint')
class YourEndpoint(EndpointInterface):
    """Your endpoint with full feature support"""
    
    @staticmethod
    def call_api(client, acquirer_id: str, merchant_id: str, request):
        """Execute your API call"""
        return your_api_call(client, acquirer_id, merchant_id, request)
    
    @staticmethod
    def build_request(row, cards=None, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None, dcc_context=None):
        """Build request with full feature support"""
        return build_your_request(row, cards, address, networktokens, threeds, cardonfile, merchantdata, previous_outputs, dcc_context)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, cards=None, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None):
        """Build request with DCC context"""
        return build_your_request(row, cards, address, networktokens, threeds, cardonfile, merchantdata, previous_outputs, dcc_context)
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """Return required dependencies (e.g., ['payment_id'])"""
        return ['dependency_id']  # or [] if no dependencies
    
    @staticmethod
    def supports_chaining() -> bool:
        """Whether this endpoint can be used in chains"""
        return True
    
    @staticmethod
    def get_output_keys() -> List[str]:
        """What this endpoint provides for other steps"""
        return ['your_id']
    
    @staticmethod
    def supports_dcc() -> bool:
        """Whether this endpoint supports DCC"""
        return True  # or False
```

### Step 2: Add API Call Implementation

Add to `src/api_calls.py`:

```python
def your_api_call(client, acquirer_id, merchant_id, request):
    """Execute your API call with error handling"""
    try:
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).your_endpoint().post(request)
        return response
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise
```

### Step 3: Register in Main Module

The framework will automatically discover your endpoint through the `@register_endpoint` decorator when the module is imported.

## Creating Request Builders

### Basic Request Builder Structure

Create `src/request_builders/your_endpoint.py`:

```python
"""Build requests for your_endpoint API calls"""
import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.your_request import YourRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData

from ..utils import generate_random_string, clean_request
from ..avs import apply_avs_data
from ..network_token import apply_network_token_data
from ..threed_secure import apply_threed_secure_data
from ..cardonfile import apply_cardonfile_data
from ..merchant_data import apply_merchant_data
from ..core.dcc_manager import DCCContext

def build_your_request(row, cards=None, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None, dcc_context=None):
    """Build YourRequest with full feature support"""
    
    request = YourRequest()
    
    # Add Merchant data if specified
    if pd.notna(row.get('merchant_data')) and merchantdata is not None:
        apply_merchant_data(request, row, merchantdata)
    
    # Apply basic fields
    if pd.notna(row.get('amount')):
        amount_data = AmountData()
        amount_data.amount = int(row['amount'])
        amount_data.currency_code = row['currency']
        amount_data.number_of_decimals = 2
        request.amount = amount_data
    
    # Apply advanced payment features
    if pd.notna(row.get('address_data')) and address is not None:
        apply_avs_data(request, row, address)
    
    if pd.notna(row.get('network_token_data')) and networktokens is not None:
        apply_network_token_data(request, row, networktokens)
    
    if pd.notna(row.get('threed_secure_data')) and threeds is not None:
        apply_threed_secure_data(request, row, threeds)
    
    if pd.notna(row.get('card_on_file_data')) and cardonfile is not None:
        apply_cardonfile_data(request, row, cardonfile, previous_outputs)
    
    # Apply API property enhancements
    if pd.notna(row.get('brand_selector')):
        # Apply to appropriate field based on endpoint
        if hasattr(request, 'card_payment_data'):
            request.card_payment_data.brand_selector = row['brand_selector']
    
    if pd.notna(row.get('is_final')):
        request.is_final = str(row['is_final']).upper() == 'TRUE'
    
    # Apply DCC data if context provided
    if dcc_context:
        apply_dcc_data(request, dcc_context, row)
    
    return clean_request(request)

def apply_dcc_data(request, dcc_context, row):
    """Apply DCC data to request"""
    if not dcc_context or not dcc_context.rate_reference_id:
        return request
    
    from worldline.acquiring.sdk.v1.domain.dcc_data import DccData
    
    dcc_data = DccData()
    dcc_data.amount = int(row['amount'])
    dcc_data.currency_code = row['currency']
    dcc_data.number_of_decimals = 2
    dcc_data.conversion_rate = dcc_context.inverted_exchange_rate
    
    request.dynamic_currency_conversion = dcc_data
    return request
```

### Card-Based Request Builder

For endpoints that use cards:

```python
def build_card_based_request(row, cards, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None, dcc_context=None):
    """Build request for card-based endpoint"""
    
    card_row = cards.loc[row['card_id']]
    request = YourCardRequest()
    
    # Add Merchant data first
    if pd.notna(row.get('merchant_data')) and merchantdata is not None:
        apply_merchant_data(request, row, merchantdata)
    
    # Build card data
    from worldline.acquiring.sdk.v1.domain.plain_card_data import PlainCardData
    from worldline.acquiring.sdk.v1.domain.card_payment_data import CardPaymentData
    
    card_data = PlainCardData()
    card_data.card_number = str(card_row['card_number'])
    card_data.expiry_date = str(card_row['expiry_date'])
    
    if pd.notna(card_row.get('card_security_code')):
        card_data.card_security_code = str(card_row['card_security_code'])
    
    card_payment_data = CardPaymentData()
    card_payment_data.card_data = card_data
    
    # Apply brand selector
    if pd.notna(row.get('brand_selector')):
        card_payment_data.brand_selector = row['brand_selector']
    
    request.card_payment_data = card_payment_data
    
    # Apply advanced features...
    # (same as above)
    
    return clean_request(request)
```

## Advanced Payment Features

### Card-on-File Integration

```python
# In your request builder
if pd.notna(row.get('card_on_file_data')) and cardonfile is not None:
    apply_cardonfile_data(request, row, cardonfile, previous_outputs)
```

The `apply_cardonfile_data` function handles:
- Initial vs. subsequent transactions
- Scheme transaction ID linking
- CIT vs. MIT scenarios

### 3D Secure & SCA Exemptions

```python
# In your request builder  
if pd.notna(row.get('threed_secure_data')) and threeds is not None:
    apply_threed_secure_data(request, row, threeds)
```

Supports:
- Full 3D Secure authentication
- Exemption-only scenarios (no 3DS data)
- Combined 3DS + exemption requests
- All SCA exemption types

### Merchant Data Integration

```python
# In your request builder (apply first)
if pd.notna(row.get('merchant_data')) and merchantdata is not None:
    apply_merchant_data(request, row, merchantdata)
```

The `apply_merchant_data` function adds:
- Merchant Category Code (MCC)
- Business name and address
- Complete merchant information

### Network Token Support

```python
# In your request builder
if pd.notna(row.get('network_token_data')) and networktokens is not None:
    apply_network_token_data(request, row, networktokens)
```

Handles:
- Apple Pay integration
- Google Pay integration  
- Token cryptograms and ECI values

### Address Verification

```python
# In your request builder
if pd.notna(row.get('address_data')) and address is not None:
    apply_avs_data(request, row, address)
```

## API Property Enhancements

### Partial Operations Support

```python
def build_capture_payment_request(row, cards=None, **kwargs):
    """Build capture request with partial operation support"""
    request = ApiCaptureRequest()
    
    # Apply partial operation flags
    if pd.notna(row.get('is_final')):
        request.is_final = str(row['is_final']).upper() == 'TRUE'
    
    if pd.notna(row.get('capture_sequence_number')):
        request.capture_sequence_number = int(row['capture_sequence_number'])
    
    return clean_request(request)
```

### Brand Selection Control

```python
def apply_brand_selector(request, row):
    """Apply brand selector to card-based requests"""
    if pd.notna(row.get('brand_selector')):
        if hasattr(request, 'card_payment_data') and request.card_payment_data:
            request.card_payment_data.brand_selector = row['brand_selector']
```

### SCA Exemption Implementation

Create exemption-only scenarios:

```python
# In threeddata.csv
three_d_id,three_d_secure_type,authentication_value,eci,version,sca_exemption_requested
LVP_NO3DS,,,,,LOW_VALUE_PAYMENT
TRA_NO3DS,,,,,TRANSACTION_RISK_ANALYSIS
```

The framework automatically handles exemption application without 3DS data.

## Configuration Management

### Adding New Configuration Files

1. **Create CSV file** in `config/static/your_feature.csv`
2. **Update ConfigurationManager** in `src/config/config_manager.py`:

```python
def load_all_configs(self, test_file_path):
    """Load all configuration files"""
    # ... existing code ...
    
    # Load your new configuration
    your_feature_path = os.path.join(self.config_dir, 'static', 'your_feature.csv')
    your_feature = self.load_data_file(your_feature_path, 'your_feature_id') if os.path.exists(your_feature_path) else None
    
    return ConfigurationSet(
        # ... existing parameters ...
        your_feature=your_feature
    )
```

3. **Update ConfigurationSet** dataclass:

```python
@dataclass
class ConfigurationSet:
    # ... existing fields ...
    your_feature: Optional[pd.DataFrame] = None
```

### Feature Application Pattern

Create `src/your_feature.py`:

```python
"""Your feature data handling for API requests"""

import pandas as pd
import logging
from worldline.acquiring.sdk.v1.domain.your_domain import YourDomain

logger = logging.getLogger(__name__)

def apply_your_feature_data(request, row, your_feature_config):
    """Apply your feature data to the request if specified in the row"""
    
    if not pd.notna(row.get('your_feature_data')):
        logger.debug("No your feature data specified in test row")
        return
    
    feature_id = row['your_feature_data']
    logger.debug(f"Applying your feature data: {feature_id}")
    
    if feature_id not in your_feature_config.index:
        logger.error(f"Feature ID {feature_id} not found in configuration")
        return
    
    feature_row = your_feature_config.loc[feature_id]
    
    # Create and populate domain object
    your_domain = YourDomain()
    your_domain.your_field = feature_row['your_field']
    
    # Apply to appropriate request field
    request.your_feature = your_domain
    
    logger.debug(f"Applied your feature: {feature_id}")
```

## Testing Your Extensions

### Unit Tests

Create `tests/test_your_endpoint.py`:

```python
"""Tests for your endpoint"""
import pytest
from unittest.mock import Mock, MagicMock
from src.endpoints.your_endpoint import YourEndpoint

class TestYourEndpoint:
    """Test your endpoint implementation"""
    
    def test_supports_dcc(self):
        """Test DCC support declaration"""
        assert YourEndpoint.supports_dcc() == True
    
    def test_get_dependencies(self):
        """Test dependency requirements"""
        deps = YourEndpoint.get_dependencies()
        assert isinstance(deps, list)
        assert 'dependency_id' in deps
    
    def test_build_request(self, mock_cards_df):
        """Test request building"""
        row = pd.Series({
            'test_id': 'TEST001',
            'card_id': 'visa_card',
            'amount': 1000,
            'currency': 'GBP'
        })
        
        request = YourEndpoint.build_request(row, cards=mock_cards_df)
        assert request is not None
        assert request.amount.amount == 1000
        assert request.amount.currency_code == 'GBP'
```

Create `tests/test_request_builders/test_your_endpoint.py`:

```python
"""Tests for your request builder"""
import pytest
import pandas as pd
from src.request_builders.your_endpoint import build_your_request

class TestBuildYourRequest:
    """Test your request builder"""
    
    def test_build_basic_request(self, mock_cards_df):
        """Test basic request building"""
        row = pd.Series({
            'test_id': 'TEST001',
            'card_id': 'visa_card',
            'amount': 1000,
            'currency': 'GBP'
        })
        
        request = build_your_request(row, mock_cards_df)
        assert request.amount.amount == 1000
        assert request.amount.currency_code == 'GBP'
    
    def test_build_with_merchant_data(self, mock_cards_df, mock_merchantdata_df):
        """Test with merchant data"""
        row = pd.Series({
            'test_id': 'TEST002',
            'card_id': 'visa_card',
            'merchant_data': 'DEFAULT_MERCHANT',
            'amount': 500,
            'currency': 'EUR'
        })
        
        request = build_your_request(row, mock_cards_df, merchantdata=mock_merchantdata_df)
        assert hasattr(request, 'merchant_data')
        assert request.merchant_data.merchant_category_code == 5812
    
    def test_build_with_brand_selector(self, mock_cards_df):
        """Test brand selector application"""
        row = pd.Series({
            'test_id': 'TEST003',
            'card_id': 'visa_card',
            'brand_selector': 'MERCHANT',
            'amount': 750,
            'currency': 'USD'
        })
        
        request = build_your_request(row, mock_cards_df)
        assert request.card_payment_data.brand_selector == 'MERCHANT'
```

### Integration Testing

Test your endpoint in a real test scenario:

```csv
chain_id,step_order,call_type,test_id,tags,card_id,merchant_id,env,amount,currency,merchant_data,brand_selector,expected_http_status
your_test,1,your_endpoint,YOUR001,custom,visa_card,merchant1,preprod,1000,GBP,DEFAULT_MERCHANT,MERCHANT,201
```

```bash
# Test your endpoint
python -m src.main --tests your_test.csv --verbose
```

## Best Practices

### Code Organization

1. **Separation of Concerns**: Keep endpoint logic, request building, and feature application separate
2. **Consistent Patterns**: Follow existing patterns for parameter handling and error management
3. **Feature Composition**: Make features optional and composable
4. **Error Handling**: Provide clear error messages for missing configurations

### Request Builder Guidelines

```python
def build_your_request(row, cards=None, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None, dcc_context=None):
    """
    Follow these patterns:
    1. Apply merchant data first (if applicable)
    2. Build core request structure
    3. Apply advanced payment features
    4. Apply API property enhancements
    5. Apply DCC data last
    6. Always return clean_request(request)
    """
    request = YourRequest()
    
    # 1. Merchant data first
    if pd.notna(row.get('merchant_data')) and merchantdata is not None:
        apply_merchant_data(request, row, merchantdata)
    
    # 2. Core structure
    # ... build basic request ...
    
    # 3. Advanced features
    if pd.notna(row.get('card_on_file_data')) and cardonfile is not None:
        apply_cardonfile_data(request, row, cardonfile, previous_outputs)
    
    # 4. API properties
    if pd.notna(row.get('brand_selector')):
        # Apply brand selector logic
    
    # 5. DCC last
    if dcc_context:
        apply_dcc_data(request, dcc_context, row)
    
    # 6. Clean and return
    return clean_request(request)
```

### Configuration Best Practices

1. **Consistent IDs**: Use descriptive, consistent identifiers
2. **Optional Fields**: Make advanced features optional with sensible defaults
3. **Validation**: Add validation for required fields and relationships
4. **Documentation**: Document CSV formats and field meanings

### Error Handling

```python
def apply_your_feature(request, row, config):
    """Apply your feature with proper error handling"""
    try:
        if not pd.notna(row.get('your_feature_data')):
            return  # Optional feature, skip gracefully
        
        feature_id = row['your_feature_data']
        
        if feature_id not in config.index:
            logger.error(f"Feature ID {feature_id} not found in configuration")
            return  # Don't fail the entire test
        
        # Apply feature logic
        
    except Exception as e:
        logger.error(f"Error applying your feature: {e}")
        # Don't re-raise unless critical
```

## Debugging and Troubleshooting

### Debug Your Endpoint

```bash
# Test specific endpoint
python -m src.main --tests your_test.csv --verbose

# Debug with single thread
python -m src.main --tests your_test.csv --threads 1 --verbose

# Test endpoint registration
python -c "
from src.core.endpoint_registry import get_endpoint
endpoint = get_endpoint('your_endpoint')
print(f'Endpoint: {endpoint}')
print(f'Supports DCC: {endpoint.supports_dcc()}')
print(f'Dependencies: {endpoint.get_dependencies()}')
"
```

### Common Issues

**Endpoint Not Found:**
- Ensure `@register_endpoint('name')` decorator is used
- Check that endpoint module is imported
- Verify endpoint name matches test file `call_type`

**Request Building Errors:**
- Check parameter types (DataFrame vs dict)
- Ensure required SDK domain objects are imported
- Verify field names match SDK expectations

**Feature Application Issues:**
- Check configuration file exists and has correct headers
- Verify feature IDs exist in configuration
- Ensure feature application doesn't conflict with other features

### Logging and Debugging

```python
import logging
logger = logging.getLogger(__name__)

def your_function():
    logger.debug("Debug information")
    logger.info("Important information")
    logger.warning("Warning message")
    logger.error("Error message")
```

Enable debug logging:
```bash
python -m src.main --tests your_test.csv --verbose --log-level DEBUG
```

## Advanced Extension Examples

### Custom Payment Method

```python
@register_endpoint('custom_payment')
class CustomPaymentEndpoint(EndpointInterface):
    """Custom payment method endpoint"""
    
    @staticmethod
    def supports_dcc() -> bool:
        return True
    
    @staticmethod
    def build_request(row, **kwargs):
        # Custom request building logic
        return build_custom_payment_request(row, **kwargs)
```

### Feature-Specific Endpoint

```python
@register_endpoint('loyalty_payment')  
class LoyaltyPaymentEndpoint(EndpointInterface):
    """Payment with loyalty points"""
    
    @staticmethod
    def build_request(row, cards=None, loyalty_config=None, **kwargs):
        request = build_create_payment_request(row, cards, **kwargs)
        
        # Add loyalty-specific logic
        if pd.notna(row.get('loyalty_points')):
            apply_loyalty_data(request, row, loyalty_config)
        
        return request
```

The Payment API Testing Framework provides a flexible, extensible architecture for testing complex payment scenarios. Follow these patterns to add new endpoints, features, and API property enhancements while maintaining consistency with the existing codebase.