# Payment API Test Framework

[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](requirements.txt)
[![Tests](https://img.shields.io/badge/tests-267%2F267%20passing-brightgreen.svg)](#testing)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](documentation/)

A comprehensive Python testing framework for Worldline Acquiring payment APIs, supporting complex payment workflows, Dynamic Currency Conversion (DCC), advanced payment features, and enhanced API properties for partial operations, SCA compliance, and merchant data integration.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd wlacqapitest
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure credentials
cp config/credentials/secrets.csv.template config/credentials/secrets.csv
# Edit with your API credentials

# Run smoke tests
python -m src.main --tests smoke_tests.csv

# Run with advanced features
python -m src.main --tests regression.csv --tags "sca,partial,merchant" --verbose
```

**📖 New to the framework?** Start with the [User Guide](documentation/user-guide.md) | **🔧 Setting up?** See [Environment Setup](documentation/environment-setup.md)

---

## ✨ Key Features

### 💳 **Comprehensive Payment Support**
- **Core Operations**: Create, capture, increment, and refund payments
- **Chain Workflows**: Multi-step payment scenarios with shared context
- **Advanced Features**: 3D Secure, AVS, Network Tokens, Card-on-File

### 🌍 **Dynamic Currency Conversion (DCC)**
- Automatic currency conversion rate inquiry
- Multi-currency payment chain support
- Real-time exchange rate integration
- Consistent DCC handling across all payment types

### 🎯 **Enhanced API Properties** ⭐ *New in v2.2.0*
- **Partial Operations**: `isFinal` flag and sequence-controlled partial captures
- **SCA Compliance**: European exemption support (LOW_VALUE_PAYMENT, TRANSACTION_RISK_ANALYSIS, etc.)
- **Merchant Data**: Complete merchant information integration with MCC codes
- **Brand Selection**: Payment brand control (CARDHOLDER/MERCHANT selection)
- **Partial Reversals**: Amount-specific authorization reversals

### 🔧 **Developer-Friendly Architecture**
- **Plugin System**: Easy endpoint extension with `@register_endpoint`
- **Request Builders**: Clean, testable request construction
- **Configuration-Driven**: CSV-based test definitions with advanced feature support
- **Comprehensive Testing**: 267 unit tests with full coverage

### 📊 **Advanced Testing Capabilities**
- **Tag-Based Filtering**: Run specific test subsets (`--tags sca,partial,merchant`)
- **Parallel Execution**: Configurable multi-threading
- **Rich Reporting**: CSV, database, and console output
- **Detailed Logging**: Comprehensive execution tracking

---

## 📋 Quick Navigation

| I want to... | Go here |
|--------------|---------|
| **Run tests immediately** | [User Guide](documentation/user-guide.md) |
| **Set up the environment** | [Environment Setup](documentation/environment-setup.md) |
| **Configure test scenarios** | [Configuration Guide](documentation/configuration-guide.md) |
| **Understand CLI options** | [CLI Reference](documentation/cli-reference.md) |
| **Write custom tests** | [Testing Guide](documentation/testing-guide.md) |
| **Extend the framework** | [Developer Guide](documentation/developer-guide.md) |
| **Understand the architecture** | [Architecture Guide](documentation/architecture-guide.md) |
| **See what's new** | [Changelog](CHANGELOG.md) |

---

## 🏗️ Project Structure

```
wlacqapitest/
├── 📚 documentation/          # Comprehensive guides
├── ⚙️  config/                # Test configurations
│   ├── static/               # Cards, merchants, environments, merchant data
│   ├── credentials/          # API credentials (secure)
│   └── test_suites/          # Test definitions
├── 🔧 src/                   # Core framework
│   ├── core/                 # Core managers (DCC, registry, etc.)
│   ├── endpoints/            # API endpoint implementations
│   ├── request_builders/     # Request construction logic
│   └── config/               # Configuration management
├── 🧪 tests/                 # Unit test suite (267 tests)
├── 📊 outputs/               # Test results and logs
└── 📜 scripts/               # Utility scripts
```

---

## 💡 Usage Examples

### Basic Payment Test
```bash
# Run all smoke tests
python -m src.main --tests smoke_tests.csv

# Run specific test
python -m src.main --tests smoke_tests.csv --test-ids API0001
```

### Advanced Scenarios
```bash
# SCA exemption scenarios
python -m src.main --tests regression.csv --tags sca

# Partial capture workflows
python -m src.main --tests regression.csv --tags partial

# Merchant data integration
python -m src.main --tests regression.csv --tags merchant

# Brand selection testing
python -m src.main --tests regression.csv --tags brand

# DCC-enabled payment chain
python -m src.main --tests smoke_tests.csv --tags dcc

# 3D Secure payments
python -m src.main --tests smoke_tests.csv --tags 3ds

# Combined feature testing
python -m src.main --tests regression.csv --tags "sca,partial,merchant"

# Parallel execution
python -m src.main --tests smoke_tests.csv --threads 4

# Verbose debugging
python -m src.main --tests smoke_tests.csv --verbose --log-level DEBUG
```

### Test Configuration
```csv
chain_id,test_id,call_type,amount,currency,threed_secure_data,merchant_data,brand_selector,is_final,tags
sca_chain,SCA001,create_payment,25,EUR,LVP_NO3DS,RESTAURANT_EU,MERCHANT,,"sca,merchant"
partial_chain,PAR001,create_payment,1000,EUR,,DEFAULT_MERCHANT,,,"partial"
partial_chain,PAR002,capture_payment,300,EUR,,,,false,"partial"
partial_chain,PAR003,capture_payment,700,EUR,,,,true,"partial"
```

---

## 🔥 What's New in v2.2.0

### 🎯 Enhanced API Properties
- **Partial Operations**: Complete partial capture and reversal support with `isFinal` flag
- **SCA Compliance**: European Strong Customer Authentication exemption requests
- **Merchant Data**: Comprehensive merchant information with category codes and location data
- **Brand Selection**: Payment brand selection control across all card-based endpoints

### 📊 Advanced Configuration
- **New CSV Files**: `merchantdata.csv` for merchant information management
- **Enhanced 3DS**: `threeddata.csv` with SCA exemption support
- **Flexible Operations**: Support for exemption-only scenarios and partial workflows

### 🔧 Framework Enhancements
- **Request Builder Extensions**: All builders enhanced with new API properties
- **Comprehensive Testing**: 267 unit tests covering all new functionality
- **Backward Compatibility**: All existing functionality preserved

**📖 Full details in [Changelog](CHANGELOG.md)**

---

## 🛠️ For Developers

### Adding New API Properties
```python
# In request builder
if pd.notna(row.get('brand_selector')):
    card_payment_data.brand_selector = row['brand_selector']

if pd.notna(row.get('merchant_data')) and merchantdata is not None:
    apply_merchant_data(request, row, merchantdata)
```

### Partial Operations Support
```python
# Partial capture with sequence control
if pd.notna(row.get('is_final')):
    request.is_final = str(row['is_final']).upper() == 'TRUE'

if pd.notna(row.get('capture_sequence_number')):
    request.capture_sequence_number = int(row['capture_sequence_number'])
```

### SCA Exemption Integration
```python
# Apply SCA exemption
if pd.notna(threed_row.get('sca_exemption_requested')):
    request.card_payment_data.ecommerce_data.sca_exemption_request = threed_row['sca_exemption_requested']
```

**📖 Complete development guide: [Developer Guide](documentation/developer-guide.md)**

---

## 🏛️ For Architects

This framework implements several key architectural patterns:

- **🔌 Plugin Architecture**: Dynamic endpoint discovery and registration
- **🏗️ Builder Pattern**: Consistent request construction with feature composition
- **🔄 Chain of Responsibility**: Sequential feature application (DCC, 3DS, AVS, SCA, Merchant Data)
- **📋 Registry Pattern**: Centralized endpoint and capability management
- **🎯 Strategy Pattern**: Endpoint-specific implementations with common interfaces
- **📊 Data-Driven Configuration**: CSV-based feature and property management

**📖 Complete architectural overview: [Architecture Guide](documentation/architecture-guide.md)**

---

## 📚 Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [User Guide](documentation/user-guide.md) | Getting started, basic usage, advanced features | End users, testers |
| [Environment Setup](documentation/environment-setup.md) | Installation and configuration | All users |
| [Configuration Guide](documentation/configuration-guide.md) | Test scenarios, CSV files, API properties | Test creators |
| [CLI Reference](documentation/cli-reference.md) | Command-line options | All users |
| [Testing Guide](documentation/testing-guide.md) | Writing and managing tests | Test developers |
| [Developer Guide](documentation/developer-guide.md) | Extending the framework | Developers |
| [Architecture Guide](documentation/architecture-guide.md) | System design and patterns | Architects, senior devs |

---

## 🧪 Testing

```bash
# Run all unit tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test category
pytest tests/test_request_builders/ -v

# Test new API properties
pytest tests/test_request_builders/test_create_payment.py::TestBuildCreatePaymentRequest::test_build_with_sca_exemption_only -v

# Performance testing with advanced features
python -m src.main --tests regression.csv --threads 8 --tags "partial,sca" --verbose
```

**Current Status**: 267/267 tests passing ✅

---

## 📋 Requirements

- **Python**: 3.9 or higher
- **Dependencies**: See [requirements.txt](requirements.txt)
- **API Access**: Worldline Acquiring API credentials
- **Environment**: macOS, Linux, Windows (with Python)

**📖 Detailed setup: [Environment Setup](documentation/environment-setup.md)**

---

## 🔒 Security

- **Credentials**: Stored in `config/credentials/` (gitignored)
- **API Keys**: Environment-specific configuration
- **HTTPS**: All API communication encrypted
- **Token Management**: Automatic OAuth2 token refresh
- **SCA Compliance**: Full European Strong Customer Authentication support

**📖 Security details: [Configuration Guide](documentation/configuration-guide.md#security)**

---

## 🤝 Contributing

1. **Check the guides**: [Developer Guide](documentation/developer-guide.md) for code patterns
2. **Follow the architecture**: [Architecture Guide](documentation/architecture-guide.md) for design principles  
3. **Update documentation**: Keep guides current with changes
4. **Add tests**: Maintain 100% test coverage (currently 267/267 tests)
5. **Update changelog**: Document changes in [CHANGELOG.md](CHANGELOG.md)

---

## 📞 Support

- **📖 Documentation**: Start with [User Guide](documentation/user-guide.md)
- **🐛 Issues**: Check existing issues or create new ones
- **💡 Feature Requests**: Use issue templates
- **❓ Questions**: Check documentation first, then create discussion

---

## 📄 License

[License details to be added]

---

## 🏷️ Release Information

- **Current Version**: 2.2.0
- **Release Date**: August 15, 2025
- **Major Features**: Advanced API Properties, SCA Compliance, Merchant Data, Partial Operations
- **Test Coverage**: 267/267 tests passing
- **Compatibility**: Fully backward compatible with v2.1.0

**📖 Full release history: [Changelog](CHANGELOG.md)**

---

*Built with ❤️ for comprehensive payment API testing*