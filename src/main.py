"""Main test runner - clean and focused execution logic with multi-threading support"""

import time
import argparse
import pandas as pd
import concurrent.futures
import logging
from threading import Lock
from worldline.acquiring.sdk.factory import Factory
from .core.endpoint_registry import EndpointRegistry

# ✅ ADD: Import endpoints package to trigger registration
import src.endpoints

# Import our modular components
from .data_loader import load_data
from .core.endpoint_registry import EndpointRegistry
from .utils import create_temp_config
from .api_calls import create_payment, increment_auth, capture, refund, get_payment, get_refund, reverse_authorization_call, standalone_refund_call, capture_refund_call
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

# ✅ NEW: Import DCC components
from .core.dcc_manager import DCCManager, perform_dcc_inquiry
from .endpoints.get_dcc_rate_endpoint import build_get_dcc_rate_request, get_dcc_rate

# Import logging configuration (EXISTING)
from .logging_config import (
    setup_logging, 
    get_main_logger,
    get_performance_logger,
    log_api_call,
    log_chain_progress,
    log_performance_summary
)

# Thread-safe result collection
results_lock = Lock()

# ✅ REMOVE: Delete the duplicate logging functions I added
# (get_main_logger, log_chain_start, log_chain_complete, log_chain_progress, log_api_call)
# These are already imported from logging_config above

# ✅ ADD: Missing log functions that aren't in logging_config
def log_chain_start(logger, chain_id):
    """Log chain start"""
    logger.info(f"[{chain_id}] Starting chain execution")

def log_chain_complete(logger, chain_id, steps_count):
    """Log chain completion"""
    logger.info(f"[{chain_id}] Completed chain execution ({steps_count} steps)")

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
  python -m src.main --tags dcc                           # Run DCC tests only
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
        default='smoke_tests.csv',
        help='Path to the test CSV file (default: smoke_tests.csv)'
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
    
    endpoint = EndpointRegistry.get_endpoint(call_type)
    if not endpoint:
        error_msg = f"Unknown call_type: {call_type}"
        logger.error(error_msg)
        return error_msg
    
    dependencies = endpoint.get_dependencies()
    for dep in dependencies:
        if dep not in previous_outputs:
            error_msg = f"{dep} not set for call_type {call_type}"
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
    """Build arguments for API call functions using registry"""
    logger = get_main_logger()
    
    endpoint = EndpointRegistry.get_endpoint(call_type)
    if not endpoint:
        error_msg = f"Unknown call_type: {call_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    base_args = [client, merchant_info['acquirer_id'], merchant_info['merchant_id']]
    
    # Add dependency arguments based on endpoint requirements
    dependencies = endpoint.get_dependencies()
    for dep in dependencies:
        if dep in previous_outputs:
            base_args.append(previous_outputs[dep])
    
    # Add request if needed
    if request is not None:
        base_args.append(request)
    
    logger.debug(f"Built API args for {call_type}: {len(base_args)} arguments")
    return base_args

def perform_dcc_inquiry(row, call_type, client, merchant_info, dcc_manager, chain_id, verbose=False):
    """✅ NEW: Perform DCC rate inquiry if needed"""
    logger = get_main_logger()
    
    # Check if DCC is enabled for this step
    if not dcc_manager.should_perform_dcc_inquiry(row):
        return None
    
    try:
        # Determine transaction type based on call type
        transaction_type = dcc_manager.determine_transaction_type(call_type)
        
        # Get existing rate reference ID for this chain
        chain_context = dcc_manager.get_chain_context(chain_id)
        existing_rate_ref = chain_context.rate_reference_id
        
        if verbose:
            print(f"[{chain_id}] Performing DCC inquiry for {transaction_type} (existing rate: {existing_rate_ref})")
        
        logger.info(f"[{chain_id}] DCC inquiry: {transaction_type}, rate_ref: {existing_rate_ref}")
        
        # Build DCC request
        dcc_request = build_get_dcc_rate_request(row, transaction_type, existing_rate_ref)
        
        # Execute DCC API call
        start_time = time.time()
        dcc_response = get_dcc_rate(
            client, merchant_info['acquirer_id'], 
            merchant_info['merchant_id'], dcc_request
        )
        dcc_duration = (time.time() - start_time) * 1000
        
        # Update DCC context with response
        dcc_manager.update_context_from_dcc_response(chain_id, dcc_response)
        
        # Log successful DCC inquiry
        log_api_call(logger, 'get_dcc_rate', row['test_id'], chain_id, dcc_duration, success=True)
        
        if verbose:
            updated_context = dcc_manager.get_chain_context(chain_id)
            print(f"[{chain_id}] DCC inquiry successful, rate ID: {updated_context.rate_reference_id}")
        
        logger.info(f"[{chain_id}] DCC inquiry successful, rate ID: {dcc_manager.get_chain_context(chain_id).rate_reference_id}")
        
        # Return DCC result for logging (optional)
        return {
            'call_type': 'get_dcc_rate',
            'test_id': row['test_id'],
            'duration_ms': dcc_duration,
            'success': True,
            'response': dcc_response.to_dictionary() if hasattr(dcc_response, 'to_dictionary') else str(dcc_response)
        }
        
    except Exception as e:
        # Log failed DCC inquiry
        log_api_call(logger, 'get_dcc_rate', row['test_id'], chain_id, 0, success=False, error=str(e))
        
        if verbose:
            print(f"[{chain_id}] DCC inquiry failed: {e}")
        
        logger.error(f"[{chain_id}] DCC inquiry failed: {e}")
        
        # Fail the entire chain as requested
        raise Exception(f"DCC inquiry failed for {call_type}: {e}")

