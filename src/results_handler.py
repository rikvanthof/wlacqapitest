"""Handle test results writing and database operations"""

import pandas as pd
import json
import re
import logging
from .utils import get_db_engine
from .api_calls import get_last_http_status, get_trace_id
from .response_utils import get_response_status
from threading import Lock

logger = logging.getLogger(__name__)
db_lock = Lock()

def parse_error_response(exception_message):
    """Parse error response from exception message to extract title and detail"""
    logger.debug(f"Parsing error response from exception: {str(exception_message)[:200]}...")
    
    error_info = {
        'title': None,
        'detail': None,
        'response_body': None
    }
    
    try:
        # Try to extract response_body from exception message
        response_body_match = re.search(r"response_body='([^']*)'|response_body=\"([^\"]*)\"", str(exception_message))
        
        if response_body_match:
            response_body = response_body_match.group(1) or response_body_match.group(2)
            logger.debug(f"Extracted response body: {response_body[:100]}...")
            
            # Try to parse as JSON
            try:
                json_data = json.loads(response_body)
                # Store the clean JSON response body
                error_info['response_body'] = response_body
                error_info['title'] = json_data.get('title')
                error_info['detail'] = json_data.get('detail')
                logger.debug(f"Parsed JSON error - title: {error_info['title']}, detail: {error_info['detail'][:100] if error_info['detail'] else None}...")
                return error_info
            except json.JSONDecodeError:
                logger.debug("Response body is not valid JSON, treating as HTML/text")
                # Not JSON, might be HTML or plain text
                error_info['response_body'] = response_body
                
                # Try to extract title from HTML <title> tags
                html_title_match = re.search(r'<title[^>]*>([^<]*)</title>', response_body, re.IGNORECASE)
                if html_title_match:
                    error_info['title'] = html_title_match.group(1).strip()
                    logger.debug(f"Extracted HTML title: {error_info['title']}")
                
                # For HTML responses, use first part as detail (truncated)
                if len(response_body) > 200:
                    error_info['detail'] = response_body[:200] + "..."
                else:
                    error_info['detail'] = response_body
                
                logger.debug(f"Parsed HTML/text error - title: {error_info['title']}, detail length: {len(error_info['detail'])}")
                return error_info
        else:
            logger.debug("No response_body found in exception message")
        
        # If no response_body found, use the exception message as detail
        error_info['detail'] = str(exception_message)
        logger.debug("Using exception message as error detail")
        
    except Exception as e:
        # If parsing fails, fall back to using the original exception message
        error_info['detail'] = str(exception_message)
        logger.warning(f"Could not parse error response: {e}")
        print(f"Warning: Could not parse error response: {e}")
    
    return error_info

def get_payment_id(response, call_type, previous_outputs):
    """Extract payment_id for tracking payment relationships"""
    logger.debug(f"Extracting payment_id for call_type: {call_type}")
    
    if call_type == 'create_payment':
        # Handle case where response is None (API call failed)
        if response is None:
            logger.debug("Response is None for create_payment, cannot extract payment_id")
            return None
        payment_id = response.payment_id
        logger.debug(f"Extracted payment_id from create_payment response: {payment_id}")
        return payment_id
    elif call_type in ['increment_payment', 'capture_payment', 'refund_payment', 'get_payment']:
        # These operations work on existing payments
        payment_id = previous_outputs.get('payment_id')
        logger.debug(f"Using existing payment_id from previous outputs: {payment_id}")
        return payment_id
    else:
        logger.debug(f"No payment_id extraction needed for call_type: {call_type}")
        return None

def get_refund_id(response, call_type, previous_outputs):
    """Extract refund_id for tracking refund relationships"""
    logger.debug(f"Extracting refund_id for call_type: {call_type}")
    
    if call_type == 'refund_payment':
        # Handle case where response is None (API call failed)
        if response is None:
            logger.debug("Response is None for refund_payment, cannot extract refund_id")
            return None
        # Extract refund_id from nested structure
        refund_id = response.refund.refund_id if hasattr(response, 'refund') else None
        logger.debug(f"Extracted refund_id from refund_payment response: {refund_id}")
        return refund_id
    elif call_type == 'get_refund':
        # This operation works on existing refunds
        refund_id = previous_outputs.get('refund_id')
        logger.debug(f"Using existing refund_id from previous outputs: {refund_id}")
        return refund_id
    else:
        logger.debug(f"No refund_id extraction needed for call_type: {call_type}")
        return None

def format_duration(duration_ms):
    """Format duration to whole milliseconds"""
    formatted = round(duration_ms)
    logger.debug(f"Formatted duration: {duration_ms} -> {formatted} ms")
    return formatted

def format_http_status(http_status):
    """Format HTTP status as integer"""
    if http_status is None:
        logger.debug("HTTP status is None")
        return None
    try:
        formatted = int(float(http_status))
        logger.debug(f"Formatted HTTP status: {http_status} -> {formatted}")
        return formatted
    except (ValueError, TypeError):
        logger.debug(f"Could not format HTTP status as integer: {http_status}")
        return http_status

