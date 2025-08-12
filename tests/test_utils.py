"""Test utility functions"""

import pytest
import tempfile
import configparser
from unittest.mock import patch, Mock
from src.utils import (
    generate_nonce, generate_random_string, generate_uuid,
    create_temp_config, get_db_engine, clean_request
)

class TestGenerateFunctions:
    """Test random generation functions"""
    
    def test_generate_nonce(self):
        """Test nonce generation"""
        nonce = generate_nonce()
        assert isinstance(nonce, int)
        assert 100000 <= nonce <= 999999
        
        # Test uniqueness (probabilistic)
        nonces = [generate_nonce() for _ in range(100)]
        assert len(set(nonces)) > 90  # Should be mostly unique

    def test_generate_random_string(self):
        """Test random string generation"""
        # Test different lengths
        for length in [1, 5, 10, 40]:
            result = generate_random_string(length)
            assert len(result) == length
            assert result.isalnum()
        
        # Test uniqueness
        strings = [generate_random_string(10) for _ in range(100)]
        assert len(set(strings)) > 90  # Should be mostly unique
        
    def test_generate_random_string_invalid_length(self):
        """Test random string generation with invalid length"""
        with pytest.raises(ValueError, match="Length must be a positive integer"):
            generate_random_string(0)
        
        with pytest.raises(ValueError, match="Length must be a positive integer"):
            generate_random_string(-1)
            
        with pytest.raises(ValueError, match="Length must be a positive integer"):
            generate_random_string("invalid")

    def test_generate_uuid(self):
        """Test UUID generation"""
        uuid = generate_uuid()
        assert isinstance(uuid, str)
        assert len(uuid) == 36
        assert uuid.count('-') == 4
        
        # Test uniqueness
        uuids = [generate_uuid() for _ in range(100)]
        assert len(set(uuids)) == 100  # Should be completely unique

class TestCreateTempConfig:
    """Test temporary config file creation"""
    
    def test_create_temp_config(self):
        """Test temp config creation with valid data"""
        env_data = {
            'integrator': 'Test Integrator',
            'endpoint_host': 'api.test.com',
            'authorization_type': 'OAuth2',
            'oauth2_token_uri': 'https://auth.test.com',
            'connect_timeout': 5,
            'socket_timeout': 300,
            'max_connections': 10
        }
        
        temp_file = create_temp_config(env_data)
        
        try:
            # Verify file was created
            assert temp_file.endswith('.tmp') or 'tmp' in temp_file
            
            # Verify content
            config = configparser.ConfigParser()
            config.read(temp_file)
            
            assert 'AcquiringSDK' in config
            section = config['AcquiringSDK']
            assert section['acquiring.api.integrator'] == 'Test Integrator'
            assert section['acquiring.api.endpoint.host'] == 'api.test.com'
            assert section['acquiring.api.authorizationType'] == 'OAuth2'
            
        finally:
            # Cleanup
            import os
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_create_temp_config_with_nans(self):
        """Test temp config creation with NaN values"""
        import pandas as pd
        
        env_data = {
            'integrator': 'Test Integrator',
            'endpoint_host': 'api.test.com',
            'authorization_type': None,  # Should be skipped
            'oauth2_token_uri': 'https://auth.test.com',
            'connect_timeout': None,  # Should be skipped
        }
        
        temp_file = create_temp_config(env_data)
        
        try:
            config = configparser.ConfigParser()
            config.read(temp_file)
            
            section = config['AcquiringSDK']
            assert 'acquiring.api.authorizationType' not in section
            assert 'acquiring.api.connectTimeout' not in section
            
        finally:
            import os
            if os.path.exists(temp_file):
                os.unlink(temp_file)

class TestCleanRequest:
    """Test request cleaning function"""
    
    def test_clean_request_removes_none_attributes(self):
        """Test that None attributes are removed"""
        request = Mock()
        request.field1 = "value1"
        request.field2 = None
        request.field3 = "value3"
        
        cleaned = clean_request(request)
        
        assert hasattr(cleaned, 'field1')
        assert not hasattr(cleaned, 'field2')
        assert hasattr(cleaned, 'field3')

    def test_clean_request_removes_empty_dicts(self):
        """Test that dictionaries with all None values are removed"""
        request = Mock()
        request.field1 = "value1"
        request.field2 = {'key1': None, 'key2': None}
        request.field3 = {'key1': 'value', 'key2': None}
        
        cleaned = clean_request(request)
        
        assert hasattr(cleaned, 'field1')
        assert not hasattr(cleaned, 'field2')
        assert hasattr(cleaned, 'field3')

    def test_clean_request_preserves_valid_data(self):
        """Test that valid data is preserved"""
        request = Mock()
        request.operation_id = "TEST-123"
        request.amount = 100
        request.currency = "GBP"
        
        cleaned = clean_request(request)
        
        assert cleaned.operation_id == "TEST-123"
        assert cleaned.amount == 100
        assert cleaned.currency == "GBP"

class TestGetDbEngine:
    """Test database engine creation"""
    
    @patch('src.utils.create_engine')
    def test_get_db_engine(self, mock_create_engine):
        """Test database engine creation"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        result = get_db_engine()
        
        mock_create_engine.assert_called_once_with('sqlite:///outputs/local.db')
        assert result == mock_engine