"""Main test runner - clean and focused execution logic with multi-threading support"""

import time
import argparse
import pandas as pd
import concurrent.futures
from threading import Lock
from worldline.acquiring.sdk.factory import Factory

# Import our modular components
from .data_loader import load_data
from .utils import create_temp_config
from .api_calls import create_payment, increment_auth, capture, refund, get_payment, get_refund
from .results_handler import create_success_result, create_error_result, create_dependency_error_result, save_results
from .response_utils import update_previous_outputs, get_card_description
from .request_builders import (
    build_create_payment_request,
    build_increment_payment_request,
    build_capture_payment_request,
    build_refund_payment_request,
    build_get_payment_request,
    build_get_refund_request
)

# Import logging configuration
from .logging_config import (
    setup_logging, 
    get_main_logger,
    get_performance_logger,
    log_api_call,
    log_chain_progress,
    log_performance_summary
)

# Call function mapping (API endpoints)
CALL_FUNCTIONS = {
    'create_payment': create_payment,
    'increment_payment': increment_auth,
    'capture_payment': capture,
    'refund_payment': refund,
    'get_payment': get_payment,
    'get_refund': get_refund
}

# Request builder mapping (CSV call_type -> builder function)
REQUEST_BUILDERS = {
    'create_payment': build_create_payment_request,
    'increment_payment': build_increment_payment_request,
    'capture_payment': build_capture_payment_request,
    'refund_payment': build_refund_payment_request,
    'get_payment': build_get_payment_request,
    'get_refund': build_get_refund_request
}

# Thread-safe result collection
results_lock = Lock()

