<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Command Line Interface Reference</title>
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
        .option-header {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0 10px 0;
            border-left: 4px solid #2196f3;
        }
        .option-type {
            color: #666;
            font-style: italic;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Command Line Interface Reference</h1>

        <h2>Synopsis</h2>
        <pre><code>python -m src.main [OPTIONS]</code></pre>

        <h2>Description</h2>
        <p>Execute payment API test chains with configurable parallelism and test files.</p>

        <h2>Options</h2>

        <div class="option-header">
            <h3><code>--threads</code>, <code>-t</code></h3>
            <p class="option-type"><strong>Type:</strong> Integer &nbsp;&nbsp; <strong>Default:</strong> <code>1</code></p>
            <p><strong>Description:</strong> Number of parallel threads for chain execution</p>
        </div>

        <pre><code># Sequential execution (default)
python -m src.main --threads 1

# Parallel execution with 3 threads
python -m src.main --threads 3

# Maximum parallelism (use with caution)
python -m src.main --threads 10</code></pre>

        <p><strong>Notes:</strong></p>
        <ul>
            <li><code>--threads 1</code> = Sequential execution (chains run one after another)</li>
            <li><code>--threads N</code> = Parallel execution (up to N chains run simultaneously)</li>
            <li>Steps within each chain always execute sequentially</li>
            <li>Higher thread counts may hit API rate limits</li>
        </ul>

        <div class="option-header">
            <h3><code>--tests</code>, <code>-f</code></h3>
            <p class="option-type"><strong>Type:</strong> String (file path) &nbsp;&nbsp; <strong>Default:</strong> <code>config/tests.csv</code></p>
            <p><strong>Description:</strong> Path to the test CSV file</p>
        </div>

        <pre><code># Use default test file
python -m src.main

# Use custom test file
python -m src.main --tests config/smoke_tests.csv

# Use test file from different directory
python -m src.main --tests /path/to/custom/tests.csv</code></pre>

        <p><strong>File Format Requirements:</strong></p>
        <ul>
            <li>Must be valid CSV with headers</li>
            <li>Required columns: <code>chain_id</code>, <code>step_order</code>, <code>call_type</code>, <code>test_id</code></li>
            <li>Must be sorted by <code>chain_id</code> and <code>step_order</code></li>
        </ul>

        <div class="option-header">
            <h3><code>--verbose</code>, <code>-v</code></h3>
            <p class="option-type"><strong>Type:</strong> Flag (no value) &nbsp;&nbsp; <strong>Default:</strong> <code>False</code></p>
            <p><strong>Description:</strong> Enable verbose output for debugging</p>
        </div>

        <pre><code># Standard output
python -m src.main

# Verbose output
python -m src.main --verbose</code></pre>

        <p><strong>Verbose Output Includes:</strong></p>
        <ul>
            <li>Step-by-step chain execution progress</li>
            <li>Detailed API call information</li>
            <li>Request/response debugging details</li>
            <li>Thread execution status</li>
            <li>Extended error messages</li>
        </ul>

        <h2>Examples</h2>

        <h3>Basic Usage</h3>
        <pre><code># Run all tests sequentially with default settings
python -m src.main

# Run tests in parallel with 3 threads
python -m src.main --threads 3</code></pre>

        <h3>Custom Test Files</h3>
        <pre><code># Smoke test suite
python -m src.main --tests config/smoke_tests.csv

# Regression test suite with parallelism
python -m src.main --tests config/regression.csv --threads 5

# Single chain test
python -m src.main --tests config/single_chain.csv --verbose</code></pre>

        <h3>Development & Debugging</h3>
        <pre><code># Debug single-threaded execution
python -m src.main --verbose

# Debug specific test file
python -m src.main --tests config/debug.csv --verbose

# Performance testing with high parallelism
python -m src.main --tests config/load_test.csv --threads 8</code></pre>

        <h3>Production Usage</h3>
        <pre><code># Scheduled regression testing
python -m src.main --tests config/nightly_regression.csv --threads 5

# Environment validation
python -m src.main --tests config/env_validation.csv --threads 2

# Performance benchmarking
python -m src.main --tests config/perf_benchmark.csv --threads 1</code></pre>

        <h2>Exit Codes</h2>
        <table>
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Meaning</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>0</td>
                    <td>Success - all tests completed (may include failed API calls)</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Error - configuration issue, file not found, or system error</td>
                </tr>
            </tbody>
        </table>

        <div class="alert alert-info">
            <strong>Note:</strong> The exit code indicates whether the test <em>execution</em> succeeded, not whether all API calls passed. Check the results CSV or console output for API call success rates.
        </div>

        <h2>Environment Variables</h2>
        <p>Currently, the framework doesn't use environment variables. All configuration is file-based through CSV files in the <code>/config</code> directory.</p>

        <h2>Output Files</h2>
        <p>Every execution creates/updates:</p>
        <ul>
            <li><code>outputs/results.csv</code> - Latest test results</li>
            <li><code>outputs/local.db</code> - SQLite database with all historical results</li>
        </ul>

        <h2>Performance Considerations</h2>

        <h3>Thread Count Recommendations</h3>
        <table>
            <thead>
                <tr>
                    <th>Test Scenario</th>
                    <th>Recommended Threads</th>
                    <th>Rationale</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Development/Debugging</td>
                    <td>1</td>
                    <td>Easier to trace issues</td>
                </tr>
                <tr>
                    <td>Smoke Testing</td>
                    <td>2-3</td>
                    <td>Fast feedback, low load</td>
                </tr>
                <tr>
                    <td>Regression Testing</td>
                    <td>3-5</td>
                    <td>Balanced speed/stability</td>
                </tr>
                <tr>
                    <td>Load Testing</td>
                    <td>5-10</td>
                    <td>Maximum throughput</td>
                </tr>
            </tbody>
        </table>

        <h3>Memory Usage</h3>
        <ul>
            <li>Each thread requires ~10-50MB depending on test complexity</li>
            <li>Large test files increase memory usage regardless of thread count</li>
            <li>Monitor system resources when using high thread counts</li>
        </ul>

        <h3>API Rate Limits</h3>
        <ul>
            <li>Worldline APIs may have rate limiting</li>
            <li>Higher thread counts may trigger rate limits</li>
            <li>Use <code>--verbose</code> to monitor for HTTP 429 responses</li>
            <li>Reduce thread count if rate limiting occurs</li>
        </ul>
    </div>
</body>
</html>