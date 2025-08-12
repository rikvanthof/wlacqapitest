"""Focused assertion engine for payment API responses"""

import pandas as pd
from typing import Any, Optional, Dict, List
from ..logging_config import get_main_logger

class PaymentAssertionResult:
    """Container for payment assertion results"""
    
    def __init__(self):
        self.passed = True
        self.passed_assertions = []
        self.failed_assertions = []
        self.details = {}
    
    def add_pass(self, message: str, actual_value: Any = None, expected_value: Any = None):
        """Add a passed assertion"""
        self.passed_assertions.append(message)
        if actual_value is not None:
            self.details[message] = {'expected': expected_value, 'actual': actual_value, 'status': 'PASS'}
    
    def add_fail(self, message: str, actual_value: Any = None, expected_value: Any = None):
        """Add a failed assertion"""
        self.passed = False
        self.failed_assertions.append(message)
        if actual_value is not None:
            self.details[message] = {'expected': expected_value, 'actual': actual_value, 'status': 'FAIL'}
    
    @property
    def message(self) -> str:
        """Get summary message"""
        if self.passed:
            return f"All assertions passed: {', '.join(self.passed_assertions)}" if self.passed_assertions else "No assertions to check"
        else:
            failed_msg = f"Failed: {', '.join(self.failed_assertions)}"
            if self.passed_assertions:
                failed_msg += f" | Passed: {', '.join(self.passed_assertions)}"
            return failed_msg

