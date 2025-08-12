"""Results handling for API test execution with payment-specific assertions"""

import json
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional
from .logging_config import get_main_logger
from .core.payment_assertions import PaymentAssertionEngine
from .response_utils import get_transaction_id, get_response_status
from .utils import get_db_engine

def get_results_logger():
    """Get logger for results handling"""
    return get_main_logger()

def serialize_request_data(request: Any) -> str:
    """Serialize request data to JSON string (CSV-safe)"""
    try:
        if request is None:
            return ''
        
        if hasattr(request, 'to_dictionary'):
            # Create compact JSON and escape any problematic characters
            json_str = json.dumps(request.to_dictionary(), separators=(',', ':'), ensure_ascii=True)
            # ✅ Additional safety: replace any remaining problematic characters
            return json_str.replace('\n', '\\n').replace('\r', '\\r')
        elif hasattr(request, '__dict__'):
            # Try to serialize object attributes
            data = {key: str(value) for key, value in request.__dict__.items() 
                   if not key.startswith('_')}
            json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=True)
            return json_str.replace('\n', '\\n').replace('\r', '\\r')
        else:
            return str(request).replace('\n', '\\n').replace('\r', '\\r')
    except Exception as e:
        return f"Serialization error: {e}"

def serialize_response_data(response: Any) -> str:
    """Serialize response data to JSON string (CSV-safe)"""
    try:
        if response is None:
            return ''
        
        if hasattr(response, 'to_dictionary'):
            # Create compact JSON and escape any problematic characters
            json_str = json.dumps(response.to_dictionary(), separators=(',', ':'), ensure_ascii=True)
            # ✅ Additional safety: replace any remaining problematic characters
            return json_str.replace('\n', '\\n').replace('\r', '\\r')
        elif hasattr(response, '__dict__'):
            # Try to serialize object attributes
            data = {key: str(value) for key, value in response.__dict__.items() 
                   if not key.startswith('_')}
            json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=True)
            return json_str.replace('\n', '\\n').replace('\r', '\\r')
        else:
            return str(response).replace('\n', '\\n').replace('\r', '\\r')
    except Exception as e:
        return f"Serialization error: {e}"

def parse_error_response(error: Exception) -> Dict[str, Any]:
    """Parse error response to extract structured error information"""
    try:
        error_str = str(error)
        
        # Try to extract JSON from error message
        if 'response_body=' in error_str:
            import re
            match = re.search(r"response_body='({.*?})'", error_str)
            if match:
                try:
                    error_json = json.loads(match.group(1))
                    return {
                        'title': error_json.get('title', 'Unknown Error'),
                        'detail': error_json.get('detail', error_str),
                        'type': error_json.get('type', ''),
                        'status': error_json.get('status', 500)
                    }
                except json.JSONDecodeError:
                    pass
        
        # Fallback to basic error info
        return {
            'title': type(error).__name__,
            'detail': error_str,
            'type': '',
            'status': 500
        }
    except Exception:
        return {
            'title': 'Unknown Error',
            'detail': str(error),
            'type': '',
            'status': 500
        }

def create_success_result(chain_id: str, row: pd.Series, call_type: str, response: Any, 
                         duration: float, merchant_description: str, previous_outputs: Dict[str, Any], 
                         request: Any, card_description: str) -> Dict[str, Any]:
    """Create success result with payment-specific assertions"""
    logger = get_results_logger()
    
    # Initialize payment assertion engine
    assertion_engine = PaymentAssertionEngine()
    
    # Get HTTP status from response (assuming 201 for creates, 200 for others by default)
    http_status = 201 if call_type == 'create_payment' else 200
    
    # Try to extract actual HTTP status if available
    if hasattr(response, 'status_code'):
        http_status = response.status_code
    elif hasattr(response, 'to_dictionary'):
        resp_dict = response.to_dictionary()
        http_status = resp_dict.get('httpStatusCode', http_status)
    
    # Evaluate payment assertions
    assertion_result = assertion_engine.evaluate_payment_assertions(
        row, response, http_status, call_type
    )
    
    logger.info(f"Creating success result for {chain_id} - {call_type} - {row['test_id']}")
    logger.info(f"Assertion result: {assertion_result.message}")
    
    result = {
        'chain_id': chain_id,
        'test_id': row['test_id'],
        'call_type': call_type,
        'pass': assertion_result.passed,  # ✅ Now uses focused payment assertions!
        'assertion_message': assertion_result.message,
        'assertion_details': str(assertion_result.details),
        
        # API response data
        'transaction_id': get_transaction_id(response, call_type),
        'response_status': get_response_status(response, call_type),
        'http_status': http_status,
        'duration_ms': duration,
        'merchant_description': merchant_description,
        'card_description': card_description,
        'amount': row.get('amount', ''),
        'currency': row.get('currency', ''),
        'error_message': '',
        'error_type': '',
        'error_details': '',
        'request_data': serialize_request_data(request),
        'response_data': serialize_response_data(response),
        'previous_outputs': str(previous_outputs),
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Success result created - Status: {result['response_status']}, "
               f"HTTP: {result['http_status']}, Duration: {duration:.0f}ms, Pass: {result['pass']}")
    
    return result

