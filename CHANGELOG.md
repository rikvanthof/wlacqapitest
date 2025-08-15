# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Performance optimizations for high-volume testing
- Enhanced error reporting and diagnostics
- Additional payment method support

## [2.1.0] - 2025-08-15

### Added
- **Dynamic Currency Conversion (DCC)** support across all payment endpoints
  - DCC rate inquiry integration before payment operations
  - Chain-aware DCC context management for multi-step workflows
  - Proper currency conversion with original/resulting amount handling
- **Request Builder Pattern** implementation
  - Centralized request construction in `src/request_builders/`
  - Consistent DCC integration across all payment types
  - Clean separation between endpoint logic and request building
- **Enhanced Endpoint Registry** 
  - Plugin-style endpoint registration with `@register_endpoint` decorator
  - DCC capability detection per endpoint type
  - Dependency management for chained operations
- **Comprehensive Documentation**
  - Developer guide (`documentation/developer-guide.md`)
  - Architecture guide (`documentation/architecture-guide.md`)
  - Design principles and implementation patterns
- **Debug Tools**
  - DCC request structure debugging utilities
  - Test fixtures and validation scripts
  - Request builder testing tools (organized in `debug/` folder)

### Fixed
- API validation errors with empty `dynamicCurrencyConversion` objects
- Proper SDK field mapping (`amount`, `currency_code`, `conversion_rate`, `number_of_decimals`)
- Request cleaning and validation before API calls
- Unit test coverage for all DCC functionality (108/108 tests passing)

### Technical
- DCC Manager (`src/core/dcc_manager.py`) for conversion context handling
- Enhanced main execution engine with DCC workflow integration
- Request builders for all payment operations:
  - `src/request_builders/create_payment.py`
  - `src/request_builders/capture_payment.py`
  - `src/request_builders/increment_payment.py`
  - `src/request_builders/refund_payment.py`

### Compatibility
- ✅ **Fully backward compatible** - no breaking changes
- ✅ **Existing features preserved**: Network Tokens, 3D Secure, AVS, Card-on-File
- ✅ **Configuration compatible** - existing test suites work unchanged
- ✅ **API compatible** - all existing endpoints function as before

## [2.0.0] - 2025-08-14

### Added
- **Advanced Payment Features**
  - Card-on-File (CoF) support with initial/subsequent transaction handling
  - Enhanced 3D Secure authentication integration
  - Network Token support for tokenized payments
  - Address Verification System (AVS) integration
- **Enhanced Configuration Management**
  - Structured configuration folders (`config/static/`, `config/credentials/`, `config/test_suites/`)
  - Improved data loading with card-on-file configurations
  - Better error handling and validation

### Fixed
- Unit test coverage for new payment features
- Operation ID generation (changed separator from `-` to `:`)
- Request object assertions and attribute handling
- Data loader unpacking for additional configuration types

### Technical
- Enhanced request builders for advanced payment scenarios
- Improved test coverage (updated test assertions)
- Better SDK integration with correct attribute names

### Breaking Changes
- Operation ID format changed from `TEST001-abc123` to `TEST001:abc123`
- Data loader now returns 8 items (added card-on-file configurations)

## [1.0.0] - 2025-08-10

### Added
- Initial release of Payment API Test Framework
- Support for core Worldline Acquiring API operations:
  - Payment creation and authorization
  - Payment capture and increments  
  - Payment refunds
  - Payment and refund status queries
- **Payment Chain Support**
  - Multi-step payment workflows
  - Dependency management between operations
  - Chain context preservation
- **Configuration Management**
  - CSV-based test definitions
  - Environment and merchant configuration
  - Card and payment method setup
- **Testing Infrastructure**
  - Comprehensive assertion framework
  - Database result storage
  - CSV result export
  - Detailed execution logging
- **Performance Features**
  - Multi-threaded execution support
  - Configurable concurrency levels
  - Performance metrics and reporting

### Technical
- Python 3.9+ support
- Worldline Acquiring SDK integration
- SQLite database for result storage
- Pandas for data manipulation
- Comprehensive unit test suite

---

## Version History Summary

- **v2.1.0**: DCC Implementation - Major feature addition with backward compatibility
- **v2.0.0**: Advanced Payment Features - Card-on-File, 3DS, Network Tokens, AVS
- **v1.0.0**: Initial Release - Core payment testing framework

## Upgrade Notes

### From v2.0.0 to v2.1.0
- ✅ **No configuration changes required**
- ✅ **Fully backward compatible**
- DCC functionality is opt-in via test configuration
- All existing tests continue to work unchanged
- New DCC tests can be added by setting `dcc_target_currency` in test data

### From v1.0.0 to v2.0.0
- ⚠️ **Breaking change**: Operation ID format changed from `-` to `:` separator
- Data loader returns additional configuration item (card-on-file)
- Update any code that depends on operation ID format
- Enhanced payment features available (CoF, 3DS, Network Tokens, AVS)

## Contributing

When adding new features or fixes:
1. Update this CHANGELOG.md in the `[Unreleased]` section
2. Follow [Semantic Versioning](https://semver.org/) for version numbers
3. Categorize changes as: Added, Changed, Deprecated, Removed, Fixed, Security
4. Include upgrade notes for breaking changes
5. Mark breaking changes clearly with ⚠️ warnings