# Environment Setup Guide

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Project Setup](#project-setup)
- [Initial Configuration](#initial-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Overview

This guide walks you through setting up a complete development environment for the Payment API Testing Framework. By the end of this guide, you'll have a fully functional testing environment ready to execute comprehensive payment API tests including Card-on-File, 3D Secure, Network Tokens, and Address Verification.

> **⏱️ Estimated Setup Time:** 15-30 minutes depending on your system and internet connection.

## Prerequisites

### System Requirements

| Component | Minimum Version | Recommended Version | Notes |
|-----------|----------------|-------------------|-------|
| Python | 3.8 | 3.9+ | Required for framework execution |
| pip | 20.0 | Latest | Python package manager |
| Git | 2.20 | Latest | Version control (optional) |
| RAM | 4GB | 8GB+ | For parallel test execution |
| Disk Space | 500MB | 1GB+ | For dependencies and test results |

### Check Current Python Installation

**Windows:**
```cmd
# Check Python version
python --version
# or
python3 --version

# Check pip version
pip --version
# or
pip3 --version
```

**macOS:**
```bash
# Check Python version
python3 --version

# Check pip version
pip3 --version

# If Python 3 is not installed, install via Homebrew:
brew install python3
```

**Linux:**
```bash
# Check Python version
python3 --version

# Check pip version
pip3 --version

# If Python 3 is not installed (Ubuntu/Debian):
sudo apt update
sudo apt install python3 python3-pip

# If Python 3 is not installed (CentOS/RHEL):
sudo yum install python3 python3-pip
```

## Installation Steps

### Step 1: Create Project Directory

Create a dedicated directory for the payment testing framework:

```bash
# Create project directory
mkdir payment-api-tester
cd payment-api-tester

# Verify you're in the correct directory
pwd
```

### Step 2: Create Python Virtual Environment

Create an isolated Python environment for the project:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Verify activation (should show virtual environment path)
which python
```

> **✅ Success Indicator:** Your command prompt should now show `(venv)` at the beginning, indicating the virtual environment is active.

### Step 3: Install Core Dependencies

Install the required Python packages:

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install core dependencies
pip install pandas==2.1.0
pip install sqlalchemy==2.0.20
pip install worldline-acquiring-sdk-python==1.3.0

# Install testing dependencies
pip install pytest==7.4.0
pip install pytest-cov==4.1.0
pip install pytest-mock==3.11.1

# Install dashboard dependencies (optional)
pip install dash==2.14.0
pip install plotly==5.15.0

# Create requirements file for future reference
pip freeze > requirements.txt
```

### Step 4: Create Project Structure

Set up the directory structure for the framework:

```bash
# Create main directories
mkdir src
mkdir config
mkdir outputs
mkdir tests
mkdir documentation

# Create source code subdirectories
mkdir src/core
mkdir src/endpoints
mkdir src/request_builders
mkdir config/static
mkdir config/test_suites

# Create initial files
touch src/__init__.py
touch src/main.py
touch src/data_loader.py
touch src/utils.py
touch src/api_calls.py
touch src/results_handler.py
touch src/response_utils.py
touch src/request_builders/__init__.py
touch src/core/__init__.py
touch src/endpoints/__init__.py

# Create configuration files
touch config/static/environments.csv
touch config/static/merchants.csv
touch config/static/cards.csv
touch config/static/address.csv
touch config/static/networktokens.csv
touch config/static/threeddata.csv
touch config/static/cardonfile.csv
touch config/test_suites/smoke_tests.csv
```

Your project structure should now look like this:

```
payment-api-tester/
├── venv/                           # Virtual environment
├── src/                            # Source code
│   ├── __init__.py
│   ├── main.py
│   ├── data_loader.py
│   ├── utils.py
│   ├── api_calls.py
│   ├── results_handler.py
│   ├── response_utils.py
│   ├── core/                       # Core framework components
│   │   ├── __init__.py
│   │   ├── endpoint_registry.py
│   │   └── payment_assertions.py
│   ├── endpoints/                  # API endpoint implementations
│   │   ├── __init__.py
│   │   └── create_payment_endpoint.py
│   └── request_builders/           # Request construction logic
│       ├── __init__.py
│       └── create_payment.py
├── config/                         # Configuration files
│   ├── static/                     # Static configuration
│   │   ├── environments.csv
│   │   ├── merchants.csv
│   │   ├── cards.csv
│   │   ├── address.csv
│   │   ├── networktokens.csv
│   │   ├── threeddata.csv
│   │   └── cardonfile.csv
│   └── test_suites/               # Test scenario definitions
│       ├── smoke_tests.csv
│       ├── regression.csv
│       └── ucof_tests.csv
├── outputs/                        # Test results (created automatically)
├── tests/                          # Unit tests
├── documentation/                  # Documentation files
└── requirements.txt               # Python dependencies
```

## Project Setup

### Step 5: Copy Framework Code

Copy the payment testing framework source code into the appropriate directories. The framework includes:

**Core Files:**
- `src/main.py` - Main execution entry point
- `src/data_loader.py` - Configuration loading logic
- `src/utils.py` - Utility functions
- `src/api_calls.py` - API interaction logic
- `src/results_handler.py` - Results processing
- `src/response_utils.py` - Response parsing utilities

**Advanced Feature Files:**
- `src/cardonfile.py` - Card-on-File data application
- `src/avs.py` - Address verification logic
- `src/threed_secure.py` - 3D Secure authentication
- `src/network_tokens.py` - Network token handling

**Core Framework:**
- `src/core/endpoint_registry.py` - Endpoint registration system
- `src/core/payment_assertions.py` - Response validation engine

**Request Builders:**
- `src/request_builders/create_payment.py` - Payment request construction
- `src/request_builders/increment_payment.py` - Increment request construction
- `src/request_builders/capture_payment.py` - Capture request construction
- `src/request_builders/refund_payment.py` - Refund request construction

> **💡 Code Source:** Ensure you have all the Python files and copy them to the appropriate directories as shown in the project structure above.

### Step 6: Copy Unit Tests

Copy the unit test files to the `tests/` directory:

```bash
# Example test files to copy:
# tests/conftest.py - Shared test fixtures
# tests/test_data_loader.py - Data loading tests
# tests/test_response_utils.py - Response processing tests
# tests/test_results_handler.py - Results handling tests
# tests/test_utils.py - Utility function tests
# tests/test_request_builders/ - Request builder tests
#   ├── test_create_payment.py
#   ├── test_increment_payment.py
#   ├── test_capture_payment.py
#   └── test_refund_payment.py
```

## Initial Configuration

### Step 7: Configure Environment

Set up your environment configuration file with your Worldline API credentials:

**Edit `config/static/environments.csv`:**
```csv
env,integrator,endpoint_host,authorization_type,oauth2_token_uri,connect_timeout,socket_timeout,max_connections,client_id,client_secret
preprod,Your Integration Name,api.preprod.acquiring.worldline-solutions.com,OAuth2,https://auth-test-eu-west-1.aws.bambora.com/connect/token,5,300,10,YOUR_CLIENT_ID,YOUR_CLIENT_SECRET
prod,Your Integration Name,api.acquiring.worldline-solutions.com,OAuth2,https://auth-eu-west-1.aws.bambora.com/connect/token,5,300,10,YOUR_PROD_CLIENT_ID,YOUR_PROD_CLIENT_SECRET
```

> **⚠️ Important:** Replace `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` with your actual Worldline API credentials. Never commit real credentials to version control.

### Step 8: Configure Test Merchants

**Edit `config/static/merchants.csv`:**
```csv
merchant,env,acquirer_id,merchant_id,merchant_description
merchant1,preprod,YOUR_ACQUIRER_ID,YOUR_MERCHANT_ID,Test Merchant Description
merchant1,prod,YOUR_ACQUIRER_ID,YOUR_PROD_MERCHANT_ID,Production Merchant Description
```

> **📝 Note:** Replace with your actual acquirer and merchant IDs provided by Worldline for testing.

### Step 9: Configure Test Cards

**Edit `config/static/cards.csv`:**
```csv
card_id,card_brand,card_bin,card_number,expiry_date,card_sequence_number,card_security_code,card_pin,card_description
visa_card,VISA,411111,4111111111111111,122025,,123,,Test Visa Card
mc_card,MASTERCARD,522222,5222222222222222,122025,,456,,Test Mastercard
visa_premium,VISA,411111,4111111111111111,122025,001,123,1234,VISA Premium Test Card
```

> **⚠️ Test Cards Only:** Only use test card numbers provided by Worldline. Never use real card numbers in testing.

### Step 10: Configure Advanced Payment Features

**Edit `config/static/address.csv`:**
```csv
address_id,cardholder_postal_code,cardholder_address
AVS_FULL,8021,Hardturmstrasse 201
AVS_PARTIAL,SW1A 1AA,123 Test Street
AVS_NOMATCH,00000,Invalid Address
```

**Edit `config/static/cardonfile.csv`:**
```csv
card_on_file_id,is_initial_transaction,transaction_type,card_on_file_initiator,future_use
FIRSTUCOF-CIT,TRUE,UNSCHEDULED_CARD_ON_FILE,,CARDHOLDER_INITIATED
SUBSEQUENTUCOF-CIT,FALSE,UNSCHEDULED_CARD_ON_FILE,CARDHOLDER,
SUBSEQUENTUCOF-MIT,FALSE,UNSCHEDULED_CARD_ON_FILE,MERCHANT,
```

**Edit `config/static/threeddata.csv`:**
```csv
three_d_id,three_d_secure_type,authentication_value,eci,version
VISA_FULL,THREE_DS,AAABBEg0VhI0VniQEjRWAAAAAAA=,05,2.2.0
MASTERCARD_FULL,THREE_DS,AAABBEg0VhI0VniQEjRWAAAAAAA=,02,2.2.0
VISA_ATTEMPTED,THREE_DS_ATTEMPTED,AAABBEg0VhI0VniQEjRWAAAAAAA=,06,2.2.0
```

### Step 11: Create Sample Test Suite

**Edit `config/test_suites/smoke_tests.csv`:**
```csv
chain_id,step_order,call_type,test_id,tags,card_id,merchant_id,env,amount,currency,authorization_type,capture_immediately,card_entry_mode,cardholder_verification_method,address_data,threed_secure_data,card_on_file_data,expected_http_status,expected_response_code
smoke1,1,create_payment,SMOKE001,smoke,visa_card,merchant1,preprod,1000,GBP,FINAL_AUTHORIZATION,FALSE,ECOMMERCE,CARD_SECURITY_CODE,,,201,0
smoke1,2,capture_payment,SMOKE002,smoke,,,preprod,1000,GBP,,,,,,,201,0
ucof_smoke,1,create_payment,UCOF001,ucof,visa_card,merchant1,preprod,500,GBP,FINAL_AUTHORIZATION,TRUE,ECOMMERCE,THREE_DS,AVS_FULL,VISA_FULL,FIRSTUCOF-CIT,201,0
ucof_smoke,2,create_payment,UCOF002,ucof,visa_card,merchant1,preprod,250,GBP,FINAL_AUTHORIZATION,TRUE,ECOMMERCE,THREE_DS,AVS_FULL,VISA_FULL,SUBSEQUENTUCOF-CIT,201,0
```

## Verification

### Step 12: Verify Installation

Test that everything is set up correctly:

**Test Python Environment:**
```bash
# Verify virtual environment is active
which python
which pip

# Check installed packages
pip list

# Test import of key dependencies
python -c "import pandas; print('Pandas:', pandas.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
python -c "from worldline.acquiring.sdk.factory import Factory; print('Worldline SDK: OK')"
```

**Test Configuration Loading:**
```bash
# Test configuration file loading
python -c "
from src.config.config_manager import ConfigurationManager
config_manager = ConfigurationManager()
config_set = config_manager.load_all_configs('config/test_suites/smoke_tests.csv')
print('✅ Configuration loading: OK')
print(f'Cards loaded: {len(config_set.cards)}')
print(f'Tests loaded: {len(config_set.tests)}')
"
```

**Run Unit Tests:**
```bash
# Run all unit tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src

# Run specific test file
pytest tests/test_utils.py -v
```

### Step 13: Test Basic Execution

Try a dry run of the framework:

```bash
# Run help command
python -m src.main --help

# Test configuration loading
python -m src.main --tests smoke_tests.csv --verbose

# Test with specific tags
python -m src.main --tags smoke --verbose

# Test Card-on-File features
python -m src.main --tags ucof --verbose
```

> **ℹ️ Expected Behavior:** The framework should start and attempt to load configuration. API calls may fail if credentials aren't properly configured, but the framework should handle errors gracefully and provide meaningful error messages.

## Troubleshooting

### Common Issues and Solutions

#### ImportError: No module named 'src'

**Solution:** Make sure you're running from the project root directory and using `python -m src.main` instead of `python src/main.py`

```bash
# Check current directory
pwd
# Should show: /path/to/payment-api-tester

# Run from project root
python -m src.main
```

#### Virtual Environment Not Active

**Symptoms:** Command prompt doesn't show `(venv)`

**Solution:** Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Package Installation Fails

**Solution:** Upgrade pip and try again:

```bash
# Upgrade pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install with no cache
pip install --no-cache-dir package-name

# Alternative: Install from requirements file
pip install -r requirements.txt
```

#### Configuration File Errors

**Symptoms:** "Environment X not defined" or "Merchant Y not defined"

**Solution:** Check CSV file format and content:

```bash
# Validate CSV files
python -c "import pandas as pd; df = pd.read_csv('config/static/environments.csv'); print(df.head())"
python -c "import pandas as pd; df = pd.read_csv('config/static/merchants.csv'); print(df.head())"

# Check for encoding issues
file config/static/environments.csv
```

#### API Authentication Errors

**Symptoms:** HTTP 401 or authentication failures

**Solutions:**
- Verify client_id and client_secret in environments.csv
- Check that OAuth2 token URI is correct
- Ensure your credentials are valid for the environment
- Test with curl to verify credentials work outside the framework
- Contact Worldline support if credentials are uncertain

```bash
# Test OAuth2 token endpoint
curl -X POST https://auth-test-eu-west-1.aws.bambora.com/connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"
```

#### Advanced Feature Configuration Errors

**Symptoms:** "Card-on-file ID not found" or similar feature-specific errors

**Solution:** Verify advanced feature configuration files:

```bash
# Check Card-on-File configuration
python -c "import pandas as pd; df = pd.read_csv('config/static/cardonfile.csv'); print(df.head())"

# Check 3D Secure configuration
python -c "import pandas as pd; df = pd.read_csv('config/static/threeddata.csv'); print(df.head())"

# Check Address configuration
python -c "import pandas as pd; df = pd.read_csv('config/static/address.csv'); print(df.head())"
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:** Run with `--verbose` flag for detailed output
2. **Verify configuration:** Double-check all CSV files for formatting and content
3. **Test components individually:** Run unit tests to isolate issues
4. **Check dependencies:** Ensure all required packages are installed
5. **Review documentation:** Check Configuration Guide and CLI Reference
6. **Test minimal scenarios:** Start with simple tests before complex chains

## Next Steps

### 🎉 Environment Setup Complete!

Your Payment API Testing Framework environment is now ready. Here's what to do next:

#### 1. Review Documentation
- **Configuration Guide** - Detailed CSV configuration for all features
- **CLI Reference** - Complete command-line options and usage
- **User Guide** - Advanced usage patterns and best practices

#### 2. Configure Your Tests
- Add your actual Worldline API credentials
- Configure merchants for your specific environments
- Create comprehensive test scenarios in test_suites/
- Set up advanced payment features (UCOF, 3DS, Network Tokens)

#### 3. Run Your First Tests

```bash
# Start with smoke tests
python -m src.main --tests smoke_tests.csv --verbose

# Test specific features
python -m src.main --tags ucof --verbose
python -m src.main --tags 3ds --verbose

# Use parallel execution for larger test suites
python -m src.main --tests regression.csv --threads 3
```

#### 4. Scale Up Testing
- Add more complex test chains with multiple steps
- Use parallel execution with `--threads` for faster feedback
- Set up automated test schedules using cron or CI/CD
- Integrate with your existing testing infrastructure

#### 5. Monitor and Analyze Results
- Review results in `outputs/results.csv`
- Use the SQLite database in `outputs/local.db` for analysis
- Set up the optional dashboard for real-time monitoring
- Create reports for stakeholders

### Quick Reference Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Run tests with default settings
python -m src.main

# Run specific test suite with features
python -m src.main --tests smoke_tests.csv --tags ucof,3ds --verbose

# Run tests with parallel execution
python -m src.main --tests regression.csv --threads 4 --verbose

# Run unit tests
pytest -v --cov=src

# View latest results
cat outputs/results.csv | head -10

# Check test history in database
sqlite3 outputs/local.db "SELECT test_id, pass, duration_ms FROM results ORDER BY timestamp DESC LIMIT 10;"
```

### Advanced Setup Options

**Dashboard Setup (Optional):**
```bash
# Install dashboard dependencies if not already done
pip install dash plotly

# Launch dashboard
python src/dashboard.py

# Open browser to http://localhost:8050
```

**CI/CD Integration:**
```bash
# Example Jenkins/GitHub Actions command
python -m src.main --tests regression.csv --threads 2 > test_output.log 2>&1
```

**Production Monitoring:**
```bash
# Scheduled testing with logging
0 */4 * * * cd /path/to/payment-api-tester && source venv/bin/activate && python -m src.main --tests monitoring.csv --threads 2 >> logs/scheduled_tests.log 2>&1
```

Your Payment API Testing Framework is now ready for comprehensive testing of Worldline Acquiring API with full support for advanced payment features! 🚀