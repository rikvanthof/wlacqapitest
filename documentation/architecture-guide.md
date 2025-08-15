# Architecture Guide

## Overview

The Payment API Testing Framework employs a modular, plugin-based architecture designed for extensibility, maintainability, and robust testing of complex payment scenarios. The framework supports advanced payment features, chain-level parallelism, graceful degradation, and comprehensive configuration management through CSV files optimized for Excel editing.

## Table of Contents

- [Architectural Principles](#architectural-principles)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Plugin Architecture](#plugin-architecture)
- [Configuration Management](#configuration-management)
- [Execution Model](#execution-model)
- [Data Flow](#data-flow)
- [Error Handling Strategy](#error-handling-strategy)
- [Extensibility Design](#extensibility-design)
- [Performance Considerations](#performance-considerations)

## Architectural Principles

### 1. **Modularity and Separation of Concerns**
- **Endpoints**: Handle API-specific logic and registration
- **Request Builders**: Construct API requests with feature composition
- **Feature Modules**: Apply advanced payment capabilities independently
- **Configuration**: Manage test data and scenarios externally
- **Core Framework**: Provide execution, registry, and utility services

### 2. **Plugin-Based Extensibility**
- Endpoints register automatically via decorators
- New endpoints can be added without modifying core framework
- Feature composition allows mixing and matching capabilities
- Interface enforcement ensures consistency across plugins

### 3. **Graceful Degradation**
- Missing configurations don't halt execution
- Invalid test definitions are skipped with clear error messages
- Chain failures don't affect other chains
- Framework generates APIs that may not make business sense (by design)

### 4. **Configuration-Driven Testing**
- Test scenarios defined in CSV files for Excel compatibility
- Advanced payment features configured externally
- Environment and credential management separated
- Future migration to database/GUI planned

### 5. **Chain-Level Parallelism**
- Multiple test chains execute simultaneously
- Steps within each chain remain sequential
- Thread-safe result collection and dependency management
- Scalable performance with configurable thread counts

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Framework Entry Point                       │
│                        (src/main.py)                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Plugin Discovery & Registration                │
│                (import src.endpoints → decorators)             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Configuration Loading                        │
│              (ConfigurationManager → CSV files)                │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Chain Execution Engine                       │
│                 (ThreadPoolExecutor → Chains)                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│    Step Execution (Sequential within Chain)                     │
│  Endpoint → Request Builder → Feature Application → API Call    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Result Collection                            │
│              (Assertions → Database → CSV Export)              │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. **Endpoint Registry (src/core/endpoint_registry.py)**

**Purpose**: Central plugin management and endpoint discovery

**Key Features**:
- Decorator-based registration (`@register_endpoint`)
- Interface enforcement via `EndpointInterface` ABC
- Automatic endpoint discovery through explicit imports
- DCC capability detection and validation
- Thread-safe endpoint access

**Registration Mechanism**:
```python
@register_endpoint('create_payment')
class CreatePaymentEndpoint(EndpointInterface):
    # Implementation...
```

**Discovery Process**:
1. `main.py` imports `src.endpoints`
2. `src.endpoints.__init__.py` imports all endpoint modules
3. Import triggers `@register_endpoint` decorators
4. Endpoints register with `EndpointRegistry`
5. Registry validates interface compliance

### 2. **Configuration Manager (src/config/config_manager.py)**

**Purpose**: Centralized configuration loading and management

**Key Features**:
- CSV file loading with pandas DataFrame conversion
- Index setting for efficient lookups
- Optional configuration file handling
- Validation and error reporting
- Future database migration preparation

**Configuration Architecture**:
```
config/
├── credentials/secrets.csv     # API credentials (gitignored)
├── static/environments.csv    # API endpoints
├── static/merchants.csv       # Merchant configurations
├── static/cards.csv           # Test card data
├── static/cardonfile.csv      # Card-on-File scenarios
├── static/threeddata.csv      # 3DS & SCA exemptions
├── static/merchantdata.csv    # Merchant information
├── static/networktoken.csv    # Network tokenization
└── static/address.csv         # Address verification
```

### 3. **Request Builders (src/request_builders/)**

**Purpose**: Compose API requests with feature integration

**Key Features**:
- Builder pattern for request construction
- Feature composition through function calls
- Consistent parameter handling
- SDK domain object management
- DCC integration support

**Builder Pattern**:
```python
def build_create_payment_request(row, cards, address=None, networktokens=None, 
                                threeds=None, cardonfile=None, merchantdata=None, 
                                previous_outputs=None, dcc_context=None):
    request = ApiPaymentRequest()
    
    # 1. Apply merchant data first
    if merchantdata: apply_merchant_data(request, row, merchantdata)
    
    # 2. Build core request
    # ... core logic ...
    
    # 3. Apply advanced features
    if cardonfile: apply_cardonfile_data(request, row, cardonfile, previous_outputs)
    if threeds: apply_threed_secure_data(request, row, threeds)
    
    # 4. Apply DCC last
    if dcc_context: apply_dcc_data(request, dcc_context, row)
    
    return clean_request(request)
```

### 4. **Feature Modules**

**Purpose**: Independent advanced payment feature implementation

**Modules**:
- `cardonfile.py` - Card-on-File (UCOF) functionality
- `threed_secure.py` - 3D Secure authentication & SCA exemptions
- `merchant_data.py` - Merchant information integration
- `network_token.py` - Network tokenization (Apple Pay, Google Pay)
- `avs.py` - Address verification service
- `core/dcc_manager.py` - Dynamic Currency Conversion

**Feature Application Pattern**:
```python
def apply_feature_data(request, row, feature_config, previous_outputs=None):
    """Standard pattern for feature application"""
    if not pd.notna(row.get('feature_data')):
        return  # Optional feature, skip gracefully
    
    feature_id = row['feature_data']
    if feature_id not in feature_config.index:
        logger.error(f"Feature ID {feature_id} not found")
        return  # Don't fail entire test
    
    # Apply feature logic
    feature_data = create_feature_object(feature_config.loc[feature_id])
    request.feature = feature_data
```

## Plugin Architecture

### Registration System

**Decorator Pattern**:
```python
def register_endpoint(call_type: str):
    """Decorator to register an endpoint"""
    def decorator(endpoint_class):
        EndpointRegistry.validate_endpoint(call_type, endpoint_class)
        EndpointRegistry.register(call_type, endpoint_class)
        return endpoint_class
    return decorator
```

**Interface Enforcement**:
```python
class EndpointInterface(ABC):
    @staticmethod @abstractmethod
    def call_api(*args, **kwargs): pass
    
    @staticmethod @abstractmethod
    def build_request(row, *args, **kwargs): pass
    
    @staticmethod @abstractmethod
    def get_dependencies() -> List[str]: pass
    
    @staticmethod @abstractmethod
    def supports_chaining() -> bool: pass
    
    @staticmethod @abstractmethod
    def get_output_keys() -> List[str]: pass
    
    @staticmethod
    def supports_dcc() -> bool: return False
```

### Discovery Mechanism

**Explicit Import Strategy**:
1. **main.py** imports `src.endpoints`
2. **endpoints/__init__.py** imports all endpoint modules
3. **Endpoint modules** use `@register_endpoint` decorators
4. **Registry** validates and stores endpoint implementations

**Benefits of Explicit Imports**:
- Predictable loading behavior
- Clear dependency management
- Easy debugging and testing
- No filesystem scanning required
- Works reliably across deployment environments

### Endpoint Capabilities

**Capability Detection**:
- `supports_dcc()` - DCC compatibility
- `supports_chaining()` - Chain participation
- `get_dependencies()` - Required previous outputs
- `get_output_keys()` - Provided outputs for subsequent steps

**Dynamic Capability Usage**:
```python
if EndpointRegistry.endpoint_supports_dcc(call_type):
    request = endpoint.build_request_with_dcc(row, dcc_context, **kwargs)
else:
    request = endpoint.build_request(row, **kwargs)
```

## Configuration Management

### CSV-Based Strategy

**Design Rationale**:
- **Excel Compatibility**: Business users can edit test scenarios in familiar tools
- **Version Control**: Text-based format works well with Git
- **Simplicity**: No complex parsing or schema management
- **Future Migration**: Structure designed for easy database migration

**Configuration Loading Pipeline**:
```python
ConfigurationManager → load_all_configs() → ConfigurationSet
    ├── load_data_file(environments.csv) → DataFrame
    ├── load_data_file(merchants.csv) → DataFrame  
    ├── load_data_file(cards.csv) → DataFrame
    ├── load_data_file(cardonfile.csv) → DataFrame
    ├── load_data_file(threeddata.csv) → DataFrame
    ├── load_data_file(merchantdata.csv) → DataFrame
    └── load_data_file(secrets.csv) → DataFrame
```

**Index Strategy**:
- Primary keys become DataFrame indices for O(1) lookup
- Relationships maintained through ID references
- Missing configurations handled gracefully

### Security Architecture

**Credential Separation**:
- `config/credentials/secrets.csv` - Sensitive API credentials (gitignored)
- `config/static/environments.csv` - Public endpoint configurations
- Template files for credential setup
- Environment-specific credential management

## Execution Model

### Chain-Level Parallelism

**Threading Architecture**:
```python
ThreadPoolExecutor(max_workers=thread_count)
    ├── Chain 1 → Sequential Steps → Results
    ├── Chain 2 → Sequential Steps → Results  
    ├── Chain 3 → Sequential Steps → Results
    └── Chain N → Sequential Steps → Results
```

**Benefits**:
- **Scalability**: Multiple chains execute simultaneously
- **Isolation**: Chain failures don't affect other chains
- **Dependency Safety**: Steps within chains remain sequential
- **Resource Control**: Configurable thread count prevents API overload

### Step Execution Pipeline

**Sequential Step Processing**:
```
For each step in chain:
1. Dependency Check → Skip if missing required outputs
2. Endpoint Resolution → Get registered endpoint implementation
3. Request Building → Compose API request with features
4. API Execution → Call Worldline API with error handling
5. Response Processing → Extract IDs and update previous_outputs
6. Assertion Validation → Comprehensive business logic checks
7. Result Recording → Store detailed results for analysis
```

### Dependency Management

**Previous Outputs Tracking**:
```python
previous_outputs = {
    'payment_id': 'ABC123',
    'refund_id': 'DEF456', 
    'scheme_transaction_id': 'XYZ789'  # For Card-on-File chains
}
```

**Dependency Resolution**:
- Each endpoint declares required dependencies
- Framework checks availability before execution
- Missing dependencies cause graceful step skipping
- Complex dependencies (like scheme transaction IDs) handled automatically

## Data Flow

### Test Data Flow

```
CSV Test Definition → DataFrame → Test Chains → Individual Steps
    ↓
Configuration Files → DataFrames → Feature Application
    ↓  
Request Building → SDK Objects → API Calls → Responses
    ↓
Assertion Engine → Result Objects → Database/CSV Export
```

### Feature Application Flow

```
Row Data + Configuration → Feature Module → Domain Object → Request Field
    ↓
Example: 'merchant_data': 'DEFAULT_MERCHANT' 
    + merchantdata.csv 
    → apply_merchant_data() 
    → MerchantData object 
    → request.merchant_data
```

### Chain Execution Flow

```
Chain Definition → Dependency Analysis → Step Ordering → Execution
    ↓
Step 1: create_payment → payment_id
    ↓
Step 2: capture_payment(payment_id) → capture_id  
    ↓
Step 3: refund_payment(payment_id) → refund_id
```

## Error Handling Strategy

### Graceful Degradation Philosophy

**Core Principle**: The framework should allow users to create "incorrect" API requests and test scenarios without blocking execution.

**Implementation**:
- Missing configurations → Skip feature application, continue test
- Invalid dependencies → Skip step, record error, continue chain
- API errors → Record error details, continue with next step
- Malformed requests → Allow generation, let API return appropriate errors

**Error Categories**:

1. **Configuration Errors** (Non-blocking):
   ```python
   if feature_id not in config.index:
       logger.error(f"Feature ID {feature_id} not found")
       return  # Skip feature, don't fail test
   ```

2. **Dependency Errors** (Step-blocking):
   ```python
   if 'payment_id' not in previous_outputs:
       result = create_error_result("payment_id not available")
       return result  # Skip step, record error
   ```

3. **API Errors** (Recorded but not blocking):
   ```python
   try:
       response = api_call(request)
   except Exception as e:
       result = create_error_result(str(e))
       return result  # Record error, continue chain
   ```

### Error Recovery

**Chain Isolation**: Failed chains don't affect other chains
**Step Recovery**: Failed steps don't prevent subsequent steps (if dependencies allow)
**Result Preservation**: All errors are recorded with full context for analysis

## Extensibility Design

### Adding New Endpoints

**Process**:
1. Create endpoint class implementing `EndpointInterface`
2. Add `@register_endpoint('name')` decorator
3. Create corresponding request builder function
4. Add API call implementation
5. Import in `endpoints/__init__.py`

**Framework automatically**:
- Discovers and registers the endpoint
- Validates interface compliance
- Makes endpoint available for test definitions
- Integrates with all existing features

### Adding New Features

**Process**:
1. Create feature module (e.g., `src/loyalty.py`)
2. Implement `apply_loyalty_data(request, row, config)` function
3. Add configuration file (`config/static/loyalty.csv`)
4. Update ConfigurationManager to load loyalty config
5. Modify request builders to call feature application

**Feature Integration Pattern**:
```python
# In request builder
if pd.notna(row.get('loyalty_data')) and loyalty_config is not None:
    apply_loyalty_data(request, row, loyalty_config)
```

### Adding New Configuration

**Process**:
1. Create CSV file in `config/static/`
2. Update `ConfigurationManager.load_all_configs()`
3. Update `ConfigurationSet` dataclass
4. Create feature application function
5. Integrate with request builders

## Performance Considerations

### Threading Model

**Chain-Level Parallelism Benefits**:
- Maximizes throughput for independent test scenarios
- Avoids complex step-level synchronization
- Maintains deterministic execution within chains
- Simplifies debugging and error tracking

**Thread Safety**:
- Each chain has isolated execution context
- Shared resources (registry, configuration) are read-only after initialization
- Result collection uses thread-safe mechanisms
- HTTP client instances are created per thread

### Configuration Loading

**Optimization Strategies**:
- DataFrames loaded once at startup
- Index-based O(1) configuration lookups
- Lazy loading for optional configurations
- Memory-efficient pandas operations

### Request Building

**Performance Patterns**:
- Feature application is optional and conditional
- Object creation minimized through reuse
- Clean request utility removes unused fields
- SDK object creation optimized for common patterns

### API Call Efficiency

**HTTP Optimization**:
- Connection pooling through SDK
- Configurable timeouts and connection limits
- Retry logic for transient failures
- Trace ID tracking for debugging

### Result Processing

**Storage Strategy**:
- Streaming CSV output for large result sets
- SQLite database for efficient querying
- Bulk insert operations for performance
- Configurable result retention policies

## Future Architecture Considerations

### Database Migration

**Planned Evolution**:
- CSV files → Database tables
- Excel editing → Web-based GUI
- File-based config → API-based configuration management
- Manual setup → Automated configuration deployment

### GUI Integration

**Architecture Preparation**:
- Configuration abstraction layer already in place
- REST API potential through existing modular design
- Test definition validation ready for UI integration
- Result visualization through existing database structure

### Advanced Features

**Scalability Roadmap**:
- Distributed execution across multiple nodes
- Real-time test result streaming
- Advanced assertion DSL for complex validations
- Integration with external test management systems

The Payment API Testing Framework architecture provides a solid foundation for comprehensive payment testing while maintaining flexibility for future enhancements and integrations. The modular, plugin-based design ensures that new payment methods, features, and capabilities can be added without disrupting existing functionality.