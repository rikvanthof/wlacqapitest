# AI Development Assistant Prompt for Payment API Testing Framework

## Overview

You are helping develop extensions for a Python-based Payment API Testing Framework for Worldline Acquiring APIs. This framework uses a modular, plugin-based architecture with specific design patterns and coding standards that must be maintained for consistency.

## Framework Architecture & Design Patterns

### Core Principles
1. **Plugin Architecture**: Endpoints auto-register using decorators
2. **Graceful Degradation**: Missing configurations don't halt execution; invalid tests are skipped with clear errors
3. **Feature Composition**: Advanced payment features are applied independently and can be mixed/matched
4. **Chain-Level Parallelism**: Multiple test chains run simultaneously, steps within chains are sequential
5. **Configuration-Driven**: CSV files for Excel compatibility, future database migration planned
6. **Interface Enforcement**: Abstract base classes ensure consistency across plugins

### Key Design Patterns Used
- **Registry Pattern**: `EndpointRegistry` with decorator-based registration
- **Builder Pattern**: Request construction with feature composition
- **Chain of Responsibility**: Sequential feature application to requests
- **Strategy Pattern**: Endpoint-specific implementations with common interfaces
- **Template Method**: Consistent error handling and result processing

## Project Structure

```
src/
├── core/
│   ├── endpoint_registry.py       # Plugin system with @register_endpoint
│   ├── payment_assertions.py      # Response validation engine
│   ├── dcc_manager.py             # Dynamic Currency Conversion
│   └── tag_filter.py              # Test filtering logic
├── endpoints/                      # API endpoint implementations (14 total)
│   ├── create_payment_endpoint.py # Example: Payment creation
│   ├── capture_payment_endpoint.py # Example: Payment capture
│   └── __init__.py                # Explicit imports for auto-discovery
├── request_builders/               # Request construction (13 total)
│   ├── create_payment.py          # Example: Payment request building
│   ├── capture_payment.py         # Example: Capture request building
│   └── __init__.py
├── config/
│   └── config_manager.py          # CSV configuration loading
├── [feature].py files             # Feature modules (cardonfile, threed_secure, etc.)
├── api_calls.py                   # HTTP client interactions
├── response_utils.py              # Response processing utilities
├── results_handler.py             # Result formatting and storage
└── utils.py                       # Utility functions

config/
├── credentials/secrets.csv        # API credentials (gitignored)
├── static/                        # Configuration files
│   ├── environments.csv           # API endpoints
│   ├── merchants.csv              # Merchant configurations
│   ├── cards.csv                  # Test card data
│   ├── cardonfile.csv             # Card-on-File scenarios
│   ├── threeddata.csv             # 3DS & SCA exemptions
│   ├── merchantdata.csv           # Merchant information
│   ├── networktoken.csv           # Network tokenization
│   └── address.csv                # Address verification
└── test_suites/                   # Test scenario definitions
```

## Code Patterns & Examples

### 1. Endpoint Implementation Pattern

```python
"""[Endpoint name] endpoint with enhanced features"""

from ..core.endpoint_registry import register_endpoint, EndpointInterface
from ..api_calls import your_api_call
from ..request_builders.your_endpoint import build_your_request
from typing import List

@register_endpoint('your_endpoint')
class YourEndpoint(EndpointInterface):
    """[Description] endpoint with full feature support"""
    
    @staticmethod
    def call_api(client, acquirer_id: str, merchant_id: str, request):
        """Execute [endpoint] API call"""
        return your_api_call(client, acquirer_id, merchant_id, request)
    
    @staticmethod
    def build_request(row, cards=None, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None, dcc_context=None):
        """Build [endpoint] request with full feature support"""
        return build_your_request(row, cards, address, networktokens, threeds, cardonfile, merchantdata, previous_outputs, dcc_context)
    
    @staticmethod
    def build_request_with_dcc(row, dcc_context=None, **kwargs):
        """Build [endpoint] request with DCC context"""
        return build_your_request(row, dcc_context=dcc_context, **kwargs)
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """Return required dependencies (e.g., ['payment_id'])"""
        return []  # or ['dependency_id'] if dependencies required
    
    @staticmethod
    def supports_chaining() -> bool:
        """Whether this endpoint can be used in chains"""
        return True
    
    @staticmethod
    def get_output_keys() -> List[str]:
        """What this endpoint provides for other steps"""
        return ['your_id']  # e.g., ['payment_id', 'scheme_transaction_id']
    
    @staticmethod
    def supports_dcc() -> bool:
        """Whether this endpoint supports DCC"""
        return True  # or False
```

### 2. Request Builder Pattern

