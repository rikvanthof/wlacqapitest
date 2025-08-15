# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Performance optimizations for high-volume testing
- Enhanced error reporting and diagnostics
- Additional payment method support
- Terminal data and Point-of-Sale information support

## [2.2.0] - 2025-08-15

### Added
- **Advanced API Properties Support**
  - `isFinal` flag for partial capture control with sequence numbering
  - `brandSelector` for payment brand selection (CARDHOLDER/MERCHANT) across 4 endpoints
  - `scaExemptionRequest` for European SCA compliance (LOW_VALUE_PAYMENT, TRANSACTION_RISK_ANALYSIS, etc.)
  - `reversalAmount` for partial authorization reversals
  - Complete `MerchantData` support with merchant category codes, addresses, and location info
- **Enhanced CSV Configuration**
  - New `merchantdata.csv` file for comprehensive merchant information management
  - Enhanced `threeddata.csv` with SCA exemption support (exemption-only scenarios supported)
  - Support for 3DS + exemption combinations and exemption-only transactions
- **Partial Operations Suite**
  - Full partial capture capabilities with `isFinal` flag and `capture_sequence_number`
  - Partial authorization reversal support with optional amount specification
  - Smart handling of full vs. partial operations across all relevant endpoints
- **Request Builder Enhancements**
  - MerchantData integration across all 4 card-based endpoints (create_payment, standalone_refund, account_verification, balance_inquiry)
  - Enhanced 3D Secure handling with SCA exemption support
  - Consistent optional parameter patterns across all builders

### Enhanced
- **SCA Compliance Features**
  - Exemption-only scenarios (no 3DS data required)
  - Combined 3DS authentication + SCA exemption requests
  - Full support for all exemption types: LOW_VALUE_PAYMENT, SCA_DELEGATION, SECURE_CORPORATE_PAYMENT, TRANSACTION_RISK_ANALYSIS, TRUSTED_BENEFICIARY
- **Brand Selection Control**
  - Merchant-controlled brand selection for payment optimization
  - Cardholder-controlled brand selection for customer preference
  - Applied consistently across payment, refund, verification, and inquiry operations

### Technical
- **Comprehensive Test Coverage**
  - 267 total unit tests passing (up from 242)
  - 111 request builder tests covering all new functionality
  - Zero test regressions - all existing functionality preserved
  - Comprehensive test scenarios for partial operations, SCA exemptions, and merchant data
- **New Core Modules**
  - `src/merchant_data.py` for merchant information handling
  - Enhanced `src/threed_secure.py` with SCA exemption logic
  - Updated request builders with consistent optional parameter handling
- **Data-Driven Architecture**
  - `merchantdata.csv` with complete merchant information schema
  - `threeddata.csv` enhanced with `sca_exemption_requested` column
  - Flexible CSV structure supporting both minimal and complete merchant data

### Compatibility
- ✅ **Fully backward compatible** - no breaking changes to existing functionality
- ✅ **Existing configurations preserved** - all current test suites work unchanged
- ✅ **Optional features** - new properties are opt-in via CSV configuration
- ✅ **API compatible** - existing request structures remain unchanged
- ✅ **DCC integration** - new features work seamlessly with existing DCC functionality

### CSV Schema Updates
- **merchantdata.csv**: `merchant_id,merchant_category_code,name,address,postal_code,city,state_code,country_code`
- **threeddata.csv**: Added `sca_exemption_requested` column for SCA compliance
- **Main test CSV**: Optional `brand_selector`, `merchant_data`, `is_final`, `capture_sequence_number` columns

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

- **v2.2.0**: Advanced API Properties - Partial operations, SCA compliance, MerchantData, brand selection
- **v2.1.0**: DCC Implementation - Major feature addition with backward compatibility
- **v2.0.0**: Advanced Payment Features - Card-on-File, 3DS, Network Tokens, AVS
- **v1.0.0**: Initial Release - Core payment testing framework

## Upgrade Notes

### From v2.1.0 to v2.2.0
- ✅ **No configuration changes required**
- ✅ **Fully backward compatible**
- New API properties are opt-in via CSV configuration
- Add `merchantdata.csv` file to use merchant data features
- Add `sca_exemption_requested` column to `threeddata.csv` for SCA compliance
- All existing tests continue to work unchanged

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