def perform_dcc_inquiry(row, call_type, client, merchant_info, dcc_manager, chain_id, verbose=False):
    """✅ NEW: Perform DCC rate inquiry if needed"""
    logger = get_main_logger()
    
    # Check if DCC is enabled for this step
    if not dcc_manager.should_perform_dcc_inquiry(row):
        return None
    
    try:
        # Determine transaction type based on call type
        transaction_type = dcc_manager.determine_transaction_type(call_type)
        
        # Get existing rate reference ID for this chain
        chain_context = dcc_manager.get_chain_context(chain_id)
        existing_rate_ref = chain_context.rate_reference_id
        
        if verbose:
            print(f"[{chain_id}] Performing DCC inquiry for {transaction_type} (existing rate: {existing_rate_ref})")
        
        logger.info(f"[{chain_id}] DCC inquiry: {transaction_type}, rate_ref: {existing_rate_ref}")
        
        # Build DCC request with cards data
        dcc_request = build_get_dcc_rate_request(row, transaction_type, existing_rate_ref, cards=None)  # We'll fix this
        
        # Execute DCC API call
        start_time = time.time()
        dcc_response = get_dcc_rate(
            client, merchant_info['acquirer_id'], 
            merchant_info['merchant_id'], dcc_request
        )
        dcc_duration = (time.time() - start_time) * 1000
        
        # Update DCC context with response
        dcc_manager.update_context_from_dcc_response(chain_id, dcc_response)
        
        # Log successful DCC inquiry
        log_api_call(logger, 'get_dcc_rate', row['test_id'], chain_id, dcc_duration, success=True)
        
        if verbose:
            updated_context = dcc_manager.get_chain_context(chain_id)
            print(f"[{chain_id}] DCC inquiry successful, rate ID: {updated_context.rate_reference_id}")
        
        logger.info(f"[{chain_id}] DCC inquiry successful, rate ID: {dcc_manager.get_chain_context(chain_id).rate_reference_id}")
        
        return dcc_response
        
    except Exception as e:
        # Log failed DCC inquiry
        log_api_call(logger, 'get_dcc_rate', row['test_id'], chain_id, 0, success=False, error=str(e))
        
        if verbose:
            print(f"[{chain_id}] DCC inquiry failed: {e}")
        
        logger.error(f"[{chain_id}] DCC inquiry failed: {e}")
        
        # Fail the entire chain as requested
        raise Exception(f"DCC inquiry failed for {call_type}: {e}")

