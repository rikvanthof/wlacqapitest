# Payment API Testing Framework

**Comprehensive test automation for Worldline Acquiring API (v1.3.0)**

A production-ready testing framework supporting advanced payment features, chain execution, parallel processing, and comprehensive validation with CSV-driven configuration.

## Features

### Payment Types Supported
- Create Payment - Authorization and capture
- Increment Payment - Authorization adjustments  
- Capture Payment - Settlement processing
- Refund Payment - Full and partial refunds
- Get Payment/Refund - Status inquiries

### Advanced Payment Features
- Address Verification (AVS) - Cardholder address validation
- 3D Secure Authentication - Strong customer authentication
- Network Token Payments - Apple Pay, Google Pay support
- Card-on-File (UCOF) - Initial and subsequent transactions
- Chain Execution - Multi-step payment scenarios
- Tag-based Filtering - Targeted test execution

### Testing Capabilities
- Comprehensive Assertions - Response validation engine
- Parallel Execution - Configurable thread-based testing
- CSV-driven Configuration - Environment and test management
- Results Dashboard - Real-time test monitoring
- Database Integration - SQLite results storage

## Quick Setup

### 1. Environment Setup

Clone repository and create virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

Configure your test environment in the config directory with these files:
- environments.csv - API endpoints and credentials
- cards.csv - Test card configurations
- merchants.csv - Merchant account details
- address.csv - AVS test addresses
- networktokens.csv - Apple Pay/Google Pay tokens
- threeddata.csv - 3D Secure test data
- cardonfile.csv - Card-on-File configurations

### 3. Run Tests

Basic execution:
```bash
python -m src.main
```

With specific test suite:
```bash
python -m src.main --tests smoke_tests.csv
```

With tags:
```bash
python -m src.main --tags ucof,3ds
```

Parallel execution:
```bash
python -m src.main --threads 4
```

## Usage Examples

### Feature-Specific Testing

Test Card-on-File scenarios:
```bash
python -m src.main --tags ucof
```

Test 3D Secure flows:
```bash
python -m src.main --tags 3ds
```

Test Network Token payments:
```bash
python -m src.main --tags applepay,googlepay
```

## Results & Monitoring

### Results Output
- CSV Reports: outputs/results.csv
- Database: outputs/local.db  
- Logs: Console output with configurable verbosity

### Dashboard
Launch interactive dashboard:
```bash
python src/dashboard.py
```
Then open browser to http://localhost:8050

## Project Structure

```
AcquiringAPI_Tester/
├── config/
├── src/
├── outputs/
├── tests/
└── requirements.txt
```

## Configuration Guide

### Test CSV Format
Basic test definition with essential columns:

```csv
chain_id,step_order,call_type,test_id,tags,card_id,amount,currency
chain1,1,create_payment,TEST001,smoke,visa_card,100,GBP
chain1,2,capture_payment,TEST002,smoke,,,,
```

### Environment Configuration
Environment setup with connection details:

```csv
env,integrator,endpoint_host,client_id,client_secret
test,Test Integrator,api.test.com,test-client,test-secret
```

## Card-on-File (UCOF) Testing

### Initial COF Transaction
```csv
chain_id,step_order,call_type,test_id,tags,card_on_file_data
ucof1,1,create_payment,INITIAL_COF,ucof,FIRSTUCOF-CIT
```

### Subsequent COF Transaction
```csv
chain_id,step_order,call_type,test_id,tags,card_on_file_data
ucof1,2,create_payment,SUBSEQUENT_COF,ucof,SUBSEQUENTUCOF-CIT
```

The framework automatically:
- Extracts schemeTransactionId from initial COF responses
- Links subsequent transactions via initialSchemeTransactionId
- Handles both CIT and MIT transaction flows

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch  
5. Submit pull request

## Support

For issues, questions, or contributions:
- Create GitHub issues for bugs/features
- Check documentation in docs/ directory
- Review test examples in config/test_suites/

Built for comprehensive Worldline Acquiring API testing with enterprise-grade reliability.