import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class VerifyInfo:
    type: str
    detected: bool
    element: Optional[object] = None


@dataclass
class HandleResult:
    success: bool
    need_manual: bool = False
    message: str = ""


class SecurityHandler:
    VERIFY_PATTERNS = {
        'slider': ['滑块验证', '拖动滑块', 'slider', '滑动验证'],
        'click': ['点击验证', '请点击', 'click to verify', '点击继续'],
        'image': ['图片验证', '选择包含', 'select images', '图片选择'],
        'captcha': ['验证码', 'captcha', '输入验证码', '图形验证码'],
    }
    
    def __init__(self, auto_wait_time: int = 5):
        self.auto_wait_time = auto_wait_time
    
    def detect_verification(self, driver) -> Optional[VerifyInfo]:
        try:
            page_content = driver.execute_script('''
                return {
                    text: document.body.innerText.toLowerCase(),
                    html: document.body.innerHTML.toLowerCase(),
                    title: document.title.toLowerCase()
                };
            ''')
            
            if not page_content:
                return None
            
            combined_text = f"{page_content.get('text', '')} {page_content.get('html', '')} {page_content.get('title', '')}"
            
            for verify_type, patterns in self.VERIFY_PATTERNS.items():
                for pattern in patterns:
                    if pattern.lower() in combined_text:
                        return VerifyInfo(type=verify_type, detected=True)
            
            return None
            
        except Exception as e:
            print(f"[SecurityHandler] Detection error: {e}")
            return None
    
    def handle_verification(self, driver, verify_info: VerifyInfo) -> HandleResult:
        handlers = {
            'slider': self._handle_slider,
            'click': self._handle_click_verify,
            'image': self._handle_image_verify,
            'captcha': self._handle_captcha,
        }
        
        handler = handlers.get(verify_info.type, self._handle_unknown)
        return handler(driver)
    
    def _handle_slider(self, driver) -> HandleResult:
        try:
            slider = driver.execute_script('''
                const sliders = document.querySelectorAll('[class*="slider"], [class*="slide"], [id*="slider"]');
                return sliders.length > 0 ? sliders[0] : null;
            ''')
            
            if slider:
                time.sleep(self.auto_wait_time)
                return HandleResult(success=False, need_manual=True, message="滑块验证需要人工处理")
            
            return HandleResult(success=False, need_manual=True, message="未找到滑块元素")
            
        except Exception as e:
            return HandleResult(success=False, need_manual=True, message=f"滑块处理异常: {e}")
    
    def _handle_click_verify(self, driver) -> HandleResult:
        try:
            clicked = driver.execute_script('''
                const btns = document.querySelectorAll('button, [class*="verify"], [class*="confirm"]');
                for (const btn of btns) {
                    if (btn.innerText.includes('验证') || btn.innerText.includes('确认') || btn.innerText.includes('继续')) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            ''')
            
            if clicked:
                time.sleep(1)
                return HandleResult(success=True, message="已自动点击验证按钮")
            
            return HandleResult(success=False, need_manual=True, message="未找到可点击的验证按钮")
            
        except Exception as e:
            return HandleResult(success=False, need_manual=True, message=f"点击验证异常: {e}")
    
    def _handle_image_verify(self, driver) -> HandleResult:
        return HandleResult(success=False, need_manual=True, message="图片验证需要人工处理")
    
    def _handle_captcha(self, driver) -> HandleResult:
        return HandleResult(success=False, need_manual=True, message="验证码需要人工处理")
    
    def _handle_unknown(self, driver) -> HandleResult:
        return HandleResult(success=False, need_manual=True, message="未知验证类型，需要人工处理")
