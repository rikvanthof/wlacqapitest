"""API call functions with comprehensive logging and HTTP status capture"""

from worldline.acquiring.sdk.v1.domain.api_payment_request import ApiPaymentRequest
from worldline.acquiring.sdk.v1.domain.api_increment_request import ApiIncrementRequest
from worldline.acquiring.sdk.v1.domain.api_capture_request import ApiCaptureRequest
from worldline.acquiring.sdk.v1.domain.api_payment_refund_request import ApiPaymentRefundRequest
from worldline.acquiring.sdk.v1.domain.api_payment_reversal_request import ApiPaymentReversalRequest
from worldline.acquiring.sdk.v1.domain.api_refund_request import ApiRefundRequest
from worldline.acquiring.sdk.v1.domain.api_capture_request_for_refund import ApiCaptureRequestForRefund
from worldline.acquiring.sdk.v1.domain.api_refund_reversal_request import ApiRefundReversalRequest
from worldline.acquiring.sdk.v1.domain.api_account_verification_request import ApiAccountVerificationRequest

from worldline.acquiring.sdk.v1.domain.amount_data import AmountData

import threading
import uuid
import logging

logger = logging.getLogger(__name__)

# Thread-local storage for HTTP status codes and trace IDs
_thread_local = threading.local()

def set_last_http_status(status_code):
    """Store the last HTTP status code for this thread"""
    logger.debug(f"Setting HTTP status code: {status_code}")
    _thread_local.last_status_code = status_code

def get_last_http_status():
    """Get the last captured HTTP status code for this thread"""
    status = getattr(_thread_local, 'last_status_code', None)
    logger.debug(f"Retrieved HTTP status code: {status}")
    return status

def set_trace_id(trace_id):
    """Store the current trace ID for this thread"""
    logger.debug(f"Setting trace ID: {trace_id}")
    _thread_local.trace_id = trace_id

def get_trace_id():
    """Get the current trace ID for this thread"""
    trace_id = getattr(_thread_local, 'trace_id', None)
    logger.debug(f"Retrieved trace ID: {trace_id}")
    return trace_id

def generate_trace_id():
    """Generate a new trace ID and store it"""
    trace_id = str(uuid.uuid4())
    logger.info(f"Generated new trace ID: {trace_id}")
    set_trace_id(trace_id)
    return trace_id