# ✅ ADD: DCC inquiry function that accepts cards
def perform_dcc_inquiry_with_cards(row, call_type, client, merchant_info, cards, dcc_manager, chain_id, verbose=False):
    """Perform DCC rate inquiry with cards data"""
    logger = get_main_logger()
    
    # Check if DCC is enabled for this step
    if not dcc_manager.should_perform_dcc_inquiry(row):
        return None
    
    try:
        # Determine transaction type based on call type
        transaction_type = dcc_manager.determine_transaction_type(call_type)
        
        # Get existing rate reference ID for this chain
        chain_context = dcc_manager.get_chain_context(chain_id)
        existing_rate_ref = chain_context.rate_reference_id
        
        if verbose:
            print(f"[{chain_id}] Performing DCC inquiry for {transaction_type} (existing rate: {existing_rate_ref})")
        
        logger.info(f"[{chain_id}] DCC inquiry: {transaction_type}, rate_ref: {existing_rate_ref}")
        
        # ✅ FIX: Build DCC request WITH cards data
        dcc_request = build_get_dcc_rate_request(row, transaction_type, existing_rate_ref, cards=cards)
        
        # Execute DCC API call
        start_time = time.time()
        dcc_response = get_dcc_rate(
            client, merchant_info['acquirer_id'], 
            merchant_info['merchant_id'], dcc_request
        )
        dcc_duration = (time.time() - start_time) * 1000
        
        # Update DCC context with response
        dcc_manager.update_context_from_dcc_response(chain_id, dcc_response)
        
        # Log successful DCC inquiry using existing function
        log_api_call(logger, 'get_dcc_rate', row['test_id'], chain_id, dcc_duration, success=True)
        
        if verbose:
            updated_context = dcc_manager.get_chain_context(chain_id)
            print(f"[{chain_id}] DCC inquiry successful, rate ID: {updated_context.rate_reference_id}")
        
        return dcc_response
        
    except Exception as e:
        # Log failed DCC inquiry using existing function
        log_api_call(logger, 'get_dcc_rate', row['test_id'], chain_id, 0, success=False, error=str(e))
        
        if verbose:
            print(f"[{chain_id}] DCC inquiry failed: {e}")
        
        logger.error(f"[{chain_id}] DCC inquiry failed: {e}")
        
        # Fail the entire chain as requested

# ✅ UPDATE: Fix DCC inquiry call to pass cards
def process_test_step(row, call_type, client, merchant_info, cards, address, networktokens, threeds, cardonfile, previous_outputs, chain_id, step_num, total_steps, dcc_manager=None, verbose=False):
    """✅ Enhanced: Process a single test step with DCC support using existing registry pattern"""
    logger = get_main_logger()
    test_id = row['test_id']
    
    # Log progress using existing function
    log_chain_progress(logger, chain_id, step_num, total_steps, test_id, call_type)
    
    if verbose:
        print(f"[{chain_id}] Processing {call_type} - {test_id}")
    
    # Get endpoint from registry
    endpoint = EndpointRegistry.get_endpoint(call_type)
    if not endpoint:
        available_endpoints = list(EndpointRegistry.get_all_endpoints().keys())
        error_msg = f"Unknown call_type: {call_type}. Available: {available_endpoints}"
        logger.error(f"[{chain_id}] {error_msg}")
        print(f"[{chain_id}] {error_msg}")
        return create_dependency_error_result(chain_id, row, call_type, error_msg)
    
    # Check dependencies using registry
    dependency_error = validate_dependencies(call_type, previous_outputs)
    if dependency_error:
        logger.error(f"[{chain_id}] {dependency_error}")
        print(f"[{chain_id}] {dependency_error}")
        return create_dependency_error_result(chain_id, row, call_type, dependency_error)
    
    # ✅ NEW: Perform DCC inquiry if needed (WITH CARDS DATA)
    dcc_context = None
    if dcc_manager:
        try:
            # ✅ FIX: Create a modified perform_dcc_inquiry that accepts cards
            dcc_result = perform_dcc_inquiry_with_cards(row, call_type, client, merchant_info, cards, dcc_manager, chain_id, verbose)
            dcc_context = dcc_manager.get_chain_context(chain_id)
        except Exception as e:
            # DCC inquiry failed - fail the entire chain
            logger.error(f"[{chain_id}] DCC inquiry failed, stopping chain: {e}")
            print(f"[{chain_id}] DCC inquiry failed, stopping chain: {e}")
            card_description = get_card_description(call_type, cards, row.get('card_id'))
            return create_error_result(
                chain_id, row, f"dcc_inquiry_{call_type}", e, 0,
                merchant_info['merchant_description'], previous_outputs, None, card_description
            )
    
        # ✅ Enhanced: Build request using registry with DCC context
        request = None
        try:
            if call_type == 'create_payment':
                # Create payment uses the full signature with DCC
                if dcc_context and endpoint.supports_dcc():
                    request = endpoint.build_request_with_dcc(row, dcc_context, cards, address, networktokens, threeds, cardonfile, previous_outputs)
                else:
                    request = endpoint.build_request(row, cards, address, networktokens, threeds, cardonfile, previous_outputs)
            elif call_type in ['increment_payment', 'capture_payment', 'refund_payment']:
                # ✅ FIXED: Use DCC-aware request building for payment operations
                if dcc_context and endpoint.supports_dcc():
                    request = endpoint.build_request_with_dcc(row, dcc_context)  # Pass DCC context
                else:
                    request = endpoint.build_request(row)
            else:
                # GET operations and other endpoints don't need DCC
                request = endpoint.build_request(row)
            logger.debug(f"[{chain_id}] Request built successfully")
        except Exception as e:
            logger.error(f"[{chain_id}] Request building failed: {e}")
            print(f"[{chain_id}] Request building failed: {e}")
            return create_dependency_error_result(chain_id, row, call_type, f"Request building failed: {e}")
    
    # Build API call arguments using registry
    args = build_api_call_args(call_type, client, merchant_info, previous_outputs, request)
    
    # Execute API call using registry
    start_time = time.time()
    try:
        logger.debug(f"[{chain_id}] Executing API call: {call_type}")
        response = endpoint.call_api(*args)
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

