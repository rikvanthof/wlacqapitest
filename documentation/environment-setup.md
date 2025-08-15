# Environment Setup Guide

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Configuration Setup](#configuration-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Overview

This guide walks you through setting up the Payment API Testing Framework from scratch. By the end, you'll have a fully functional testing environment ready to execute comprehensive payment API tests including Card-on-File, 3D Secure, Network Tokens, Address Verification, SCA Exemptions, Merchant Data, Partial Operations, and Brand Selection.

> **⏱️ Estimated Setup Time:** 10-20 minutes depending on your system and internet connection.

## Prerequisites

### System Requirements

| Component | Minimum Version | Recommended Version | Notes |
|-----------|----------------|-------------------|-------|
| Python | 3.8 | 3.9+ | Required for framework execution |
| pip | 20.0 | Latest | Python package manager |
| Git | 2.20 | Latest | For cloning the repository |
| RAM | 4GB | 8GB+ | For parallel test execution |
| Disk Space | 500MB | 1GB+ | For dependencies and test results |

### Check Current Python Installation

**Windows:**
```cmd
python --version
pip --version
```

**macOS/Linux:**
```bash
python3 --version
pip3 --version
```

> **📝 Note:** On macOS/Linux, you may need to use `python3` and `pip3` instead of `python` and `pip`.

## Installation Steps

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url> wlacqapitest
cd wlacqapitest

# Or if you have the project files
# Extract/copy the project to a directory called wlacqapitest
cd wlacqapitest
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python
```

> **✅ Success Indicator:** Your command prompt should show `(venv)` prefix.

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

**Dependencies installed:**
- `acquiring-sdk-python` - Worldline Acquiring SDK
- `pandas` - Data manipulation and analysis
- `sqlalchemy` - Database toolkit
- `flask` - Web framework (for dashboard)
- `dash` - Dashboard framework
- `plotly` - Interactive plotting

### Step 4: Verify Project Structure

Your project should look like this:

```
wlacqapitest/
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── pytest.ini
├── config/
│   ├── credentials/
│   │   ├── README.md
│   │   ├── secrets.csv.template
│   │   └── secrets.csv                 # You'll create this
│   ├── static/
│   │   ├── address.csv
│   │   ├── cardonfile.csv
│   │   ├── cards.csv
│   │   ├── environments.csv
│   │   ├── merchantdata.csv
│   │   ├── merchants.csv
│   │   ├── networktoken.csv
│   │   └── threeddata.csv
│   └── test_suites/
│       ├── custom/
│       └── smoke_tests.csv
├── documentation/                      # Comprehensive guides
├── src/                               # Main source code (18 directories, 122 files)
├── tests/                             # Unit tests (267 tests)
├── outputs/                           # Test results (auto-created)
└── scripts/                           # Utility scripts
```

## Configuration Setup

### Step 5: Set Up Credentials

The framework separates sensitive credentials from configuration:

```bash
# Copy the template
cp config/credentials/secrets.csv.template config/credentials/secrets.csv

# Edit with your actual credentials
# Use your preferred editor (nano, vim, VSCode, etc.)
nano config/credentials/secrets.csv
```

**Edit `config/credentials/secrets.csv`:**
```csv
env,client_id,client_secret
dev,your-dev-client-id,your-dev-client-secret
preprod,your-test-client-id,your-test-client-secret
prod,your-prod-client-id,your-prod-client-secret
```

> **⚠️ Security:** Replace with your actual Worldline API credentials. This file is gitignored and won't be committed.

### Step 6: Review Environment Configuration

The environments are already configured in `config/static/environments.csv`:

```csv
env,integrator,endpoint_host,authorization_type,oauth2_token_uri,connect_timeout,socket_timeout,max_connections
dev,Augmented Rik,api.dev.acquiring.worldline-solutions.com,OAuth2,https://auth-test-eu-west-1.aws.bambora.com/connect/token,5,300,10
preprod,Augmented Rik,api.preprod.acquiring.worldline-solutions.com,OAuth2,https://auth-test-eu-west-1.aws.bambora.com/connect/token,5,300,10
```

> **📝 Note:** You can customize the integrator name if needed.

### Step 7: Review Test Configuration

The framework comes with pre-configured test data:

- **Merchants:** `config/static/merchants.csv` - Test merchant configurations
- **Cards:** `config/static/cards.csv` - Test card data (Worldline test cards)
- **Advanced Features:** Pre-configured Card-on-File, 3DS, SCA exemptions, merchant data, etc.

**Check test merchants:**
```bash
head -3 config/static/merchants.csv
```

**Check test cards:**
```bash
head -3 config/static/cards.csv
```

### Step 8: Review Sample Tests

Examine the smoke test configuration:

```bash
head -3 config/test_suites/smoke_tests.csv
```

The test suite includes:
- Basic payment flows
- 3D Secure authentication
- Card-on-File scenarios
- Advanced payment features

## Verification

### Step 9: Test Installation

**Verify Python Environment:**
```bash
# Check virtual environment
which python
pip list

# Test key imports
python -c "import pandas; print('✅ Pandas:', pandas.__version__)"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"
python -c "from worldline.acquiring.sdk.factory import Factory; print('✅ Worldline SDK: OK')"
```

**Test Configuration Loading:**
```bash
python -c "
from src.config.config_manager import ConfigurationManager
config_manager = ConfigurationManager()
try:
    config_set = config_manager.load_all_configs('config/test_suites/smoke_tests.csv')
    print('✅ Configuration loading: OK')
    print(f'📋 Tests loaded: {len(config_set.tests)}')
    print(f'💳 Cards loaded: {len(config_set.cards)}')
    print(f'🏪 Merchants loaded: {len(config_set.merchants)}')
    print(f'🔒 Environments loaded: {len(config_set.environments)}')
except Exception as e:
    print('❌ Configuration error:', e)
"
```

### Step 10: Run Unit Tests

```bash
# Run all unit tests (267 tests)
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src

# Expected output: 267 tests passing
```

### Step 11: Test Basic Framework Execution

```bash
# Test help command
python -m src.main --help

# Test configuration validation (should show help and validate configs)
python -m src.main --tests smoke_tests.csv --verbose
```

> **ℹ️ Expected Behavior:** Framework should start, load configurations, and show help. API calls will require valid credentials to execute fully.

### Step 12: Test with Valid Credentials

If you have valid Worldline API credentials:

```bash
# Run smoke tests
python -m src.main --tests smoke_tests.csv --tags smoke --verbose

# Test specific features
python -m src.main --tags "smoke,visa" --verbose
```

## Troubleshooting

### Common Issues

#### 1. Virtual Environment Not Active
**Symptoms:** Commands fail with import errors, `(venv)` not shown in prompt

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

#### 2. Missing Dependencies
**Symptoms:** `ModuleNotFoundError` when running tests

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check what's installed
pip list
```

#### 3. Configuration File Not Found
**Symptoms:** "secrets.csv not found" or similar errors

**Solution:**
```bash
# Ensure secrets file exists
ls -la config/credentials/

# Copy template if missing
cp config/credentials/secrets.csv.template config/credentials/secrets.csv
```

#### 4. Invalid Credentials
**Symptoms:** HTTP 401 errors, authentication failures

**Solution:**
- Verify `config/credentials/secrets.csv` has correct client_id and client_secret
- Ensure credentials match the environment (dev/preprod/prod)
- Test credentials with Worldline support if uncertain

#### 5. Import Errors
**Symptoms:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Ensure you're in the project root directory
pwd
# Should show: /path/to/wlacqapitest

# Run from project root using module syntax
python -m src.main
```

### Getting Help

1. **Check verbose output:** Add `--verbose` to see detailed execution logs
2. **Run unit tests:** `pytest -v` to verify core functionality
3. **Check configuration:** Verify all CSV files have correct headers and data
4. **Review documentation:** Check other guides in `documentation/` folder

## Next Steps

### 🎉 Setup Complete!

Your Payment API Testing Framework is ready. Here's what to do next:

#### 1. Explore the Framework

```bash
# See all available options
python -m src.main --help

# Run specific test types
python -m src.main --tags smoke --verbose
python -m src.main --tags "3ds,ucof" --verbose
python -m src.main --tags "sca,partial,merchant" --verbose
```

#### 2. Review Available Features

**Advanced Payment Features:**
- `--tags ucof` - Card-on-File scenarios
- `--tags 3ds` - 3D Secure authentication  
- `--tags sca` - SCA exemption scenarios
- `--tags partial` - Partial operations (captures, reversals)
- `--tags merchant` - Merchant data integration
- `--tags brand` - Brand selection control

#### 3. Add Your Test Scenarios

```bash
# Create custom test suite
cp config/test_suites/smoke_tests.csv config/test_suites/my_tests.csv
# Edit my_tests.csv with your specific scenarios

# Run your custom tests
python -m src.main --tests my_tests.csv --verbose
```

#### 4. Scale Up Testing

```bash
# Use parallel execution for faster results
python -m src.main --tests smoke_tests.csv --threads 3 --verbose

# Run comprehensive regression testing
python -m src.main --tags regression --threads 2
```

#### 5. Monitor Results

- **CSV Results:** `outputs/results.csv` - Latest test results
- **Database:** `outputs/local.db` - Historical results for analysis  
- **Dashboard:** `python src/dashboard.py` - Optional web dashboard

### Quick Reference Commands

```bash
# Basic execution
python -m src.main

# Feature-specific testing
python -m src.main --tags "sca,partial" --verbose

# Parallel execution
python -m src.main --threads 3 --verbose

# Custom test suite
python -m src.main --tests my_custom_tests.csv --verbose

# Full unit test suite
pytest -v --cov=src
```

### Documentation

Explore the comprehensive documentation in the `documentation/` folder:

- **User Guide** - Advanced usage and features
- **Configuration Guide** - Detailed CSV configuration  
- **CLI Reference** - All command-line options
- **Developer Guide** - Extending the framework
- **Testing Guide** - Unit test details

**Your Payment API Testing Framework is now ready for comprehensive testing! 🚀**