```python
"""Build requests for [endpoint] API calls"""
import pandas as pd
from worldline.acquiring.sdk.v1.domain.your_request import YourRequest
from worldline.acquiring.sdk.v1.domain.amount_data import AmountData

from ..utils import generate_random_string, clean_request
from ..avs import apply_avs_data
from ..network_token import apply_network_token_data
from ..threed_secure import apply_threed_secure_data
from ..cardonfile import apply_cardonfile_data
from ..merchant_data import apply_merchant_data

def build_your_request(row, cards=None, address=None, networktokens=None, threeds=None, cardonfile=None, merchantdata=None, previous_outputs=None, dcc_context=None):
    """Build YourRequest with full feature support"""
    
    # For card-based endpoints, get card data
    if cards is not None:
        card_row = cards.loc[row['card_id']]
    
    request = YourRequest()
    
    # 1. Apply merchant data FIRST (if applicable)
    if pd.notna(row.get('merchant_data')) and merchantdata is not None:
        apply_merchant_data(request, row, merchantdata)
    
    # 2. Build core request structure
    if pd.notna(row.get('amount')):
        amount_data = AmountData()
        amount_data.amount = int(row['amount'])
        amount_data.currency_code = row['currency']
        amount_data.number_of_decimals = 2
        request.amount = amount_data
    
    # 3. Apply advanced payment features (order matters)
    if pd.notna(row.get('address_data')) and address is not None:
        apply_avs_data(request, row, address)
    
    if pd.notna(row.get('network_token_data')) and networktokens is not None:
        apply_network_token_data(request, row, networktokens)
    
    if pd.notna(row.get('threed_secure_data')) and threeds is not None:
        apply_threed_secure_data(request, row, threeds)
    
    if pd.notna(row.get('card_on_file_data')) and cardonfile is not None:
        apply_cardonfile_data(request, row, cardonfile, previous_outputs)
    
    # 4. Apply API property enhancements
    if pd.notna(row.get('brand_selector')):
        # Apply to appropriate field based on endpoint
        if hasattr(request, 'card_payment_data'):
            request.card_payment_data.brand_selector = row['brand_selector']
    
    if pd.notna(row.get('is_final')):
        request.is_final = str(row['is_final']).upper() == 'TRUE'
    
    if pd.notna(row.get('capture_sequence_number')):
        request.capture_sequence_number = int(row['capture_sequence_number'])
    
    # 5. Apply DCC data LAST
    if dcc_context:
        apply_dcc_data(request, dcc_context, row)
    
    # 6. Always clean and return
    return clean_request(request)
```

### 3. Feature Module Pattern

```python
"""[Feature name] data handling for API requests"""

import pandas as pd
import logging
from worldline.acquiring.sdk.v1.domain.your_domain import YourDomain

logger = logging.getLogger(__name__)

def apply_your_feature_data(request, row, your_feature_config, previous_outputs=None):
    """Apply [feature] data to the request if specified in the row"""
    
    if not pd.notna(row.get('your_feature_data')):
        logger.debug("No [feature] data specified in test row")
        return
    
    feature_id = row['your_feature_data']
    logger.debug(f"Applying [feature] data: {feature_id}")
    
    # Handle both DataFrame and dict cases
    if isinstance(your_feature_config, pd.DataFrame):
        if feature_id not in your_feature_config.index:
            logger.error(f"[Feature] ID {feature_id} not found in configuration")
            return  # Don't fail entire test - graceful degradation
        feature_row = your_feature_config.loc[feature_id]
    elif isinstance(your_feature_config, dict):
        if feature_id not in your_feature_config:
            logger.error(f"[Feature] ID {feature_id} not found in configuration")
            return
        feature_row = your_feature_config[feature_id]
    else:
        logger.error(f"Invalid [feature] configuration type: {type(your_feature_config)}")
        return
    
    try:
        # Create and populate domain object
        your_domain = YourDomain()
        your_domain.your_field = feature_row['your_field']
        # ... populate other fields ...
        
        # Apply to appropriate request field
        request.your_feature = your_domain
        
        logger.debug(f"Applied [feature]: {feature_id}")
        
    except Exception as e:
        logger.error(f"Error applying [feature] data: {e}")
        # Don't re-raise - graceful degradation
```

### 4. Error Handling Pattern

```python
# ALWAYS use graceful degradation
def some_function():
    try:
        # Main logic
        pass
    except Exception as e:
        logger.error(f"Error in function: {e}")
        return  # Don't re-raise unless critical
    
# Configuration missing - skip gracefully
if feature_id not in config.index:
    logger.error(f"Feature ID {feature_id} not found")
    return  # Skip feature, don't fail test

# Dependency missing - skip step
if 'payment_id' not in previous_outputs:
    return create_error_result("payment_id not available")
```

### 5. Testing Pattern