def _patch_http_methods():
    """Patch HTTP methods to capture status codes and add trace headers"""
    logger.info("Attempting to patch HTTP methods for status capture and trace headers")
    
    try:
        from worldline.acquiring.sdk.communication.default_connection import DefaultConnection
        
        # Check if already patched
        if hasattr(DefaultConnection, '_http_status_patched'):
            logger.info("HTTP methods already patched, skipping")
            return
        
        logger.debug("Patching DefaultConnection HTTP methods")
        
        # Store original methods
        original_post = getattr(DefaultConnection, 'post', None)
        original_get = getattr(DefaultConnection, 'get', None)
        
        logger.debug(f"Original POST method found: {original_post is not None}")
        logger.debug(f"Original GET method found: {original_get is not None}")
        
        def add_trace_header(headers):
            """Add Trace-ID header to existing headers"""
            trace_id = get_trace_id()
            if not trace_id:
                logger.debug("No trace ID available, skipping header addition")
                return headers
            
            logger.debug(f"Adding Trace-ID header: {trace_id}")
            
            # Handle different header formats
            if headers is None:
                try:
                    from worldline.acquiring.sdk.communication.request_header import RequestHeader
                    logger.debug("Creating new RequestHeader list with Trace-ID")
                    return [RequestHeader('Trace-ID', trace_id)]
                except ImportError:
                    logger.warning("RequestHeader import failed, returning original headers")
                    return headers
            elif isinstance(headers, list):
                # Check if it's a list of RequestHeader objects
                if headers and hasattr(headers[0], '__class__') and 'RequestHeader' in str(headers[0].__class__):
                    try:
                        from worldline.acquiring.sdk.communication.request_header import RequestHeader
                        modified_headers = headers.copy() if headers else []
                        modified_headers.append(RequestHeader('Trace-ID', trace_id))
                        logger.debug(f"Added Trace-ID to RequestHeader list ({len(modified_headers)} total headers)")
                        return modified_headers
                    except ImportError:
                        logger.warning("RequestHeader import failed for list modification")
                        return headers
                else:
                    # Regular list of tuples
                    modified_headers = headers.copy() if headers else []
                    modified_headers.append(('Trace-ID', trace_id))
                    logger.debug(f"Added Trace-ID to tuple list ({len(modified_headers)} total headers)")
                    return modified_headers
            elif isinstance(headers, dict):
                modified_headers = headers.copy()
                modified_headers['Trace-ID'] = trace_id
                logger.debug(f"Added Trace-ID to dict headers ({len(modified_headers)} total headers)")
                return modified_headers
            else:
                logger.debug(f"Unknown header format: {type(headers)}, returning original")
                return headers
            return modified_headers
        
        def patched_post(self, uri, request_headers, body):
            logger.debug(f"Patched POST call to: {uri}")
            # Add trace header
            modified_headers = add_trace_header(request_headers)
            response = original_post(self, uri, modified_headers, body)
            # Handle tuple response format: (status_code, headers, body_generator)
            if isinstance(response, tuple) and len(response) >= 1:
                status_code = response[0]
                set_last_http_status(status_code)
                logger.info(f"POST response: {status_code} for {uri}")
            else:
                logger.debug(f"POST response format: {type(response)}")
            return response
        
        def patched_get(self, uri, request_headers):
            logger.debug(f"Patched GET call to: {uri}")
            # Add trace header
            modified_headers = add_trace_header(request_headers)
            response = original_get(self, uri, modified_headers)
            # Handle tuple response format: (status_code, headers, body_generator)
            if isinstance(response, tuple) and len(response) >= 1:
                status_code = response[0]
                set_last_http_status(status_code)
                logger.info(f"GET response: {status_code} for {uri}")
            else:
                logger.debug(f"GET response format: {type(response)}")
            return response
        
        # Apply patches
        if original_post:
            DefaultConnection.post = patched_post
            logger.debug("POST method patched successfully")
        if original_get:
            DefaultConnection.get = patched_get
            logger.debug("GET method patched successfully")
        
        DefaultConnection._http_status_patched = True
        logger.info("HTTP status code capture and Trace-ID headers enabled successfully")
        print("HTTP status code capture and Trace-ID headers enabled")
        
    except Exception as e:
        logger.error(f"Error patching HTTP methods: {e}", exc_info=True)
        print(f"Error patching HTTP methods: {e}")

# Apply the patch when this module is imported
logger.info("Initializing HTTP method patching")
_patch_http_methods()

def create_payment(client, acquirer_id, merchant_id, request):
    """POST /processing/v1/{acquirerId}/{merchantId}/payments - Create payment"""
    logger.info(f"Creating payment - Acquirer: {acquirer_id}, Merchant: {merchant_id}")
    logger.debug(f"Request type: {type(request).__name__}")
    
    trace_id = generate_trace_id()
    
    try:
        logger.debug("Calling SDK process_payment method")
        
        # === FINAL REQUEST DEBUG ===
        logger.debug("=== FINAL REQUEST DEBUG ===")
        logger.debug(f"Request type: {type(request).__name__}")

        if hasattr(request, 'card_payment_data'):
            cpd = request.card_payment_data
            logger.debug(f"CardPaymentData type: {type(cpd).__name__}")
            
            # Check all attributes
            cpd_attrs = [attr for attr in dir(cpd) if not attr.startswith('_')]
            logger.debug(f"CardPaymentData attributes: {cpd_attrs}")
            
            # Check specific nested objects
            if hasattr(cpd, 'address_verification_data'):
                avs = cpd.address_verification_data
                logger.debug(f"AVS object type: {type(avs).__name__}")
                logger.debug(f"AVS object: {avs.__dict__ if hasattr(avs, '__dict__') else 'NO_DICT'}")
            else:
                logger.debug("NO address_verification_data attribute")
            
            # FIXED: Correct attribute name is 'ecommerce_data' not 'e_commerce_data'
            if hasattr(cpd, 'ecommerce_data'):
                ecd = cpd.ecommerce_data
                logger.debug(f"ECommerce object type: {type(ecd).__name__}")
                logger.debug(f"ECommerce object: {ecd.__dict__ if hasattr(ecd, '__dict__') else 'NO_DICT'}")
            else:
                logger.debug("NO ecommerce_data attribute")
            
            if hasattr(cpd, 'network_token_data'):
                ntd = cpd.network_token_data
                logger.debug(f"NetworkToken object type: {type(ntd).__name__}")
                logger.debug(f"NetworkToken object: {ntd.__dict__ if hasattr(ntd, '__dict__') else 'NO_DICT'}")
            else:
                logger.debug("NO network_token_data attribute")

        logger.debug("=== END DEBUG ===")
        
        logger.debug(f"Final request dictionary: {request.to_dictionary()}")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).payments().process_payment(request)
        
        # Log response details
        if hasattr(response, 'payment_id'):
            logger.info(f"Payment created successfully - ID: {response.payment_id}, Trace: {trace_id}")
        else:
            logger.info(f"Payment creation response received - Trace: {trace_id}")
        
        if hasattr(response, 'status'):
            logger.debug(f"Payment status: {response.status}")
        
        return response
        
    except Exception as e:
        logger.error(f"Payment creation failed - Acquirer: {acquirer_id}, Merchant: {merchant_id}, Trace: {trace_id}, Error: {e}")
        raise