def create_success_result(chain_id, row, call_type, response, duration, merchant_description, previous_outputs, request=None, card_description=None):
    """Create a result record for successful API calls"""
    logger.info(f"Creating success result for {chain_id} - {call_type} - {row['test_id']}")
    
    # Convert response to JSON format
    response_body = None
    try:
        if hasattr(response, 'to_dictionary'):
            import json
            response_body = json.dumps(response.to_dictionary(), indent=None)
            logger.debug(f"Converted response to JSON: {len(response_body)} characters")
        else:
            response_body = str(response)
            logger.debug(f"Converted response to string: {len(response_body)} characters")
    except Exception as e:
        logger.warning(f"Could not convert response to JSON: {e}")
        print(f"Warning: Could not convert response to JSON: {e}")
        response_body = str(response)
    
    # Convert request to JSON format
    request_body = None
    if request is not None:
        try:
            if hasattr(request, 'to_dictionary'):
                import json
                request_body = json.dumps(request.to_dictionary(), indent=None)
                logger.debug(f"Converted request to JSON: {len(request_body)} characters")
            else:
                request_body = str(request)
                logger.debug(f"Converted request to string: {len(request_body)} characters")
        except Exception as e:
            logger.warning(f"Could not convert request to JSON: {e}")
            print(f"Warning: Could not convert request to JSON: {e}")
            request_body = str(request)
    else:
        logger.debug("No request body to convert")
    
    # Get additional data
    trace_id = get_trace_id()
    payment_id = get_payment_id(response, call_type, previous_outputs)
    refund_id = get_refund_id(response, call_type, previous_outputs)
    status = get_response_status(response, call_type)
    http_status = format_http_status(get_last_http_status())
    duration_formatted = format_duration(duration)
    
    is_pass = status in ['CAPTURED', 'REFUNDED', 'APPROVED', 'AUTHORIZED']
    
    logger.info(f"Success result created - Status: {status}, HTTP: {http_status}, Duration: {duration_formatted}ms, Pass: {is_pass}")
    
    return {
        'chain_id': chain_id,
        'step_order': row['step_order'],
        'call_type': call_type,
        'test_id': row['test_id'],
        'trace_id': trace_id,
        'payment_id': payment_id,
        'refund_id': refund_id,
        'merchant_description': merchant_description,
        'card_description': card_description or 'N/A',
        'request_body': request_body,
        'response_body': response_body,
        'status': status,
        'http_status': http_status,
        'duration_ms': duration_formatted,
        'pass': is_pass,
        'error': None,
        'error_title': None,
        'error_detail': None
    }

def create_error_result(chain_id, row, call_type, error, duration, merchant_description, previous_outputs, request=None, card_description=None):
    """Create a result record for failed API calls"""
    logger.error(f"Creating error result for {chain_id} - {call_type} - {row['test_id']}: {str(error)[:100]}...")
    
    # Parse error response to extract structured information
    error_info = parse_error_response(str(error))
    
    # Convert request to JSON format
    request_body = None
    if request is not None:
        try:
            if hasattr(request, 'to_dictionary'):
                import json
                request_body = json.dumps(request.to_dictionary(), indent=None)
                logger.debug(f"Converted request to JSON: {len(request_body)} characters")
            else:
                request_body = str(request)
                logger.debug(f"Converted request to string: {len(request_body)} characters")
        except Exception as e:
            logger.warning(f"Could not convert request to JSON: {e}")
            print(f"Warning: Could not convert request to JSON: {e}")
            request_body = str(request)
    else:
        logger.debug("No request body to convert")
    
    # Get additional data
    trace_id = get_trace_id()
    payment_id = get_payment_id(None, call_type, previous_outputs)
    refund_id = get_refund_id(None, call_type, previous_outputs)
    http_status = format_http_status(get_last_http_status())
    duration_formatted = format_duration(duration)
    
    logger.error(f"Error result created - HTTP: {http_status}, Duration: {duration_formatted}ms, Title: {error_info['title']}")
    
    return {
        'chain_id': chain_id,
        'step_order': row['step_order'],
        'call_type': call_type,
        'test_id': row['test_id'],
        'trace_id': trace_id,
        'payment_id': payment_id,
        'refund_id': refund_id,
        'merchant_description': merchant_description,
        'card_description': card_description or 'N/A',
        'request_body': request_body,
        'response_body': error_info['response_body'],
        'status': None,
        'http_status': http_status,
        'duration_ms': duration_formatted,
        'pass': False,
        'error': str(error),
        'error_title': error_info['title'],
        'error_detail': error_info['detail']
    }

def create_dependency_error_result(chain_id, row, call_type, error_msg):
    """Create a result record for dependency errors (missing payment_id, etc.)"""
    logger.error(f"Creating dependency error result for {chain_id} - {call_type} - {row['test_id']}: {error_msg}")
    
    return {
        'chain_id': chain_id,
        'step_order': row['step_order'],
        'call_type': call_type,
        'test_id': row['test_id'],
        'trace_id': None,
        'payment_id': None,
        'refund_id': None,
        'merchant_description': None,
        'card_description': None,
        'request_body': None,
        'response_body': None,
        'status': None,
        'http_status': None,
        'duration_ms': 0,
        'pass': False,
        'error': error_msg,
        'error_title': None,
        'error_detail': error_msg
    }

def save_results(results):
    """Save results to both CSV and database (thread-safe)"""
    logger.info(f"Saving {len(results)} results to CSV and database")
    
    if not results:
        logger.warning("No results to save")
        print("No results to save")
        return
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    logger.debug(f"Created DataFrame with shape: {results_df.shape}")
    
    # Save to CSV (thread-safe with lock)
    with db_lock:
        csv_path = 'outputs/results.csv'
        try:
            results_df.to_csv(csv_path, index=False)
            logger.info(f"Results saved to CSV: {csv_path}")
            print(f"Results saved to {csv_path}")
        except Exception as e:
            logger.error(f"Failed to save results to CSV: {e}")
            print(f"Error: Could not save to CSV: {e}")
            return
        
        # Save to database
        try:
            logger.debug("Attempting to save results to database")
            engine = get_db_engine()
            results_df.to_sql('runs', engine, if_exists='append', index=False)
            logger.info(f"Results saved to database: {len(results)} records")
            print(f"Results saved to database ({len(results)} records)")
        except Exception as e:
            logger.warning(f"Could not save to database: {e}")
            print(f"Warning: Could not save to database: {e}")