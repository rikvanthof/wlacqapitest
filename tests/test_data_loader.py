"""Test data loading functions - updated for ConfigurationManager"""

import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import patch, Mock
from src.data_loader import load_data
from src.config.config_manager import ConfigurationError

class TestLoadData:
    """Test data loading function"""
    
    @patch('src.config.config_manager.ConfigurationManager.load_all_configs')
    def test_load_data_success(self, mock_load_configs):
        """Test successful data loading"""
        # Mock the config set that's returned
        mock_config_set = Mock()
        mock_config_set.environments = pd.DataFrame({'env': ['test']}).set_index('env')
        mock_config_set.cards = pd.DataFrame({'card_id': ['card1']}).set_index('card_id')
        mock_config_set.merchants = pd.DataFrame({'merchant': ['m1'], 'env': ['test']}).set_index(['env', 'merchant'])
        mock_config_set.address = pd.DataFrame({'address_id': ['addr1']}).set_index('address_id')
        mock_config_set.networktokens = pd.DataFrame({'token_id': ['token1']}).set_index('token_id')
        mock_config_set.threeds = pd.DataFrame({'threeds_id': ['3ds1']}).set_index('threeds_id')
        mock_config_set.cardonfile = pd.DataFrame({'cof_id': ['cof1']}).set_index('cof_id')  # ✅ Added
        mock_config_set.tests = pd.DataFrame({'test_id': ['TEST001'], 'chain_id': ['chain1']})
        
        mock_load_configs.return_value = mock_config_set
        
        result = load_data('test_file.csv')
        
        # Should return 8 items now (including cardonfile)
        assert len(result) == 8
        environments, cards, merchants, address, networktokens, threeds, cardonfile, tests = result
        
        # Verify each item
        assert len(environments) == 1
        assert len(cards) == 1
        assert len(merchants) == 1
        assert len(address) == 1
        assert len(networktokens) == 1
        assert len(threeds) == 1
        assert len(cardonfile) == 1  # ✅ Added verification
        assert len(tests) == 1

    @patch('src.config.config_manager.ConfigurationManager.load_all_configs')
    def test_load_data_address_data_types(self, mock_load_configs):
        """Test address data loading with proper data types"""
        mock_config_set = Mock()
        mock_config_set.environments = pd.DataFrame().set_index(pd.Index([], name='env'))
        mock_config_set.cards = pd.DataFrame().set_index(pd.Index([], name='card_id'))
        mock_config_set.merchants = pd.DataFrame().set_index(pd.MultiIndex.from_tuples([], names=['env', 'merchant']))
        mock_config_set.address = pd.DataFrame({
            'address_id': ['addr1'],
            'cardholder_postal_code': ['12345'],
            'cardholder_address': ['123 Main St']
        }).set_index('address_id')
        mock_config_set.networktokens = pd.DataFrame().set_index(pd.Index([], name='token_id'))
        mock_config_set.threeds = pd.DataFrame().set_index(pd.Index([], name='threeds_id'))
        mock_config_set.cardonfile = pd.DataFrame().set_index(pd.Index([], name='cof_id'))  # ✅ Added
        # Fix: Add chain_id column to prevent KeyError
        mock_config_set.tests = pd.DataFrame(columns=['chain_id', 'test_id'])
        
        mock_load_configs.return_value = mock_config_set
        
        _, _, _, address, _, _, _, _ = load_data('test_file.csv')  # ✅ Updated unpacking
        
        # Verify address data types
        assert len(address) == 1
        assert 'addr1' in address.index

    @patch('src.config.config_manager.ConfigurationManager.load_all_configs')
    def test_load_data_with_networktokens(self, mock_load_configs):
        """Test loading with network tokens"""
        mock_config_set = Mock()
        mock_config_set.environments = pd.DataFrame().set_index(pd.Index([], name='env'))
        mock_config_set.cards = pd.DataFrame().set_index(pd.Index([], name='card_id'))
        mock_config_set.merchants = pd.DataFrame().set_index(pd.MultiIndex.from_tuples([], names=['env', 'merchant']))
        mock_config_set.address = pd.DataFrame().set_index(pd.Index([], name='address_id'))
        mock_config_set.networktokens = pd.DataFrame({
            'networktoken_id': ['token1'],
            'wallet_id': ['103']
        }).set_index('networktoken_id')
        mock_config_set.threeds = pd.DataFrame().set_index(pd.Index([], name='threeds_id'))
        mock_config_set.cardonfile = pd.DataFrame().set_index(pd.Index([], name='cof_id'))  # ✅ Added
        # Fix: Add chain_id column to prevent KeyError
        mock_config_set.tests = pd.DataFrame(columns=['chain_id', 'test_id'])
        
        mock_load_configs.return_value = mock_config_set
        
        environments, cards, merchants, address, networktokens, threeds, cardonfile, tests = load_data('test_file.csv')  # ✅ Updated unpacking
        
        # Should return 8 items including networktokens and cardonfile
        assert len(networktokens) == 1
        assert 'token1' in networktokens.index

    @patch('src.config.config_manager.ConfigurationManager.load_all_configs')
    def test_load_data_file_not_found(self, mock_load_configs):
        """Test data loading with non-existent file"""
        mock_load_configs.side_effect = ConfigurationError("Test file not found in any location: non_existent_file.csv")
        
        with pytest.raises(ConfigurationError):
            load_data('non_existent_file.csv')

    @patch('src.config.config_manager.ConfigurationManager.load_all_configs')
    def test_load_data_sorting(self, mock_load_configs):
        """Test that tests are sorted properly"""
        mock_config_set = Mock()
        mock_config_set.environments = pd.DataFrame().set_index(pd.Index([], name='env'))
        mock_config_set.cards = pd.DataFrame().set_index(pd.Index([], name='card_id'))
        mock_config_set.merchants = pd.DataFrame().set_index(pd.MultiIndex.from_tuples([], names=['env', 'merchant']))
        mock_config_set.address = pd.DataFrame().set_index(pd.Index([], name='address_id'))
        mock_config_set.networktokens = pd.DataFrame().set_index(pd.Index([], name='networktoken_id'))
        mock_config_set.threeds = pd.DataFrame().set_index(pd.Index([], name='threeds_id'))
        mock_config_set.cardonfile = pd.DataFrame().set_index(pd.Index([], name='cof_id'))  # ✅ Added
        mock_config_set.tests = pd.DataFrame({
            'test_id': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
            'chain_id': ['chain1', 'chain1', 'chain2', 'chain2'],
            'step_order': [1, 2, 1, 2]
        })
        
        mock_load_configs.return_value = mock_config_set
        
        _, _, _, _, _, _, _, tests = load_data('test_file.csv')  # ✅ Updated unpacking
        
        # Verify data structure (tests should be accessible)
        assert len(tests) == 4

    @patch('src.config.config_manager.ConfigurationManager.load_all_configs')
    def test_load_data_with_cardonfile(self, mock_load_configs):
        """Test loading with card-on-file configurations"""
        mock_config_set = Mock()
        mock_config_set.environments = pd.DataFrame().set_index(pd.Index([], name='env'))
        mock_config_set.cards = pd.DataFrame().set_index(pd.Index([], name='card_id'))
        mock_config_set.merchants = pd.DataFrame().set_index(pd.MultiIndex.from_tuples([], names=['env', 'merchant']))
        mock_config_set.address = pd.DataFrame().set_index(pd.Index([], name='address_id'))
        mock_config_set.networktokens = pd.DataFrame().set_index(pd.Index([], name='networktoken_id'))
        mock_config_set.threeds = pd.DataFrame().set_index(pd.Index([], name='threeds_id'))
        mock_config_set.cardonfile = pd.DataFrame({
            'card_on_file_id': ['FIRSTUCOF-CIT'],
            'is_initial_transaction': [True]
        }).set_index('card_on_file_id')
        mock_config_set.tests = pd.DataFrame(columns=['chain_id', 'test_id'])
        
        mock_load_configs.return_value = mock_config_set
        
        environments, cards, merchants, address, networktokens, threeds, cardonfile, tests = load_data('test_file.csv')
        
        # Verify card-on-file data
        assert len(cardonfile) == 1
        assert 'FIRSTUCOF-CIT' in cardonfile.index