def increment_auth(client, acquirer_id, merchant_id, payment_id, request):
    """POST /processing/v1/{acquirerId}/{merchantId}/payments/{paymentId}/increments - Increment authorization"""
    logger.info(f"Incrementing authorization - Payment: {payment_id}, Acquirer: {acquirer_id}, Merchant: {merchant_id}")
    logger.debug(f"Request type: {type(request).__name__}")
    
    trace_id = generate_trace_id()
    
    try:
        logger.debug("Calling SDK increment_payment method")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).payments().increment_payment(payment_id, request)
        
        logger.info(f"Authorization incremented successfully - Payment: {payment_id}, Trace: {trace_id}")
        
        if hasattr(response, 'payment') and hasattr(response.payment, 'status'):
            logger.debug(f"Payment status after increment: {response.payment.status}")
        
        return response
        
    except Exception as e:
        logger.error(f"Authorization increment failed - Payment: {payment_id}, Trace: {trace_id}, Error: {e}")
        raise

def capture(client, acquirer_id, merchant_id, payment_id, request):
    """POST /processing/v1/{acquirerId}/{merchantId}/payments/{paymentId}/captures - Capture payment"""
    logger.info(f"Capturing payment - Payment: {payment_id}, Acquirer: {acquirer_id}, Merchant: {merchant_id}")
    logger.debug(f"Request type: {type(request).__name__}")
    
    trace_id = generate_trace_id()
    
    try:
        logger.debug("Calling SDK simple_capture_of_payment method")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).payments().simple_capture_of_payment(payment_id, request)
        
        logger.info(f"Payment captured successfully - Payment: {payment_id}, Trace: {trace_id}")
        
        if hasattr(response, 'status'):
            logger.debug(f"Capture status: {response.status}")
        
        return response
        
    except Exception as e:
        logger.error(f"Payment capture failed - Payment: {payment_id}, Trace: {trace_id}, Error: {e}")
        raise

def refund(client, acquirer_id, merchant_id, payment_id, request):
    """POST /processing/v1/{acquirerId}/{merchantId}/payments/{paymentId}/refunds - Refund payment"""
    logger.info(f"Creating refund - Payment: {payment_id}, Acquirer: {acquirer_id}, Merchant: {merchant_id}")
    logger.debug(f"Request type: {type(request).__name__}")
    
    trace_id = generate_trace_id()
    
    try:
        logger.debug("Calling SDK create_refund method")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).payments().create_refund(payment_id, request)
        
        # Log refund details
        if hasattr(response, 'refund') and hasattr(response.refund, 'refund_id'):
            logger.info(f"Refund created successfully - ID: {response.refund.refund_id}, Payment: {payment_id}, Trace: {trace_id}")
        else:
            logger.info(f"Refund creation response received - Payment: {payment_id}, Trace: {trace_id}")
        
        if hasattr(response, 'refund') and hasattr(response.refund, 'status'):
            logger.debug(f"Refund status: {response.refund.status}")
        
        return response
        
    except Exception as e:
        logger.error(f"Refund creation failed - Payment: {payment_id}, Trace: {trace_id}, Error: {e}")
        raise

def get_payment(client, acquirer_id, merchant_id, payment_id):
    """GET /processing/v1/{acquirerId}/{merchantId}/payments/{paymentId} - Retrieve payment"""
    logger.info(f"Retrieving payment - Payment: {payment_id}, Acquirer: {acquirer_id}, Merchant: {merchant_id}")
    
    trace_id = generate_trace_id()
    
    try:
        logger.debug("Calling SDK get_payment_status method")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).payments().get_payment_status(payment_id, None)
        
        logger.info(f"Payment retrieved successfully - Payment: {payment_id}, Trace: {trace_id}")
        
        if hasattr(response, 'status'):
            logger.debug(f"Retrieved payment status: {response.status}")
        
        return response
        
    except Exception as e:
        logger.error(f"Payment retrieval failed - Payment: {payment_id}, Trace: {trace_id}, Error: {e}")
        raise

