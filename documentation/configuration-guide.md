<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Guide</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        h3 {
            color: #555;
            margin-top: 25px;
        }
        code {
            background-color: #f1f2f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }
        pre {
            background-color: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 15px 0;
        }
        pre code {
            background-color: transparent;
            padding: 0;
            color: inherit;
        }
        .file-tree {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #6c757d;
            font-family: monospace;
            margin: 15px 0;
        }
        .config-file {
            background-color: #e8f5e8;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #4caf50;
        }
        .config-file h4 {
            margin-top: 0;
            color: #2e7d32;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            border-left: 4px solid;
        }
        .alert-info {
            background-color: #e3f2fd;
            border-color: #2196f3;
            color: #0277bd;
        }
        .alert-warning {
            background-color: #fff3e0;
            border-color: #ff9800;
            color: #ef6c00;
        }
        .alert-success {
            background-color: #e8f5e8;
            border-color: #4caf50;
            color: #2e7d32;
        }
        .pattern-box {
            background-color: #f0f4f8;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
            border-left: 4px solid #64b5f6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Configuration Guide</h1>

        <h2>Overview</h2>
        <p>The Payment API Testing Framework uses CSV files for configuration, making it easy to manage test data, environments, and scenarios without code changes.</p>

        <h2>Configuration Directory Structure</h2>
        <div class="file-tree">
config/
├── tests.csv          # Test step definitions (main test file)
├── environments.csv   # API endpoint configurations
├── merchants.csv      # Merchant account settings
├── cards.csv         # Test card data
├── address.csv       # Address data for AVS testing
├── networktoken.csv  # Network tokenization data
└── threeddata.csv    # 3D Secure authentication data
        </div>

        <h2>Core Configuration Files</h2>

        <div class="config-file">
            <h4>1. tests.csv - Test Definitions</h4>
            <p><strong>Purpose:</strong> Defines the sequence of API calls that make up test chains.</p>
            
            <p><strong>Required Columns:</strong></p>
            <ul>
                <li><code>chain_id</code> - Unique identifier for the test chain</li>
                <li><code>step_order</code> - Order of execution within the chain (1, 2, 3...)</li>
                <li><code>call_type</code> - Type of API call to make</li>
                <li><code>test_id</code> - Unique identifier for this test step</li>
                <li><code>card_id</code> - Reference to card in cards.csv (for create_payment)</li>
                <li><code>merchant_id</code> - Reference to merchant in merchants.csv</li>
                <li><code>env</code> - Environment to run in (matches environments.csv)</li>
                <li><code>amount</code> - Transaction amount (where applicable)</li>
                <li><code>currency</code> - Currency code (GBP, EUR, USD, etc.)</li>
            </ul>

            <p><strong>Supported Call Types:</strong></p>
            <ul>
                <li><code>create_payment</code> - Create a new payment</li>
                <li><code>increment_payment</code> - Increment payment authorization</li>
                <li><code>capture_payment</code> - Capture a payment</li>
                <li><code>refund_payment</code> - Refund a payment</li>
                <li><code>get_payment</code> - Retrieve payment status</li>
                <li><code>get_refund</code> - Retrieve refund status</li>
            </ul>

            <p><strong>Example:</strong></p>
            <pre><code>chain_id,step_order,call_type,test_id,card_id,merchant_id,env,amount,currency,authorization_type,capture_immediately
chain1,1,create_payment,PAY001,card01,merchant1,preprod,1000,GBP,FINAL_AUTHORIZATION,FALSE
chain1,2,capture_payment,CAP001,,,preprod,1000,GBP,,
chain1,3,get_payment,GET001,,,preprod,,,</code></pre>
        </div>

        <div class="config-file">
            <h4>2. environments.csv - API Environments</h4>
            <p><strong>Purpose:</strong> Configures API endpoints and authentication for different environments.</p>
            
            <p><strong>Required Columns:</strong></p>
            <ul>
                <li><code>env</code> - Environment identifier (used in tests.csv)</li>
                <li><code>integrator</code> - Integration name</li>
                <li><code>endpoint_host</code> - API hostname</li>
                <li><code>authorization_type</code> - Authentication method (OAuth2)</li>
                <li><code>oauth2_token_uri</code> - OAuth token endpoint</li>
                <li><code>client_id</code> - OAuth client identifier</li>
                <li><code>client_secret</code> - OAuth client secret</li>
                <li><code>connect_timeout</code> - Connection timeout (seconds)</li>
                <li><code>socket_timeout</code> - Socket timeout (seconds)</li>
                <li><code>max_connections</code> - Maximum concurrent connections</li>
            </ul>

            <p><strong>Example:</strong></p>
            <pre><code>env,integrator,endpoint_host,authorization_type,oauth2_token_uri,connect_timeout,socket_timeout,max_connections,client_id,client_secret
preprod,My Integration,api.preprod.acquiring.worldline-solutions.com,OAuth2,https://auth-test-eu-west-1.aws.bambora.com/connect/token,5,300,10,your-client-id,your-client-secret
prod,My Integration,api.acquiring.worldline-solutions.com,OAuth2,https://auth-eu-west-1.aws.bambora.com/connect/token,5,300,10,your-prod-client-id,your-prod-client-secret</code></pre>
        </div>

        <div class="config-file">
            <h4>3. merchants.csv - Merchant Configurations</h4>
            <p><strong>Purpose:</strong> Maps merchant identifiers to actual acquirer and merchant IDs.</p>
            
            <p><strong>Required Columns:</strong></p>
            <ul>
                <li><code>merchant</code> - Friendly merchant identifier (used in tests.csv)</li>
                <li><code>env</code> - Environment this configuration applies to</li>
                <li><code>acquirer_id</code> - Worldline acquirer identifier</li>
                <li><code>merchant_id</code> - Worldline merchant identifier</li>
                <li><code>merchant_description</code> - Descriptive name for reporting</li>
            </ul>

            <p><strong>Example:</strong></p>
            <pre><code>merchant,env,acquirer_id,merchant_id,merchant_description
merchant1,preprod,100812,520001857,Pre-prod ECOM/DCC Test Merchant
merchant1,prod,100812,520009999,Production ECOM Merchant
merchant2,preprod,100812,520001858,Pre-prod POS Test Merchant</code></pre>
        </div>

        <div class="config-file">
            <h4>4. cards.csv - Test Card Data</h4>
            <p><strong>Purpose:</strong> Defines test payment cards with their properties.</p>
            
            <p><strong>Required Columns:</strong></p>
            <ul>
                <li><code>card_id</code> - Unique card identifier (used in tests.csv)</li>
                <li><code>card_brand</code> - Card brand (VISA, MASTERCARD, etc.)</li>
                <li><code>card_number</code> - Full card number</li>
                <li><code>expiry_date</code> - Expiry date (MMYYYY format)</li>
                <li><code>card_description</code> - Descriptive name for reporting</li>
            </ul>

            <p><strong>Optional Columns:</strong></p>
            <ul>
                <li><code>card_bin</code> - Bank Identification Number</li>
                <li><code>card_sequence_number</code> - Card sequence number</li>
                <li><code>card_security_code</code> - CVV/CVC code</li>
                <li><code>card_pin</code> - PIN for chip and PIN transactions</li>
            </ul>

            <p><strong>Example:</strong></p>
            <pre><code>card_id,card_brand,card_bin,card_number,expiry_date,card_sequence_number,card_security_code,card_pin,card_description
card01,VISA,411111,4111111111111111,122025,,123,,Test Visa Card
card02,MASTERCARD,522222,5222222222222222,122025,,456,,Test Mastercard
card03,VISA,411111,4111111111111111,122025,001,123,1234,Visa with Sequence</code></pre>
        </div>

        <h2>Extended Configuration Files</h2>

        <div class="config-file">
            <h4>5. address.csv - Address Verification Service (AVS)</h4>
            <p><strong>Purpose:</strong> Address data for AVS testing scenarios.</p>
            
            <p><strong>Columns:</strong></p>
            <ul>
                <li><code>address_id</code> - Unique address identifier</li>
                <li><code>cardholder_postal_code</code> - Postal/ZIP code</li>
                <li><code>cardholder_address</code> - Street address</li>
            </ul>

            <p><strong>Usage:</strong> Reference <code>address_id</code> in tests.csv using <code>address_data</code> column.</p>

            <p><strong>Example:</strong></p>
            <pre><code>address_id,cardholder_postal_code,cardholder_address
addr01,SW1A 1AA,123 Test Street
addr02,10001,456 Example Ave
addr03,12345,789 Sample Blvd</code></pre>
        </div>

        <div class="config-file">
            <h4>6. networktoken.csv - Network Tokenization</h4>
            <p><strong>Purpose:</strong> Network token data for tokenized transactions.</p>
            
            <p><strong>Columns:</strong></p>
            <ul>
                <li><code>networktoken_id</code> - Unique token identifier</li>
                <li><code>wallet_id</code> - Wallet identifier (103 = Apple Pay, etc.)</li>
                <li><code>network_token_cryptogram</code> - Token cryptogram</li>
                <li><code>network_token_eci</code> - Electronic Commerce Indicator</li>
            </ul>

            <p><strong>Example:</strong></p>
            <pre><code>networktoken_id,wallet_id,network_token_cryptogram,network_token_eci
token01,103,/wAAAAEACwuDlYgAAAAAgIRgE4A=,05
token02,103,/wAAAAEACwuDlYgAAAAAgIRgE4A=,02</code></pre>
        </div>

        <div class="config-file">
            <h4>7. threeddata.csv - 3D Secure Authentication</h4>
            <p><strong>Purpose:</strong> 3D Secure authentication data for enhanced security testing.</p>
            
            <p><strong>Columns:</strong></p>
            <ul>
                <li><code>three_d_id</code> - Unique 3DS identifier</li>
                <li><code>three_d_secure_type</code> - Type of 3DS authentication</li>
                <li><code>authentication_value</code> - Authentication value</li>
                <li><code>eci</code> - Electronic Commerce Indicator</li>
                <li><code>version</code> - 3DS version</li>
            </ul>

            <p><strong>Example:</strong></p>
            <pre><code>three_d_id,three_d_secure_type,authentication_value,eci,version
3ds01,THREE_DS,AAABBEg0VhI0VniQEjRWAAAAAAA=,05,2.2.0
3ds02,THREE_DS_ATTEMPTED,AAABBEg0VhI0VniQEjRWAAAAAAA=,06,2.2.0</code></pre>
        </div>

        <h2>Configuration Best Practices</h2>

        <h3>1. Data Organization</h3>
        <p><strong>Separate by Environment:</strong></p>
        <ul>
            <li>Use different merchant entries for each environment</li>
            <li>Maintain separate client credentials per environment</li>
            <li>Use descriptive merchant names including environment</li>
        </ul>

        <p><strong>Logical Grouping:</strong></p>
        <ul>
            <li>Group related test cards together</li>
            <li>Use consistent naming conventions</li>
            <li>Include descriptive names for easier debugging</li>
        </ul>

        <h3>2. Security Considerations</h3>
        <div class="alert alert-warning">
            <p><strong>Sensitive Data:</strong></p>
            <ul>
                <li>Store client secrets securely</li>
                <li>Use environment-specific credentials</li>
                <li>Consider using environment variables for production secrets</li>
                <li>Never commit real production credentials to version control</li>
            </ul>

            <p><strong>Test Data:</strong></p>
            <ul>
                <li>Use only test card numbers provided by Worldline</li>
                <li>Ensure test data doesn't contain real customer information</li>
                <li>Use realistic but fake address data</li>
            </ul>
        </div>

        <h3>3. Maintainability</h3>
        <div class="pattern-box">
            <p><strong>Naming Conventions:</strong></p>
            <pre><code>Card IDs: card01, card02, card_visa_basic, card_mc_premium
Merchant IDs: merchant1, merchant_ecom, merchant_pos
Chain IDs: chain1, smoke_test_1, regression_payment_flow
Test IDs: PAY001, CAP001, REF001 (consistent within chains)</code></pre>

            <p><strong>Documentation:</strong></p>
            <ul>
                <li>Use descriptive names in description fields</li>
                <li>Comment complex test scenarios</li>
                <li>Maintain a mapping document for complex setups</li>
            </ul>
        </div>

        <h3>4. Validation</h3>
        <p><strong>Required Field Validation:</strong></p>
        <ul>
            <li>Ensure all required columns are present</li>
            <li>Validate data types and formats</li>
            <li>Check foreign key relationships between files</li>
        </ul>

        <p><strong>Data Consistency:</strong></p>
        <ul>
            <li>Verify merchant/environment combinations exist</li>
            <li>Ensure card data is valid for the intended tests</li>
            <li>Check that chain dependencies are properly ordered</li>
        </ul>

        <h2>Environment-Specific Configuration</h2>

        <h3>Development Environment</h3>
        <pre><code>env,integrator,endpoint_host,client_id,client_secret
dev,Dev Testing,api.dev.acquiring.worldline-solutions.com,dev-client-id,dev-secret</code></pre>

        <h3>Staging/Pre-production</h3>
        <pre><code>env,integrator,endpoint_host,client_id,client_secret
preprod,Staging Tests,api.preprod.acquiring.worldline-solutions.com,preprod-client-id,preprod-secret</code></pre>

        <h3>Production</h3>
        <pre><code>env,integrator,endpoint_host,client_id,client_secret
prod,Production,api.acquiring.worldline-solutions.com,prod-client-id,prod-secret</code></pre>

        <h2>Common Configuration Patterns</h2>

        <div class="pattern-box">
            <h4>Basic Payment Flow</h4>
            <pre><code>chain_id,step_order,call_type,test_id,amount,currency
basic_flow,1,create_payment,CREATE_001,1000,GBP
basic_flow,2,capture_payment,CAPTURE_001,1000,GBP
basic_flow,3,get_payment,GET_001,,</code></pre>
        </div>

        <div class="pattern-box">
            <h4>Authorization and Capture</h4>
            <pre><code>chain_id,step_order,call_type,test_id,amount,currency,authorization_type,capture_immediately
auth_capture,1,create_payment,AUTH_001,5000,EUR,PRE_AUTHORIZATION,FALSE
auth_capture,2,increment_payment,INC_001,1000,EUR,,
auth_capture,3,capture_payment,CAP_001,6000,EUR,,</code></pre>
        </div>

        <div class="pattern-box">
            <h4>Refund Scenario</h4>
            <pre><code>chain_id,step_order,call_type,test_id,amount,currency
refund_flow,1,create_payment,PAY_001,2000,USD
refund_flow,2,capture_payment,CAP_001,2000,USD
refund_flow,3,refund_payment,REF_001,1000,USD
refund_flow,4,get_refund,GET_REF_001,,</code></pre>
        </div>

        <h2>Troubleshooting Configuration</h2>

        <h3>Common Issues</h3>
        <div class="alert alert-warning">
            <p><strong>"Environment X not defined"</strong></p>
            <ul>
                <li>Check environments.csv contains the referenced environment</li>
                <li>Verify environment name matches exactly (case-sensitive)</li>
            </ul>

            <p><strong>"Merchant Y not defined for env Z"</strong></p>
            <ul>
                <li>Ensure merchants.csv has entry for merchant+environment combination</li>
                <li>Check for typos in merchant or environment names</li>
            </ul>

            <p><strong>"Card ID not found"</strong></p>
            <ul>
                <li>Verify card exists in cards.csv</li>
                <li>Check card_id reference in tests.csv matches exactly</li>
            </ul>

            <p><strong>Invalid CSV Format</strong></p>
            <ul>
                <li>Ensure proper CSV formatting with quoted fields containing commas</li>
                <li>Check for missing headers or extra columns</li>
                <li>Validate that required columns are present</li>
            </ul>
        </div>

        <h3>Validation Commands</h3>
        <pre><code># Validate CSV files can be loaded
python -c "from src.data_loader import load_data; load_data()"

# Check specific test file
python -c "from src.data_loader import load_data; load_data('config/your_test_file.csv')"</code></pre>

        <div class="alert alert-success">
            <strong>Configuration Complete:</strong> With these configuration files properly set up, your payment API testing framework will be ready to execute comprehensive test scenarios across different environments and payment methods.
        </div>
    </div>
</body>
</html>