def parse_arguments():
    """Enhanced argument parsing with tag support"""
    parser = argparse.ArgumentParser(
        description='Run payment API tests with configurable threading, test files, and tag filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                                    # Sequential execution with default tests
  python test_runner.py --threads 3                       # Parallel execution with 3 threads
  python -m src.main --tests smoke_tests.csv              # Specific test suite
  python -m src.main --tags "smoke,visa"                  # Only tests with smoke AND visa tags
  python -m src.main --include-tags smoke --include-tags visa  # Tests with smoke OR visa
  python -m src.main --exclude-tags slow                  # Exclude tests with slow tag
  python -m src.main --list-test-suites                   # Show available test suites
  python -m src.main --list-tags                          # Show all available tags
  python test_runner.py --log-level DEBUG --log-file      # Debug logging to file
  python test_runner.py --threads 5 --log-level INFO     # Parallel with info logging
        """
    )
    
    parser.add_argument(
        '--threads', '-t',
        type=int,
        default=1,
        help='Number of parallel threads for chain execution (default: 1 - sequential)'
    )
    
    parser.add_argument(
        '--tests', '-f',
        type=str,
        default='smoke_tests.csv',  # ✅ NEW: Points to test_suites directory
        help='Path to the test CSV file (default: smoke_tests.csv)'  # ✅ NEW: Updated help
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output for debugging'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        action='store_true',
        help='Enable logging to file in addition to console'
    )
    
    parser.add_argument(
        '--log-path',
        type=str,
        default=None,
        help='Custom path for log file (implies --log-file)'
    )
    
    # Tag filtering arguments
    parser.add_argument(
        '--tags',
        type=str,
        help='Include tests with ALL of these tags (comma-separated, AND logic)'
    )
    
    parser.add_argument(
        '--include-tags',
        action='append',
        help='Include tests with ANY of these tags (can specify multiple times, OR logic)'
    )
    
    parser.add_argument(
        '--exclude-tags',
        type=str,
        help='Exclude tests with these tags (comma-separated)'
    )
    
    parser.add_argument(
        '--list-test-suites',
        action='store_true',
        help='List all available test suite files'
    )
    
    parser.add_argument(
        '--list-tags',
        action='store_true',
        help='List all available tags in the specified test suite'
    )
    
    return parser.parse_args()

def validate_dependencies(call_type, previous_outputs):
    """Check if required dependencies are available for the call type"""
    logger = get_main_logger()
    
    if call_type in ['increment_payment', 'capture_payment', 'refund_payment', 'get_payment']:
        if 'payment_id' not in previous_outputs:
            error_msg = f"payment_id not set for call_type {call_type}"
            logger.warning(error_msg)
            return error_msg
    
    if call_type == 'get_refund':
        if 'refund_id' not in previous_outputs:
            error_msg = f"refund_id not set for call_type {call_type}"
            logger.warning(error_msg)
            return error_msg
    
    logger.debug(f"Dependencies validated for {call_type}")
    return None  # No dependency issues

def get_merchant_info(row, env, merchants):
    """Extract merchant information from configuration"""
    logger = get_main_logger()
    
    merchant = row['merchant_id'] if pd.notna(row['merchant_id']) else None
    if merchant and (env, merchant) not in merchants.index:
        error_msg = f"Merchant {merchant} not defined for env {env} in merchants.csv"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    merchant_row = merchants.loc[(env, merchant)] if merchant else {}
    merchant_info = {
        'acquirer_id': merchant_row.get('acquirer_id', ''),
        'merchant_id': merchant_row.get('merchant_id', ''),
        'merchant_description': merchant_row.get('merchant_description', 'N/A')
    }
    
    logger.debug(f"Merchant info for {merchant}: {merchant_info}")
    return merchant_info

def build_api_call_args(call_type, client, merchant_info, previous_outputs, request=None):
    """Build arguments for API call functions"""
    logger = get_main_logger()
    
    base_args = [client, merchant_info['acquirer_id'], merchant_info['merchant_id']]
    
    if call_type == 'create_payment':
        args = base_args + [request]
    elif call_type in ['increment_payment', 'capture_payment', 'refund_payment']:
        args = base_args + [previous_outputs['payment_id'], request]
    elif call_type == 'get_payment':
        args = base_args + [previous_outputs['payment_id']]
    elif call_type == 'get_refund':
        args = base_args + [previous_outputs['refund_id']]
    else:
        error_msg = f"Unknown call_type: {call_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.debug(f"Built API args for {call_type}: {len(args)} arguments")
    return args

def process_test_step(row, call_type, client, merchant_info, cards, address, networktokens, threeds, previous_outputs, chain_id, step_num, total_steps, verbose=False):
    """Process a single test step"""
    logger = get_main_logger()
    test_id = row['test_id']
    
    # Log progress
    log_chain_progress(logger, chain_id, step_num, total_steps, test_id, call_type)
    
    if verbose:
        print(f"[{chain_id}] Processing {call_type} - {test_id}")
    
    # Check dependencies
    dependency_error = validate_dependencies(call_type, previous_outputs)
    if dependency_error:
        logger.error(f"[{chain_id}] {dependency_error}")
        print(f"[{chain_id}] {dependency_error}")
        return create_dependency_error_result(chain_id, row, call_type, dependency_error)
    
    # Build request (if needed)
    request = None
    if call_type in REQUEST_BUILDERS:
        logger.debug(f"[{chain_id}] Building request for {call_type}")
        builder_func = REQUEST_BUILDERS[call_type]
        if call_type == 'create_payment':
            request = builder_func(row, cards, address, networktokens, threeds)
        else:
            request = builder_func(row)
        logger.debug(f"[{chain_id}] Request built successfully")
    
    # Build API call arguments
    args = build_api_call_args(call_type, client, merchant_info, previous_outputs, request)
    
    # Execute API call
    start_time = time.time()
    try:
        logger.debug(f"[{chain_id}] Executing API call: {call_type}")
        response = CALL_FUNCTIONS[call_type](*args)
        duration = (time.time() - start_time) * 1000
        
        # Log successful API call
        log_api_call(logger, call_type, test_id, chain_id, duration, success=True)
        
        # Update previous outputs for chain dependencies
        update_previous_outputs(response, call_type, previous_outputs)
        
        # Create success result
        card_description = get_card_description(call_type, cards, row.get('card_id'))
        return create_success_result(
            chain_id, row, call_type, response, duration, 
            merchant_info['merchant_description'], previous_outputs, request, card_description
        )
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        
        # Log failed API call
        log_api_call(logger, call_type, test_id, chain_id, duration, success=False, error=str(e))
        print(f"[{chain_id}] API call failed: {e}")
        
        # Create error result
        card_description = get_card_description(call_type, cards, row.get('card_id'))
        return create_error_result(
            chain_id, row, call_type, e, duration,
            merchant_info['merchant_description'], previous_outputs, request, card_description
        )

def run_test_chain(chain_id, group, environments, merchants, cards, address, networktokens, threeds, verbose=False):
    """Run all steps in a test chain (sequential within chain)"""
    logger = get_main_logger()
    
    logger.info(f"[{chain_id}] Starting chain execution")
    print(f"[{chain_id}] Starting chain execution")
    results = []
    previous_outputs = {}
    total_steps = len(group)
    
    # Get environment configuration
    env = group['env'].iloc[0]
    if env not in environments.index:
        error_msg = f"Environment {env} not defined in environments.csv"
        logger.error(f"[{chain_id}] {error_msg}")
        raise ValueError(error_msg)
    
    env_data = environments.loc[env]
    temp_config = create_temp_config(env_data)
    logger.debug(f"[{chain_id}] Using environment: {env}")
    
    # Execute all steps in the chain sequentially
    with Factory.create_client_from_file(temp_config, env_data['client_id'], env_data['client_secret']) as client:
        logger.debug(f"[{chain_id}] API client created successfully")
        
        for step_num, (_, row) in enumerate(group.iterrows(), 1):
            call_type = row['call_type']
            
            # Validate call type
            if call_type not in CALL_FUNCTIONS:
                error_msg = f"Unknown call_type: {call_type}"
                logger.error(f"[{chain_id}] {error_msg}")
                raise ValueError(error_msg)
            
            # Get merchant information
            try:
                merchant_info = get_merchant_info(row, env, merchants)
            except ValueError as e:
                logger.error(f"[{chain_id}] Merchant configuration error: {e}")
                print(f"[{chain_id}] Merchant configuration error: {e}")
                continue
            
            # Process the test step
            result = process_test_step(row, call_type, client, merchant_info, cards, address, networktokens, threeds, previous_outputs, chain_id, step_num, total_steps, verbose)
            results.append(result)
    
    logger.info(f"[{chain_id}] Completed chain execution ({len(results)} steps)")
    print(f"[{chain_id}] Completed chain execution ({len(results)} steps)")
    return results

def run_sequential_chains(environments, merchants, cards, address, networktokens, threeds, tests, verbose=False):
    """Run test chains sequentially (original behavior)"""
    logger = get_main_logger()
    
    logger.info("🔄 Running chains sequentially")
    print("🔄 Running chains sequentially")
    all_results = []
    
    for chain_id, group in tests.groupby('chain_id'):
        try:
            chain_results = run_test_chain(chain_id, group, environments, merchants, cards, address, networktokens, threeds, verbose)
            all_results.extend(chain_results)
        except Exception as e:
            logger.error(f"❌ Chain {chain_id} failed: {e}", exc_info=True)
            print(f"❌ Chain {chain_id} failed: {e}")
            continue
    
    return all_results

def run_parallel_chains(environments, merchants, cards, address, networktokens, threeds, tests, max_workers=3, verbose=False):
    """Run test chains in parallel with controlled concurrency"""
    logger = get_main_logger()
    
    logger.info(f"🧵 Running chains in parallel with {max_workers} threads")
    print(f"🧵 Running chains in parallel with {max_workers} threads")
    all_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit each chain as a separate task
        future_to_chain = {
            executor.submit(run_test_chain, chain_id, group, environments, merchants, cards, address, networktokens, threeds, verbose): chain_id
            for chain_id, group in tests.groupby('chain_id')
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_chain):
            chain_id = future_to_chain[future]
            try:
                chain_results = future.result()
                with results_lock:
                    all_results.extend(chain_results)
                logger.info(f"✅ Completed chain: {chain_id}")
                print(f"✅ Completed chain: {chain_id}")
            except Exception as e:
                logger.error(f"❌ Chain {chain_id} failed: {e}", exc_info=True)
                print(f"❌ Chain {chain_id} failed: {e}")
    
    return all_results

def main():
    """Main execution function with configurable threading and test files"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging based on arguments
    if args.log_path:
        setup_logging(args.log_level, log_to_file=True, log_file=args.log_path)
    else:
        setup_logging(args.log_level, log_to_file=args.log_file)
    
    # Get main logger
    logger = get_main_logger()
    perf_logger = get_performance_logger()
    
    logger.info("🚀 Starting payment API test execution...")
    logger.info(f"📁 Test file: {args.tests}")
    logger.info(f"🧵 Threads: {args.threads}")
    logger.info(f"🔍 Verbose: {args.verbose}")
    logger.info(f"📋 Log level: {args.log_level}")
    
    print("🚀 Starting payment API test execution...")
    print(f"📁 Test file: {args.tests}")
    print(f"🧵 Threads: {args.threads}")
    print(f"🔍 Verbose: {args.verbose}")
    print("-" * 50)
    
    try:
        # Load configuration data
        logger.debug("Loading configuration data...")
        from .config.config_manager import ConfigurationManager
        from .core.tag_filter import TagFilter
        
        config_manager = ConfigurationManager()
        config_set = config_manager.load_all_configs(args.tests)
        
        # Handle list operations
        if args.list_test_suites:
            available_suites = config_manager.list_available_test_suites()
            print("📋 Available test suites:")
            for suite in available_suites:
                print(f"  - {suite}")
            return
        
        if args.list_tags:
            all_tags = config_manager.get_all_tags(config_set.tests)
            print(f"🏷️ Available tags in {args.tests}:")
            for tag in all_tags:
                print(f"  - {tag}")
            return
        
        # Apply tag filtering
        original_test_count = len(config_set.tests)
        if args.tags or args.include_tags or args.exclude_tags:
            # Create tag filter
            include_list = []
            if args.tags:
                include_list = [tag.strip() for tag in args.tags.split(',')]
                require_all = True  # AND logic for --tags
            elif args.include_tags:
                include_list = args.include_tags
                require_all = False  # OR logic for --include-tags
            
            exclude_list = []
            if args.exclude_tags:
                exclude_list = [tag.strip() for tag in args.exclude_tags.split(',')]
            
            tag_filter = TagFilter(include_list, exclude_list, require_all)
            config_set.tests = tag_filter.filter_tests(config_set.tests)
            
            logger.info(f"🏷️ Tag filtering: {original_test_count} → {len(config_set.tests)} tests")
        
        # Convert back to original format for compatibility
        environments = config_set.environments
        cards = config_set.cards
        merchants = config_set.merchants
        address = config_set.address
        networktokens = config_set.networktokens
        threeds = config_set.threeds
        tests = config_set.tests
        
        
        # Execute test chains
        start_time = time.time()
        enable_threading = args.threads > 1
        
        total_chains = len(tests.groupby('chain_id'))
        logger.info(f"Executing {total_chains} test chains with {len(tests)} total steps")
        
        if enable_threading:
            logger.info(f"Running {total_chains} chains in parallel with {args.threads} threads")
            all_results = run_parallel_chains(environments, merchants, cards, address, networktokens, threeds, tests, args.threads, args.verbose)
        else:
            logger.info(f"Running {total_chains} chains sequentially")
            all_results = run_sequential_chains(environments, merchants, cards, address, networktokens, threeds, tests, args.verbose)
        
        execution_time = time.time() - start_time
        
        # Save all results
        logger.debug("Saving test results...")
        save_results(all_results)
        
        print("-" * 50)
        logger.info(f"🎉 Tests complete!")
        logger.info(f"📊 Executed {len(all_results)} API calls")
        logger.info(f"⏱️  Total execution time: {execution_time:.2f} seconds")
        logger.info(f"🧵 Threading: {'Enabled' if enable_threading else 'Disabled'}")
        
        print(f"🎉 Tests complete!")
        print(f"📊 Executed {len(all_results)} API calls")
        print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
        print(f"🧵 Threading: {'Enabled' if enable_threading else 'Disabled'}")
        
        # Show pass/fail summary
        passed = sum(1 for r in all_results if r['pass'])
        failed = len(all_results) - passed
        
        # Log performance summary
        log_performance_summary(perf_logger, len(all_results), execution_time, passed, failed, enable_threading)
        
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            logger.warning(f"Some tests failed. Check results for details.")
        
    except FileNotFoundError as e:
        logger.error(f"❌ Error: Test file not found - {e}")
        logger.info("💡 Make sure the specified test file exists")
        print(f"❌ Error: Test file not found - {e}")
        print("💡 Make sure the specified test file exists")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()