def get_refund(client, acquirer_id, merchant_id, refund_id):
    """GET /processing/v1/{acquirerId}/{merchantId}/refunds/{refundId} - Retrieve refund"""
    logger.info(f"Retrieving refund - Refund: {refund_id}, Acquirer: {acquirer_id}, Merchant: {merchant_id}")
    
    trace_id = generate_trace_id()
    
    try:
        logger.debug("Calling SDK get_refund method")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).refunds().get_refund(refund_id, None)
        
        logger.info(f"Refund retrieved successfully - Refund: {refund_id}, Trace: {trace_id}")
        
        if hasattr(response, 'status'):
            logger.debug(f"Retrieved refund status: {response.status}")
        
        return response
        
    except Exception as e:
        logger.error(f"Refund retrieval failed - Refund: {refund_id}, Trace: {trace_id}, Error: {e}")
        raise

def reverse_authorization_call(client, acquirer_id, merchant_id, payment_id, request):
    """Execute reverse authorization API call"""
    try:
        logger.info(f"Executing reverse authorization - Acquirer: {acquirer_id}, Payment: {payment_id}")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).payments(payment_id).authorization_reversals().create(request)
        logger.info(f"Reverse authorization successful - Payment: {payment_id}")
        return response
    except Exception as e:
        logger.error(f"Reverse authorization failed - Payment: {payment_id}, Error: {e}")
        raise

def standalone_refund_call(client, acquirer_id, merchant_id, request):
    """Execute standalone refund API call"""
    try:
        logger.info(f"Executing standalone refund - Acquirer: {acquirer_id}")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).refunds().create(request)
        logger.info(f"Standalone refund successful - Refund ID: {getattr(response, 'refund_id', 'unknown')}")
        return response
    except Exception as e:
        logger.error(f"Standalone refund failed - Error: {e}")
        raise

def capture_refund_call(client, acquirer_id, merchant_id, refund_id, request):
    """Execute capture refund API call"""
    try:
        logger.info(f"Executing capture refund - Acquirer: {acquirer_id}, Refund: {refund_id}")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).refunds(refund_id).captures().create(request)
        logger.info(f"Capture refund successful - Refund: {refund_id}")
        return response
    except Exception as e:
        logger.error(f"Capture refund failed - Refund: {refund_id}, Error: {e}")
        raise

def reverse_refund_authorization_call(client, acquirer_id, merchant_id, refund_id, request):
    """Execute reverse refund authorization API call"""
    try:
        logger.info(f"Executing reverse refund authorization - Acquirer: {acquirer_id}, Refund: {refund_id}")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).refunds(refund_id).authorization_reversals().create(request)
        logger.info(f"Reverse refund authorization successful - Refund: {refund_id}")
        return response
    except Exception as e:
        logger.error(f"Reverse refund authorization failed - Refund: {refund_id}, Error: {e}")
        raise
    
def ping_call(client):
    """Execute ping API call - simplest possible!"""
    try:
        logger.info("Executing ping - testing API connectivity")
        response = client.v1().ping()
        logger.info("Ping successful - API is reachable")
        return response
    except Exception as e:
        logger.error(f"Ping failed - API connectivity issue: {e}")
        raise

def technical_reversal_call(client, acquirer_id, merchant_id, original_operation_id, request):
    """Execute technical reversal API call"""
    try:
        logger.info(f"Executing technical reversal - Acquirer: {acquirer_id}, Original Operation: {original_operation_id}")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).operations(original_operation_id).reverse().create(request)
        logger.info(f"Technical reversal successful - Original Operation: {original_operation_id}")
        return response
    except Exception as e:
        logger.error(f"Technical reversal failed - Original Operation: {original_operation_id}, Error: {e}")
        raise

def account_verification_call(client, acquirer_id, merchant_id, request):
    """Execute account verification API call"""
    try:
        logger.info(f"Executing account verification - Acquirer: {acquirer_id}")
        response = client.v1().acquirer(acquirer_id).merchant(merchant_id).account_verifications().create(request)
        logger.info(f"Account verification successful - Operation ID: {getattr(request, 'operation_id', 'unknown')}")
        return response
    except Exception as e:
        logger.error(f"Account verification failed - Error: {e}")
        raise