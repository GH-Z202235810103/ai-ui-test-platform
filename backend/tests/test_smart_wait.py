import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from core.smart_wait import SmartWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class TestSmartWait:
    def setup_method(self):
        self.driver = MagicMock()
        self.wait = SmartWait(self.driver, default_timeout=5)
    
    def test_wait_for_element_success(self):
        mock_element = MagicMock()
        
        with patch('core.smart_wait.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = mock_element
            result = self.wait.wait_for_element([(By.ID, 'test')])
        
        assert result == mock_element
    
    def test_wait_for_element_fallback(self):
        mock_element = MagicMock()
        call_count = [0]
        
        def mock_until(condition):
            call_count[0] += 1
            if call_count[0] < 2:
                raise TimeoutException()
            return mock_element
        
        with patch('core.smart_wait.WebDriverWait') as mock_wait:
            mock_wait.return_value.until = mock_until
            result = self.wait.wait_for_element([(By.ID, 'first'), (By.ID, 'second')])
        
        assert result == mock_element
    
    def test_wait_for_element_all_fail(self):
        with patch('core.smart_wait.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.side_effect = TimeoutException()
            
            with pytest.raises(TimeoutException):
                self.wait.wait_for_element([(By.ID, 'test')])
    
    def test_wait_for_page_stable(self):
        self.driver.execute_script.return_value = '100_complete'
        
        result = self.wait.wait_for_page_stable(timeout=2)
        
        assert result is True
    
    def test_wait_for_ajax_complete(self):
        self.driver.execute_script.return_value = True
        
        result = self.wait.wait_for_ajax_complete(timeout=5)
        
        assert result is True
    
    def test_wait_for_clickable(self):
        mock_element = MagicMock()
        
        with patch('core.smart_wait.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = mock_element
            result = self.wait.wait_for_clickable((By.ID, 'button'))
        
        assert result == mock_element
