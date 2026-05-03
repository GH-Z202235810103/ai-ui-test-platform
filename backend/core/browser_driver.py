"""
浏览器驱动抽象层 - 统一Selenium和Playwright的API差异
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from pathlib import Path


class BrowserDriver(ABC):
    """浏览器驱动抽象基类"""
    
    @abstractmethod
    def get(self, url: str) -> None:
        """访问URL"""
        pass
    
    @abstractmethod
    def click(self, selector: str) -> None:
        """点击元素"""
        pass
    
    @abstractmethod
    def send_keys(self, selector: str, text: str) -> None:
        """输入文本"""
        pass
    
    @abstractmethod
    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        pass
    
    @abstractmethod
    def take_screenshot(self, path: str) -> None:
        """截图"""
        pass
    
    @abstractmethod
    def execute_script(self, script: str, *args) -> any:
        """执行JavaScript"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """关闭浏览器"""
        pass
    
    @property
    @abstractmethod
    def current_url(self) -> str:
        """当前URL"""
        pass


class SeleniumDriver(BrowserDriver):
    """Selenium浏览器驱动实现"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def get(self, url: str) -> None:
        """访问URL"""
        self.driver.get(url)
    
    def click(self, selector: str) -> None:
        """点击元素"""
        from selenium.webdriver.common.by import By
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
    
    def send_keys(self, selector: str, text: str) -> None:
        """输入文本"""
        from selenium.webdriver.common.by import By
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        from selenium.webdriver.common.by import By
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        return element.text
    
    def take_screenshot(self, path: str) -> None:
        """截图"""
        self.driver.save_screenshot(path)
    
    def execute_script(self, script: str, *args) -> any:
        """执行JavaScript"""
        return self.driver.execute_script(script, *args)
    
    def close(self) -> None:
        """关闭浏览器"""
        self.driver.quit()
    
    @property
    def current_url(self) -> str:
        """当前URL"""
        return self.driver.current_url


class PlaywrightDriver(BrowserDriver):
    """Playwright浏览器驱动实现"""
    
    def __init__(self, page):
        self.page = page
    
    def get(self, url: str) -> None:
        """访问URL"""
        import asyncio
        asyncio.run(self.page.goto(url, wait_until="networkidle"))
    
    def click(self, selector: str) -> None:
        """点击元素"""
        import asyncio
        asyncio.run(self.page.click(selector))
    
    def send_keys(self, selector: str, text: str) -> None:
        """输入文本"""
        import asyncio
        asyncio.run(self.page.fill(selector, text))
    
    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        import asyncio
        return asyncio.run(self.page.inner_text(selector))
    
    def take_screenshot(self, path: str) -> None:
        """截图"""
        import asyncio
        asyncio.run(self.page.screenshot(path=path))
    
    def execute_script(self, script: str, *args) -> any:
        """执行JavaScript"""
        import asyncio
        return asyncio.run(self.page.evaluate(script, *args))
    
    def close(self) -> None:
        """关闭浏览器"""
        import asyncio
        asyncio.run(self.page.close())
    
    @property
    def current_url(self) -> str:
        """当前URL"""
        import asyncio
        return asyncio.run(self.page.url)


class BrowserDriverFactory:
    """浏览器驱动工厂"""
    
    @staticmethod
    def create_driver(driver_type: str, **kwargs) -> BrowserDriver:
        """创建浏览器驱动
        
        Args:
            driver_type: 驱动类型 ('selenium' 或 'playwright')
            **kwargs: 驱动参数
        
        Returns:
            BrowserDriver实例
        """
        if driver_type == 'selenium':
            driver = kwargs.get('driver')
            if not driver:
                raise ValueError("Selenium driver is required")
            return SeleniumDriver(driver)
        elif driver_type == 'playwright':
            page = kwargs.get('page')
            if not page:
                raise ValueError("Playwright page is required")
            return PlaywrightDriver(page)
        else:
            raise ValueError(f"Unsupported driver type: {driver_type}")