def run_test_chain(chain_id, group, environments, merchants, cards, address, networktokens, threeds, cardonfile, verbose=False):
    """✅ Enhanced: Run all steps in a test chain with DCC support"""
    logger = get_main_logger()
    log_chain_start(logger, chain_id)
    print(f"[{chain_id}] Starting chain execution")
    results = []
    previous_outputs = {}
    
    # ✅ NEW: Create DCC manager for this chain
    dcc_manager = DCCManager()
    
    # Get environment configuration
    env = group['env'].iloc[0]
    if env not in environments.index:
        raise ValueError(f"Environment {env} not defined in environments.csv")
    
    env_data = environments.loc[env]
    temp_config = create_temp_config(env_data)
    
    # Execute all steps in the chain sequentially
    with Factory.create_client_from_file(temp_config, env_data['client_id'], env_data['client_secret']) as client:
        for step_num, (_, row) in enumerate(group.iterrows(), 1):
            call_type = row['call_type']
            total_steps = len(group)
            
            # Validate call type
            endpoint = EndpointRegistry.get_endpoint(call_type)
            if not endpoint:
                available_endpoints = list(EndpointRegistry.get_all_endpoints().keys())
                raise ValueError(f"Unknown call_type: {call_type}. Available: {available_endpoints}")
            
            # Get merchant information
            try:
                merchant_info = get_merchant_info(row, env, merchants)
            except ValueError as e:
                logger.error(f"[{chain_id}] Merchant configuration error: {e}")
                print(f"[{chain_id}] Merchant configuration error: {e}")
                continue
            
            # ✅ Enhanced: Process the test step with DCC support
            result = process_test_step(
                row, call_type, client, merchant_info, cards, address, networktokens, threeds, cardonfile,
                previous_outputs, chain_id, step_num, total_steps, dcc_manager, verbose
            )
            results.append(result)
    
    log_chain_complete(logger, chain_id, len(results))
    print(f"[{chain_id}] Completed chain execution ({len(results)} steps)")
    return results

def run_sequential_chains(environments, merchants, cards, address, networktokens, threeds, cardonfile, tests, verbose=False):
    """Run test chains sequentially (original behavior)"""
    logger = get_main_logger()
    
    logger.info("🔄 Running chains sequentially")
    print("🔄 Running chains sequentially")
    all_results = []
    
    for chain_id, group in tests.groupby('chain_id'):
        try:
            chain_results = run_test_chain(chain_id, group, environments, merchants, cards, address, networktokens, threeds, cardonfile, verbose)
            all_results.extend(chain_results)
        except Exception as e:
            logger.error(f"❌ Chain {chain_id} failed: {e}", exc_info=True)
            print(f"❌ Chain {chain_id} failed: {e}")
            continue
    
    return all_results

def run_parallel_chains(environments, merchants, cards, address, networktokens, threeds, cardonfile, tests, max_workers=3, verbose=False):
    """Run test chains in parallel with controlled concurrency"""
    logger = get_main_logger()
    
    logger.info(f"🧵 Running chains in parallel with {max_workers} threads")
    print(f"🧵 Running chains in parallel with {max_workers} threads")
    all_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit each chain as a separate task
        future_to_chain = {
            executor.submit(run_test_chain, chain_id, group, environments, merchants, cards, address, networktokens, threeds, cardonfile, verbose): chain_id
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
        cardonfile = config_set.cardonfile
        tests = config_set.tests

        # Execute test chains
        start_time = time.time()
        enable_threading = args.threads > 1
        
        total_chains = len(tests.groupby('chain_id'))
        logger.info(f"Executing {total_chains} test chains with {len(tests)} total steps")
        
        if enable_threading:
            logger.info(f"Running {total_chains} chains in parallel with {args.threads} threads")
            all_results = run_parallel_chains(environments, merchants, cards, address, networktokens, threeds, cardonfile, tests, args.threads, args.verbose)
        else:
            logger.info(f"Running {total_chains} chains sequentially")
            all_results = run_sequential_chains(environments, merchants, cards, address, networktokens, threeds, cardonfile, tests, args.verbose)
        
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