def create_error_result(chain_id: str, row: pd.Series, call_type: str, error: Exception, 
                       duration: float, merchant_description: str, previous_outputs: Dict[str, Any],
                       request: Any, card_description: str) -> Dict[str, Any]:
    """Create error result with assertion evaluation for negative tests"""
    logger = get_results_logger()
    
    # Initialize payment assertion engine
    assertion_engine = PaymentAssertionEngine()
    
    # Extract HTTP status from error
    http_status = 500  # Default error status
    if hasattr(error, 'status_code'):
        http_status = error.status_code
    elif 'status_code=' in str(error):
        import re
        match = re.search(r'status_code=(\d+)', str(error))
        if match:
            http_status = int(match.group(1))
    
    # Evaluate assertions (might be a negative test expecting this error)
    assertion_result = assertion_engine.evaluate_payment_assertions(
        row, None, http_status, call_type
    )
    
    logger.error(f"Creating error result for {chain_id} - {call_type} - {row['test_id']}: {error}")
    logger.info(f"Assertion result for error: {assertion_result.message}")
    
    error_details = parse_error_response(error)
    
    result = {
        'chain_id': chain_id,
        'test_id': row['test_id'],
        'call_type': call_type,
        'pass': assertion_result.passed,  # ✅ Might be True for negative tests!
        'assertion_message': assertion_result.message,
        'assertion_details': str(assertion_result.details),
        
        # Error data
        'transaction_id': '',
        'response_status': 'ERROR',
        'http_status': http_status,
        'duration_ms': duration,
        'merchant_description': merchant_description,
        'card_description': card_description,
        'amount': row.get('amount', ''),
        'currency': row.get('currency', ''),
        'error_message': str(error),
        'error_type': type(error).__name__,
        'error_details': json.dumps(error_details),
        'request_data': serialize_request_data(request),
        'response_data': '',
        'previous_outputs': str(previous_outputs),
        'timestamp': datetime.now().isoformat()
    }
    
    logger.error(f"Error result created - HTTP: {result['http_status']}, "
                f"Duration: {duration:.0f}ms, Title: {error_details.get('title', 'Unknown')}")
    
    return result

def create_dependency_error_result(chain_id: str, row: pd.Series, call_type: str, 
                                  dependency_error: str) -> Dict[str, Any]:
    """Create result for dependency validation errors"""
    logger = get_results_logger()
    
    logger.warning(f"Creating dependency error result for {chain_id} - {call_type} - {row['test_id']}: {dependency_error}")
    
    result = {
        'chain_id': chain_id,
        'test_id': row['test_id'],
        'call_type': call_type,
        'pass': False,
        'assertion_message': f"Dependency error: {dependency_error}",
        'assertion_details': '',
        
        # Dependency error data
        'transaction_id': '',
        'response_status': 'DEPENDENCY_ERROR',
        'http_status': 0,
        'duration_ms': 0,
        'merchant_description': '',
        'card_description': '',
        'amount': row.get('amount', ''),
        'currency': row.get('currency', ''),
        'error_message': dependency_error,
        'error_type': 'DependencyError',
        'error_details': json.dumps({'title': 'Dependency Error', 'detail': dependency_error}),
        'request_data': '',
        'response_data': '',
        'previous_outputs': '',
        'timestamp': datetime.now().isoformat()
    }
    
    return result

def save_results(results: List[Dict[str, Any]]):
    """Save results to CSV and database"""
    logger = get_results_logger()
    
    if not results:
        logger.warning("No results to save")
        return
    
    logger.info(f"Saving {len(results)} results to CSV and database")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Save to CSV
    csv_path = 'outputs/results.csv'
    df.to_csv(csv_path, index=False)
    logger.info(f"Results saved to CSV: {csv_path}")
    print(f"Results saved to {csv_path}")
    
    # Save to database
    try:
        engine = get_db_engine()
        df.to_sql('test_results', engine, if_exists='append', index=False)
        logger.info(f"Results saved to database: {len(results)} records")
        print(f"Results saved to database ({len(results)} records)")
    except Exception as e:
        logger.error(f"Failed to save to database: {e}")
        print(f"Warning: Failed to save to database: {e}")