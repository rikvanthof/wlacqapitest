"""Endpoint registry for automatic discovery and registration of API endpoints"""

import importlib
import inspect
from typing import Dict, Any, Callable, List, Optional
from abc import ABC, abstractmethod

class EndpointInterface(ABC):
    """Interface that all endpoints must implement"""
    
    @staticmethod
    @abstractmethod
    def call_api(*args, **kwargs):
        """Execute the API call"""
        pass
    
    @staticmethod
    @abstractmethod
    def build_request(row, *args, **kwargs):
        """Build the request object"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_dependencies() -> List[str]:
        """Return list of required dependencies (e.g., ['payment_id'])"""
        pass
    
    @staticmethod
    @abstractmethod
    def supports_chaining() -> bool:
        """Whether this endpoint can be used in chains"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_output_keys() -> List[str]:
        """What keys this endpoint adds to previous_outputs (e.g., ['payment_id'])"""
        pass

class EndpointRegistry:
    """Registry for automatic endpoint discovery and management"""
    
    _endpoints: Dict[str, EndpointInterface] = {}
    _initialized = False
    
    @classmethod
    def register(cls, call_type: str, endpoint_class: EndpointInterface):
        """Register an endpoint"""
        cls._endpoints[call_type] = endpoint_class
        
    @classmethod
    def get_endpoint(cls, call_type: str) -> Optional[EndpointInterface]:
        """Get endpoint by call_type"""
        if not cls._initialized:
            cls.auto_discover()
        return cls._endpoints.get(call_type)
    
    @classmethod
    def get_all_endpoints(cls) -> Dict[str, EndpointInterface]:
        """Get all registered endpoints"""
        if not cls._initialized:
            cls.auto_discover()
        return cls._endpoints.copy()
    
    @classmethod
    def get_call_functions(cls) -> Dict[str, Callable]:
        """Generate CALL_FUNCTIONS mapping"""
        if not cls._initialized:
            cls.auto_discover()
        return {call_type: endpoint.call_api for call_type, endpoint in cls._endpoints.items()}
    
    @classmethod
    def get_request_builders(cls) -> Dict[str, Callable]:
        """Generate REQUEST_BUILDERS mapping"""
        if not cls._initialized:
            cls.auto_discover()
        return {call_type: endpoint.build_request for call_type, endpoint in cls._endpoints.items()}
    
    @classmethod
    def auto_discover(cls):
        """Auto-discover endpoints in the endpoints package"""
        try:
            # Import all endpoint modules
            from ..endpoints import (
                create_payment_endpoint,
                increment_payment_endpoint,
                capture_payment_endpoint,
                refund_payment_endpoint,
                get_payment_endpoint,
                get_refund_endpoint
            )
            cls._initialized = True
        except ImportError as e:
            print(f"Warning: Could not auto-discover all endpoints: {e}")
    
    @classmethod
    def validate_endpoint(cls, call_type: str, endpoint_class: EndpointInterface) -> bool:
        """Validate that an endpoint implements the required interface"""
        required_methods = ['call_api', 'build_request', 'get_dependencies', 'supports_chaining', 'get_output_keys']
        
        for method in required_methods:
            if not hasattr(endpoint_class, method):
                raise ValueError(f"Endpoint {call_type} missing required method: {method}")
        
        return True

# Decorator for easy registration
def register_endpoint(call_type: str):
    """Decorator to register an endpoint"""
    def decorator(endpoint_class):
        EndpointRegistry.validate_endpoint(call_type, endpoint_class)
        EndpointRegistry.register(call_type, endpoint_class)
        return endpoint_class
    return decorator