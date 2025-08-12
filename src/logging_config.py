"""Centralized logging configuration for the Payment API Testing Framework"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_level='INFO', log_to_file=False, log_file=None):
    """
    Configure logging for the entire application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file as well as console
        log_file: Custom log file path (optional)
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Create formatters
    console_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (always present)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        if log_file is None:
            # Default log file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f'outputs/payment_tests_{timestamp}.log'
        
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"Logging to file: {log_file}")
    
    # Log the configuration
    root_logger.info(f"Logging configured: level={log_level}, file_logging={log_to_file}")
    
    return root_logger

def get_logger(name):
    """
    Get a logger for a specific module
    
    Args:
        name: Logger name (typically __name__ from the calling module)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

# Predefined loggers for different components
def get_data_loader_logger():
    """Get logger for data loading operations"""
    return logging.getLogger('payment_tests.data_loader')

def get_api_logger():
    """Get logger for API operations"""
    return logging.getLogger('payment_tests.api')

def get_request_builder_logger():
    """Get logger for request building"""
    return logging.getLogger('payment_tests.request_builder')

def get_results_logger():
    """Get logger for results handling"""
    return logging.getLogger('payment_tests.results')

def get_main_logger():
    """Get logger for main execution flow"""
    return logging.getLogger('payment_tests.main')

def get_performance_logger():
    """Get logger for performance metrics"""
    return logging.getLogger('payment_tests.performance')

def get_network_token_logger():
    """Get logger for network token operations"""
    return logging.getLogger('payment_tests.network_token')

def get_avs_logger():
    """Get logger for AVS operations"""
    return logging.getLogger('payment_tests.avs')

# Utility functions for structured logging
def log_api_call(logger, call_type, test_id, chain_id, duration_ms=None, success=True, error=None):
    """Log API call with structured information"""
    if success:
        msg = f"[{chain_id}] {call_type} - {test_id}"
        if duration_ms:
            msg += f" ({duration_ms:.0f}ms)"
        logger.info(msg)
    else:
        logger.error(f"[{chain_id}] {call_type} - {test_id} FAILED: {error}")

def log_request_building(logger, call_type, test_id, chain_id, has_avs=False, has_network_token=False):
    """Log request building with feature flags"""
    features = []
    if has_avs:
        features.append("AVS")
    if has_network_token:
        features.append("NetworkToken")
    
    feature_str = f" [{', '.join(features)}]" if features else ""
    logger.debug(f"[{chain_id}] Building {call_type} request for {test_id}{feature_str}")

def log_chain_progress(logger, chain_id, current_step, total_steps, test_id, call_type):
    """Log chain execution progress"""
    logger.info(f"[{chain_id}] Step {current_step}/{total_steps}: {call_type} - {test_id}")

def log_performance_summary(logger, total_calls, total_time, passed, failed, threading_enabled):
    """Log performance summary"""
    avg_time = (total_time / total_calls) if total_calls > 0 else 0
    logger.info(f"Performance Summary: {total_calls} calls, {total_time:.2f}s total, {avg_time:.2f}s avg")
    logger.info(f"Results: {passed} passed, {failed} failed, Threading: {'ON' if threading_enabled else 'OFF'}")