```python
"""Tests for [your module]"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.your_module import your_function

class TestYourFunction:
    """Test suite for your_function"""
    
    def test_successful_case(self, mock_cards_df):
        """Test the happy path"""
        row = pd.Series({
            'test_id': 'TEST001',
            'card_id': 'visa_card',
            'amount': 1000,
            'currency': 'GBP'
        })
        
        result = your_function(row, mock_cards_df)
        assert result is not None
        assert result.amount.amount == 1000
    
    def test_with_advanced_features(self, mock_cards_df, mock_merchantdata_df):
        """Test with advanced payment features"""
        row = pd.Series({
            'test_id': 'TEST002', 
            'merchant_data': 'DEFAULT_MERCHANT',
            'brand_selector': 'MERCHANT'
        })
        
        result = your_function(row, mock_cards_df, merchantdata=mock_merchantdata_df)
        assert hasattr(result, 'merchant_data')
        assert result.card_payment_data.brand_selector == 'MERCHANT'
    
    def test_graceful_degradation(self, mock_cards_df):
        """Test missing configuration handling"""
        row = pd.Series({
            'test_id': 'TEST003',
            'your_feature_data': 'MISSING_ID'  # Doesn't exist in config
        })
        
        # Should not raise exception
        result = your_function(row, mock_cards_df, your_feature_config=pd.DataFrame())
        assert result is not None  # Function completes despite missing config
```

## Development Guidelines

### Configuration Management
- CSV files use index columns for O(1) lookups
- Optional configurations should have None checks
- New config files need ConfigurationManager updates
- Use pandas DataFrame.loc[] for index-based access

### Request Building Standards
1. Apply merchant data FIRST (if applicable)
2. Build core request structure
3. Apply advanced payment features
4. Apply API property enhancements
5. Apply DCC data LAST
6. Always return `clean_request(request)`

### Feature Integration
- Features are always optional with graceful fallback
- Use `pd.notna(row.get('feature_data'))` pattern
- Handle both DataFrame and dict configurations
- Apply features in request builders, not endpoints

### Error Handling Philosophy
- **Never fail entire test execution for configuration issues**
- Log errors clearly but continue processing
- Return early from functions on missing configurations
- Record detailed error information in results
- Allow "incorrect" API requests to be generated (by design)

### Threading Considerations
- Endpoints and features must be thread-safe
- Use logger for debugging (thread-safe)
- No shared mutable state between threads
- Each chain has isolated execution context

## Common Development Tasks

### Adding New Endpoint
1. Create `src/endpoints/your_endpoint.py` with `@register_endpoint`
2. Implement `EndpointInterface` abstract methods
3. Create `src/request_builders/your_endpoint.py`
4. Add API call to `src/api_calls.py`
5. Add import to `src/endpoints/__init__.py`
6. Create unit tests in `tests/test_endpoints/` and `tests/test_request_builders/`

### Adding New Feature
1. Create `src/your_feature.py` with `apply_your_feature_data()` function
2. Create `config/static/your_feature.csv` configuration file
3. Update `ConfigurationManager.load_all_configs()`
4. Update `ConfigurationSet` dataclass
5. Modify request builders to call feature application
6. Add comprehensive unit tests

### Adding New Configuration
1. Create CSV file in `config/static/`
2. Update `src/config/config_manager.py`
3. Update configuration loading in main execution flow
4. Add validation and error handling
5. Update relevant request builders

### Adding API Properties
1. Add new columns to test CSV files
2. Update request builders to handle new properties
3. Add validation in request building
4. Update assertion engine if needed
5. Add comprehensive test coverage

## Quality Standards

### Code Quality
- Follow existing naming conventions
- Use type hints for parameters and return values
- Add docstrings for all public functions and classes
- Follow pandas best practices for DataFrame operations
- Use logging instead of print statements

### Testing Requirements
- Unit tests for all new functionality
- Test both successful and error scenarios
- Test graceful degradation behavior
- Mock external dependencies appropriately
- Maintain test coverage above 90%

### Documentation
- Update relevant documentation files
- Add CSV file format documentation
- Include usage examples
- Document any new configuration requirements

## Request Help Format

When asking for help, please provide:

1. **What you're trying to build**: "I want to add [feature/endpoint] that does [description]"

2. **Existing similar code**: "This is similar to [existing_endpoint/feature] but differs in [ways]"

3. **Configuration needs**: "I need a CSV with columns [list] for [purpose]"

4. **Integration points**: "This needs to integrate with [existing features] and work with [endpoints]"

5. **Error handling**: "When [configuration missing/API fails], it should [behavior]"

6. **Specific questions**: "I'm unsure about [specific technical aspect] and need guidance on [pattern/approach]"

This framework prioritizes consistency, extensibility, and graceful error handling. Always follow existing patterns and maintain the principle that configuration issues should never halt test execution entirely.