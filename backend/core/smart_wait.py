import time
from typing import List, Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SmartWait:
    def __init__(self, driver, default_timeout: int = 10):
        self.driver = driver
        self.default_timeout = default_timeout
    
    def wait_for_element(self, locators: List[Tuple[str, str]], timeout: Optional[int] = None):
        timeout = timeout or self.default_timeout
        last_error = None
        
        for locator in locators:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                return element
            except TimeoutException as e:
                last_error = e
                continue
        
        raise last_error or TimeoutException(f"Element not found with any locator: {locators}")
    
    def wait_for_clickable(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        timeout = timeout or self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    
    def wait_for_visible(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        timeout = timeout or self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    
    def wait_for_page_stable(self, timeout: int = 5) -> bool:
        start_time = time.time()
        last_hash = None
        
        while time.time() - start_time < timeout:
            try:
                current_hash = self.driver.execute_script('''
                    return document.body.innerHTML.length + '_' + document.readyState;
                ''')
                
                if current_hash == last_hash:
                    return True
                last_hash = current_hash
                time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        
        return False
    
    def wait_for_ajax_complete(self, timeout: int = 10) -> bool:
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                ajax_complete = self.driver.execute_script('''
                    return typeof jQuery !== 'undefined' ? jQuery.active === 0 : true;
                ''')
                
                if ajax_complete:
                    return True
                time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        
        return False
    
    def wait_for_url_contains(self, text: str, timeout: Optional[int] = None) -> bool:
        timeout = timeout or self.default_timeout
        WebDriverWait(self.driver, timeout).until(
            EC.url_contains(text)
        )
        return True
    
    def wait_for_title_contains(self, text: str, timeout: Optional[int] = None) -> bool:
        timeout = timeout or self.default_timeout
        WebDriverWait(self.driver, timeout).until(
            EC.title_contains(text)
        )
        return True