class PaymentAssertionEngine:
    """Engine for payment-specific assertions"""
    
    def __init__(self):
        self.logger = get_main_logger()
    
    def evaluate_payment_assertions(self, row: pd.Series, response: Any, 
                                   http_status: int, call_type: str) -> PaymentAssertionResult:
        """Evaluate payment assertions based on test row expectations"""
        
        result = PaymentAssertionResult()
        
        try:
            # 1. HTTP Status Code
            self._assert_http_status(row, http_status, result)
            
            # 2. Response Code (if provided)
            self._assert_response_code(row, response, result)
            
            # 3. Total Authorization Amount (if provided)
            self._assert_total_auth_amount(row, response, result)
            
            # 4. Card Security Result (if provided)
            self._assert_card_security_result(row, response, result)
            
            # 5. Address Verification Result (if provided)
            self._assert_avs_result(row, response, result)
            
            # 6. Merchant Advice Code (if provided)
            self._assert_merchant_advice_code(row, response, result)
            
        except Exception as e:
            self.logger.error(f"Assertion evaluation failed: {e}")
            result.add_fail(f"Assertion evaluation error: {e}")
        
        return result
    
    def _assert_http_status(self, row: pd.Series, http_status: int, result: PaymentAssertionResult):
        """Assert HTTP status code"""
        expected_http = row.get('expected_http_status')
        
        if pd.notna(expected_http) and expected_http != '':
            expected_http = int(expected_http)
            if http_status == expected_http:
                result.add_pass(f"HTTP status: {http_status}", http_status, expected_http)
            else:
                result.add_fail(f"HTTP status: expected {expected_http}, got {http_status}", 
                               http_status, expected_http)
    
    def _assert_response_code(self, row: pd.Series, response: Any, result: PaymentAssertionResult):
        """Assert responseCode field"""
        expected_code = row.get('expected_response_code')
        
        if pd.notna(expected_code) and expected_code != '':
            expected_code = str(expected_code).strip()  # ✅ Keep as string, no float conversion
            actual_code = self._extract_response_code(response)
            
            if actual_code is not None:
                actual_code_str = str(actual_code).strip()
                if actual_code_str == expected_code:
                    result.add_pass(f"responseCode: {actual_code_str}", actual_code_str, expected_code)
                else:
                    result.add_fail(f"responseCode: expected '{expected_code}', got '{actual_code_str}'", 
                                actual_code_str, expected_code)
            else:
                result.add_fail(f"responseCode: expected '{expected_code}', but not found in response", 
                            None, expected_code)
    
    def _assert_total_auth_amount(self, row: pd.Series, response: Any, result: PaymentAssertionResult):
        """Assert totalAuthorizationAmount.amount"""
        expected_amount = row.get('expected_total_auth_amount')
        
        if pd.notna(expected_amount) and expected_amount != '':
            expected_amount = float(expected_amount)
            actual_amount = self._extract_total_auth_amount(response)
            
            if actual_amount is not None:
                if abs(actual_amount - expected_amount) < 0.01:  # Allow for minor floating point differences
                    result.add_pass(f"totalAuthorizationAmount: {actual_amount}", actual_amount, expected_amount)
                else:
                    result.add_fail(f"totalAuthorizationAmount: expected {expected_amount}, got {actual_amount}", 
                                   actual_amount, expected_amount)
            else:
                result.add_fail(f"totalAuthorizationAmount: expected {expected_amount}, but not found in response", 
                               None, expected_amount)
    
    def _assert_card_security_result(self, row: pd.Series, response: Any, result: PaymentAssertionResult):
        """Assert cardPaymentData.ecommerceData.cardSecurityResult"""
        expected_result = row.get('expected_card_security_result')
        
        if pd.notna(expected_result) and expected_result != '':
            expected_result = str(expected_result)
            actual_result = self._extract_card_security_result(response)
            
            if actual_result is not None:
                if str(actual_result) == expected_result:
                    result.add_pass(f"cardSecurityResult: {actual_result}", actual_result, expected_result)
                else:
                    result.add_fail(f"cardSecurityResult: expected {expected_result}, got {actual_result}", 
                                   actual_result, expected_result)
            else:
                result.add_fail(f"cardSecurityResult: expected {expected_result}, but not found in response", 
                               None, expected_result)
    
    def _assert_avs_result(self, row: pd.Series, response: Any, result: PaymentAssertionResult):
        """Assert cardPaymentData.ecommerceData.addressVerificationResult"""
        expected_result = row.get('expected_avs_result')
        
        if pd.notna(expected_result) and expected_result != '':
            expected_result = str(expected_result)
            actual_result = self._extract_avs_result(response)
            
            if actual_result is not None:
                if str(actual_result) == expected_result:
                    result.add_pass(f"addressVerificationResult: {actual_result}", actual_result, expected_result)
                else:
                    result.add_fail(f"addressVerificationResult: expected {expected_result}, got {actual_result}", 
                                   actual_result, expected_result)
            else:
                result.add_fail(f"addressVerificationResult: expected {expected_result}, but not found in response", 
                               None, expected_result)
    
    def _assert_merchant_advice_code(self, row: pd.Series, response: Any, result: PaymentAssertionResult):
        """Assert additionalResponseData.merchantAdviceCode"""
        expected_code = row.get('expected_merchant_advice_code')
        
        if pd.notna(expected_code) and expected_code != '':
            expected_code = str(expected_code)
            actual_code = self._extract_merchant_advice_code(response)
            
            if actual_code is not None:
                if str(actual_code) == expected_code:
                    result.add_pass(f"merchantAdviceCode: {actual_code}", actual_code, expected_code)
                else:
                    result.add_fail(f"merchantAdviceCode: expected {expected_code}, got {actual_code}", 
                                   actual_code, expected_code)
            else:
                result.add_fail(f"merchantAdviceCode: expected {expected_code}, but not found in response", 
                               None, expected_code)
    
    # Extraction methods for the 6 specific properties
    
    def _extract_response_code(self, response: Any) -> Optional[str]:
        """Extract responseCode from response"""
        try:
            if hasattr(response, 'to_dictionary'):
                resp_dict = response.to_dictionary()
                return resp_dict.get('responseCode')
            return None
        except Exception as e:
            self.logger.warning(f"Failed to extract responseCode: {e}")
            return None
    
    def _extract_total_auth_amount(self, response: Any) -> Optional[str]:
        """Extract amount from response (totalAuthorizationAmount doesn't exist)"""
        try:
            if hasattr(response, 'to_dictionary'):
                resp_dict = response.to_dictionary()
                
                # Look for amount in the original request amount field since totalAuthorizationAmount doesn't exist
                # For create_payment, the amount is in the request, not response
                # This field might not be meaningful for assertions - consider removing
                return None  # ✅ This field doesn't exist in API responses
            
            return None
        except Exception as e:
            self.logger.warning(f"Failed to extract totalAuthorizationAmount: {e}")
            return None

    
    def _extract_card_security_result(self, response: Any) -> Optional[str]:
        """Extract cardPaymentData.ecommerceData.cardSecurityCodeResult from response"""
        try:
            if hasattr(response, 'to_dictionary'):
                resp_dict = response.to_dictionary()
                
                # Navigate: cardPaymentData -> ecommerceData -> cardSecurityCodeResult (NOT cardSecurityResult)
                card_payment = resp_dict.get('cardPaymentData')
                if card_payment and 'ecommerceData' in card_payment:
                    ecommerce_data = card_payment['ecommerceData']
                    return ecommerce_data.get('cardSecurityCodeResult')  # ✅ Fixed field name
            
            return None
        except Exception as e:
            self.logger.warning(f"Failed to extract cardSecurityCodeResult: {e}")
            return None
    
    def _extract_avs_result(self, response: Any) -> Optional[str]:
        """Extract cardPaymentData.ecommerceData.addressVerificationResult from response"""
        try:
            if hasattr(response, 'to_dictionary'):
                resp_dict = response.to_dictionary()
                
                # Navigate: cardPaymentData -> ecommerceData -> addressVerificationResult
                card_payment = resp_dict.get('cardPaymentData')
                if card_payment and 'ecommerceData' in card_payment:
                    ecommerce_data = card_payment['ecommerceData']
                    return ecommerce_data.get('addressVerificationResult')
            
            return None
        except Exception as e:
            self.logger.warning(f"Failed to extract addressVerificationResult: {e}")
            return None
    
    def _extract_merchant_advice_code(self, response: Any) -> Optional[str]:
        """Extract additionalResponseData.merchantAdviceCode from response"""
        try:
            if hasattr(response, 'to_dictionary'):
                resp_dict = response.to_dictionary()
                
                # Navigate: additionalResponseData -> merchantAdviceCode
                additional_data = resp_dict.get('additionalResponseData')
                if additional_data:
                    return additional_data.get('merchantAdviceCode')
            
            return None
        except Exception as e:
            self.logger.warning(f"Failed to extract merchantAdviceCode: {e}")
            return None