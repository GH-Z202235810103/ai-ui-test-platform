import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock
from core.security_handler import SecurityHandler, VerifyInfo, HandleResult


class TestSecurityHandler:
    def setup_method(self):
        self.handler = SecurityHandler()
        self.driver = MagicMock()
    
    def test_detect_slider_verification(self):
        self.driver.execute_script.return_value = {
            'text': '页面包含滑块验证请完成',
            'html': '',
            'title': ''
        }
        
        result = self.handler.detect_verification(self.driver)
        
        assert result is not None
        assert result.type == 'slider'
    
    def test_detect_click_verification(self):
        self.driver.execute_script.return_value = {
            'text': '请点击验证按钮',
            'html': '',
            'title': ''
        }
        
        result = self.handler.detect_verification(self.driver)
        
        assert result is not None
        assert result.type == 'click'
    
    def test_detect_captcha_verification(self):
        self.driver.execute_script.return_value = {
            'text': '请输入验证码',
            'html': '',
            'title': ''
        }
        
        result = self.handler.detect_verification(self.driver)
        
        assert result is not None
        assert result.type == 'captcha'
    
    def test_no_verification_detected(self):
        self.driver.execute_script.return_value = {
            'text': '正常页面内容',
            'html': '',
            'title': ''
        }
        
        result = self.handler.detect_verification(self.driver)
        
        assert result is None
    
    def test_handle_slider_verification(self):
        verify_info = VerifyInfo(type='slider', detected=True)
        
        result = self.handler.handle_verification(self.driver, verify_info)
        
        assert result.success is True or result.need_manual is True
    
    def test_handle_captcha_needs_manual(self):
        verify_info = VerifyInfo(type='captcha', detected=True)
        
        result = self.handler.handle_verification(self.driver, verify_info)
        
        assert result.need_manual is True
    
    def test_handle_unknown_verification(self):
        verify_info = VerifyInfo(type='unknown', detected=True)
        
        result = self.handler.handle_verification(self.driver, verify_info)
        
        assert result.need_manual is True
