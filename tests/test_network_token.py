"""Fixed unit tests for network token functionality"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.network_token import apply_network_token_data

class TestNetworkToken:
    """Test network token data application"""

    @pytest.fixture
    def mock_request(self):
        """Mock request object with card payment data"""
        request = Mock()
        request.card_payment_data = Mock()
        request.card_payment_data.card_data = Mock()
        return request

    @pytest.fixture
    def mock_networktokens_df(self):
        """Mock network tokens DataFrame"""
        return pd.DataFrame({
            'network_token': ['4111111111111111'],
            'token_expiry_date': ['1225'],
            'cryptogram': ['ABC123DEF456'],
            'eci': ['05']
        }, index=['nt1'])

    def test_apply_network_token_missing_id(self, mock_request, mock_networktokens_df):
        """Test network token with missing ID"""
        row = pd.Series({
            'network_token_data': 'nonexistent'
        })
        
        # ✅ Fixed: Function throws ValueError, not KeyError
        with pytest.raises(ValueError, match="Network Token ID nonexistent not found"):
            apply_network_token_data(mock_request, row, mock_networktokens_df)

    # ... rest of the tests remain the same