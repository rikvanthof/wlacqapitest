# Payment API Test Framework

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](requirements.txt)
[![Tests](https://img.shields.io/badge/tests-108%2F108%20passing-brightgreen.svg)](#testing)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](documentation/)

A comprehensive Python testing framework for Worldline Acquiring payment APIs, supporting complex payment workflows, Dynamic Currency Conversion (DCC), and advanced payment features.

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

# Run with DCC
python -m src.main --tests smoke_tests.csv --tags dcc --verbose
```

**📖 New to the framework?** Start with the [User Guide](documentation/user-guide.md) | **🔧 Setting up?** See [Environment Setup](documentation/environment-setup.md)

---

## ✨ Key Features

### 💳 **Comprehensive Payment Support**
- **Core Operations**: Create, capture, increment, and refund payments
- **Chain Workflows**: Multi-step payment scenarios with shared context
- **Advanced Features**: 3D Secure, AVS, Network Tokens, Card-on-File

### 🌍 **Dynamic Currency Conversion (DCC)** ⭐ *New in v2.1.0*
- Automatic currency conversion rate inquiry
- Multi-currency payment chain support
- Real-time exchange rate integration
- Consistent DCC handling across all payment types

### 🔧 **Developer-Friendly Architecture**
- **Plugin System**: Easy endpoint extension with `@register_endpoint`
- **Request Builders**: Clean, testable request construction
- **Configuration-Driven**: CSV-based test definitions
- **Comprehensive Testing**: 108 unit tests with full coverage

### 📊 **Advanced Testing Capabilities**
- **Tag-Based Filtering**: Run specific test subsets (`--tags dcc,3ds`)
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
│   ├── static/               # Cards, merchants, environments
│   ├── credentials/          # API credentials (secure)
│   └── test_suites/          # Test definitions
├── 🔧 src/                   # Core framework
│   ├── core/                 # Core managers (DCC, registry, etc.)
│   ├── endpoints/            # API endpoint implementations
│   ├── request_builders/     # Request construction logic
│   └── config/               # Configuration management
├── 🧪 tests/                 # Unit test suite
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
# DCC-enabled payment chain
python -m src.main --tests smoke_tests.csv --tags dcc

# 3D Secure payments
python -m src.main --tests smoke_tests.csv --tags 3ds

# Parallel execution
python -m src.main --tests smoke_tests.csv --threads 4

# Verbose debugging
python -m src.main --tests smoke_tests.csv --verbose --log-level DEBUG
```

### Test Configuration
```csv
chain_id,test_id,call_type,amount,currency,dcc_target_currency,tags
chain1,API0001,create_payment,1000,GBP,EUR,"dcc,smoke"
chain1,API0002,capture_payment,500,GBP,EUR,"dcc,smoke"
```

---

## 🔥 What's New in v2.1.0

### 🌍 Dynamic Currency Conversion
- **Complete DCC Integration**: Automatic rate inquiry and conversion
- **Chain Context**: DCC data flows seamlessly across payment steps
- **Real-world Testing**: Multi-currency scenarios with actual exchange rates

### 🏗️ Enhanced Architecture
- **Request Builder Pattern**: Centralized, testable request construction
- **Plugin Registry**: Easy endpoint extension without core changes
- **Improved Documentation**: Comprehensive guides for all user types

**📖 Full details in [Changelog](CHANGELOG.md)**

---

## 🛠️ For Developers

### Adding New Endpoints
```python
@register_endpoint('new_endpoint')
class NewEndpoint(EndpointInterface):
    @staticmethod
    def build_request(row, **kwargs):
        return build_new_request(row, **kwargs)
    
    @staticmethod
    def supports_dcc() -> bool:
        return True
```

### Creating Request Builders
```python
def build_new_request(row, dcc_context=None):
    request = ApiNewRequest()
    # Build request logic
    if dcc_context:
        apply_dcc_data(request, dcc_context, row)
    return clean_request(request)
```

**📖 Complete development guide: [Developer Guide](documentation/developer-guide.md)**

---

## 🏛️ For Architects

This framework implements several key architectural patterns:

- **🔌 Plugin Architecture**: Dynamic endpoint discovery and registration
- **🏗️ Builder Pattern**: Consistent request construction with feature composition
- **🔄 Chain of Responsibility**: Sequential feature application (DCC, 3DS, AVS)
- **📋 Registry Pattern**: Centralized endpoint and capability management
- **🎯 Strategy Pattern**: Endpoint-specific implementations with common interfaces

**📖 Complete architectural overview: [Architecture Guide](documentation/architecture-guide.md)**

---

## 📚 Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [User Guide](documentation/user-guide.md) | Getting started, basic usage | End users, testers |
| [Environment Setup](documentation/environment-setup.md) | Installation and configuration | All users |
| [Configuration Guide](documentation/configuration-guide.md) | Test scenarios and settings | Test creators |
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
pytest tests/test_dcc_integration.py -v

# Performance testing
python -m src.main --tests smoke_tests.csv --threads 8 --verbose
```

**Current Status**: 108/108 tests passing ✅

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

**📖 Security details: [Configuration Guide](documentation/configuration-guide.md#security)**

---

## 🤝 Contributing

1. **Check the guides**: [Developer Guide](documentation/developer-guide.md) for code patterns
2. **Follow the architecture**: [Architecture Guide](documentation/architecture-guide.md) for design principles  
3. **Update documentation**: Keep guides current with changes
4. **Add tests**: Maintain 100% test coverage
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

- **Current Version**: 2.1.0
- **Release Date**: August 15, 2025
- **Major Features**: Dynamic Currency Conversion, Request Builder Pattern
- **Compatibility**: Fully backward compatible with v2.0.0

**📖 Full release history: [Changelog](CHANGELOG.md)**

---

*Built with ❤️ for comprehensive payment API testing*