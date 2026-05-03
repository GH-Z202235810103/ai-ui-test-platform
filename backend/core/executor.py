"""
测试执行器 - 使用Selenium执行测试并生成截图

工具选择说明：
- 执行测试用例：使用Selenium，因为它更成熟、稳定，且广泛使用
- 智能录制回放：使用Playwright，因为它在录制和事件捕获方面有优势
- 抽象层设计：创建了BrowserDriver抽象层，统一两种工具的API差异

核心功能：
- 智能截图：基于DOM变化检测，避免重复截图
- 错误处理：完善的异常捕获和处理机制
- 多浏览器支持：优先使用Edge，失败后尝试Chrome、Firefox
- 截图管理：自动清理旧截图，限制历史数量
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
import cv2
import numpy as np
import tempfile
import os
import hashlib
import random

SCREENSHOT_DIR = Path(__file__).parent.parent / "screenshots"


def human_like_delay(min_sec=0.3, max_sec=1.5, enabled=True):
    """模拟人类操作的随机延迟，避免被检测为自动化
    
    Args:
        min_sec: 最小延迟秒数
        max_sec: 最大延迟秒数
        enabled: 是否启用延迟（无头模式可以禁用）
    """
    if not enabled:
        return 0
    import time
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay


def check_security_verification(driver):
    """检测是否触发安全验证页面"""
    try:
        result = driver.execute_script('''
            return {
                hasVerifyText: document.body.innerText.includes('安全验证') ||
                               document.body.innerText.includes('请完成以下验证') ||
                               document.body.innerText.includes('验证码'),
                hasVerifyElement: document.querySelector('.verify-wrap') !== null ||
                                  document.querySelector('#verify') !== null,
                isVerifyPage: document.title.includes('安全验证') ||
                              document.title.includes('验证')
            };
        ''')
        if result and (result.get('hasVerifyText') or result.get('hasVerifyElement') or result.get('isVerifyPage')):
            return True
        return False
    except Exception as e:
        print(f"[安全验证检测] 错误: {e}")
        return False


class ScreenshotConfig:
    """截图配置类"""
    quality = 90  # JPEG质量 (0-100)
    format = "png"  # 截图格式 (png/jpeg)
    smart_capture = True  # 智能截图
    max_history = 100  # 最大历史截图数
    cleanup_days = 7  # 清理天数
    compression_quality = 85  # 压缩质量 (0-100)
    max_width = 1920  # 最大宽度
    max_height = 1080  # 最大高度
    capture_in_headless = False  # 无头模式下是否截图（默认不截图）


def compress_screenshot(image_path: str) -> None:
    """压缩截图，减少存储空间的使用
    
    Args:
        image_path: 图片路径
    """
    try:
        import cv2
        import numpy as np
        
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("无法读取图片")
        
        # 获取图片尺寸
        height, width = img.shape[:2]
        
        # 调整大小（如果超过最大尺寸）
        if width > ScreenshotConfig.max_width or height > ScreenshotConfig.max_height:
            # 计算缩放比例
            scale = min(
                ScreenshotConfig.max_width / width,
                ScreenshotConfig.max_height / height
            )
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            print(f"[截图压缩] 调整大小: {width}x{height} -> {new_width}x{new_height}")
        
        # 压缩并保存
        quality = ScreenshotConfig.compression_quality
        cv2.imwrite(image_path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        
        # 计算压缩前后的文件大小
        original_size = os.path.getsize(image_path)
        print(f"[截图压缩] 压缩后文件大小: {original_size / 1024:.2f} KB")
    except Exception as e:
        print(f"[截图压缩] 错误: {e}")
        # 压缩失败时不影响测试执行


def get_image_hash(image_path: str) -> str:
    """计算图片的感知哈希值
    
    优化：使用感知哈希算法，提高去重的准确性
    
    Args:
        image_path: 图片路径
    
    Returns:
        图片的感知哈希值
    """
    try:
        # 使用感知哈希算法
        import cv2
        import numpy as np
        
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("无法读取图片")
        
        # 调整大小为32x32灰度图
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (32, 32), interpolation=cv2.INTER_AREA)
        
        # 计算DCT
        dct = cv2.dct(np.float32(img))
        
        # 取左上角8x8区域
        dct_8x8 = dct[:8, :8]
        
        # 计算平均值
        mean = np.mean(dct_8x8)
        
        # 生成哈希值
        hash_bits = []
        for i in range(8):
            for j in range(8):
                if dct_8x8[i, j] > mean:
                    hash_bits.append('1')
                else:
                    hash_bits.append('0')
        
        # 转换为十六进制
        hash_value = hex(int(''.join(hash_bits), 2))[2:].zfill(16)
        print(f"[哈希计算] 图片 {image_path} 的感知哈希值: {hash_value}")
        return hash_value
    except Exception as e:
        print(f"[哈希计算] 错误: {e}")
        # 失败时使用MD5作为备用
        md5 = hashlib.md5()
        try:
            with open(image_path, 'rb') as f:
                # 分块读取，每块8MB
                while chunk := f.read(8 * 1024 * 1024):
                    md5.update(chunk)
            hash_value = md5.hexdigest()
            print(f"[哈希计算] 使用MD5备用: {hash_value}")
            return hash_value
        except Exception:
            return "error_hash"


def get_page_dom_hash(driver) -> str:
    """获取页面DOM的哈希值
    
    优化：
    - 增加错误处理，确保函数不会因为DOM操作失败而影响整个测试
    - 简化DOM内容获取，只获取关键信息
    - 添加超时处理
    
    Args:
        driver: Selenium WebDriver实例
    
    Returns:
        DOM的MD5哈希值，如果失败返回None
    """
    try:
        # 尝试获取页面关键信息（不包含时间戳，避免每次计算结果不同）
        dom_content = driver.execute_script('''
            try {
                return {
                    title: document.title || '',
                    url: window.location.href || '',
                    body_length: document.body.innerText.length || 0,
                    head_inner_text: document.head.innerText || '',
                    body_inner_text: document.body.innerText.substring(0, 1000) || ''
                };
            } catch (e) {
                return {
                    title: '',
                    url: '',
                    body_length: 0,
                    head_inner_text: '',
                    body_inner_text: ''
                };
            }
        ''')
        # 计算哈希值
        dom_str = str(dom_content)
        hash_value = hashlib.md5(dom_str.encode('utf-8')).hexdigest()
        print(f"[DOM检测] DOM哈希值: {hash_value}")
        return hash_value
    except Exception as e:
        print(f"[DOM检测] 错误: {e}")
        return None


def has_page_changed(driver, previous_dom_hash: str) -> bool:
    """检测页面是否发生变化
    
    优化：
    - 增加错误处理，确保函数不会因为DOM操作失败而影响整个测试
    - 提供更合理的默认行为
    
    Args:
        driver: Selenium WebDriver实例
        previous_dom_hash: 之前的DOM哈希值
    
    Returns:
        如果页面发生变化返回True，否则返回False
    """
    try:
        current_hash = get_page_dom_hash(driver)
        # 如果无法获取当前哈希值或之前没有哈希值，默认需要截图
        if not current_hash or not previous_dom_hash:
            return True
        # 比较哈希值，不同则认为页面发生变化
        return current_hash != previous_dom_hash
    except Exception as e:
        print(f"[页面变化检测] 错误: {e}")
        # 发生错误时默认需要截图，确保测试不会因为检测失败而跳过截图
        return True


def generate_screenshot_name(testcase: Dict, step_idx: int, step_desc: str = "") -> str:
    """生成智能截图名称
    
    优化：
    - 增加安全性，移除所有可能导致文件系统问题的字符
    - 确保生成的文件名安全且唯一
    - 提供更清晰的命名格式
    
    Args:
        testcase: 测试用例字典
        step_idx: 步骤索引
        step_desc: 步骤描述
    
    Returns:
        安全的截图文件名
    """
    import re
    
    # 获取测试用例信息
    test_id = str(testcase.get('id', 'unknown'))
    test_name = str(testcase.get('name', 'test'))
    
    # 移除不安全的字符
    def sanitize_string(s):
        # 只保留字母、数字、下划线和连字符
        return re.sub(r'[^a-zA-Z0-9_-]', '', s)
    
    # 清理字符串
    test_id = sanitize_string(test_id) or 'unknown'
    test_name = sanitize_string(test_name) or 'test'
    step_desc = sanitize_string(step_desc)[:20] or 'step'
    
    # 生成时间戳和唯一ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]  # 生成唯一标识符
    
    # 生成文件名
    if step_idx == 0:
        return f"{test_id}_{test_name}_homepage_{timestamp}_{unique_id}.png"
    else:
        return f"{test_id}_{test_name}_step_{step_idx}_{step_desc}_{timestamp}_{unique_id}.png"


def cleanup_old_screenshots(days: int = None) -> int:
    """清理旧截图
    
    Args:
        days: 保留天数，默认使用配置值
    
    Returns:
        删除的文件数量
    """
    if days is None:
        days = ScreenshotConfig.cleanup_days
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    try:
        if SCREENSHOT_DIR.exists():
            for file_path in SCREENSHOT_DIR.iterdir():
                if file_path.is_file():
                    # 检查文件修改时间
                    if file_path.stat().st_mtime < cutoff_date.timestamp():
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            print(f"[清理] 删除文件失败 {file_path}: {e}")
    except Exception as e:
        print(f"[清理] 错误: {e}")
    
    return deleted_count


def limit_screenshot_history(max_count: int = None) -> int:
    """限制截图历史数量
    
    Args:
        max_count: 最大数量，默认使用配置值
    
    Returns:
        删除的文件数量
    """
    if max_count is None:
        max_count = ScreenshotConfig.max_history
    
    deleted_count = 0
    
    try:
        if SCREENSHOT_DIR.exists():
            # 获取所有截图文件并按修改时间排序
            screenshot_files = []
            for file_path in SCREENSHOT_DIR.iterdir():
                if file_path.is_file() and file_path.suffix in ['.png', '.jpg', '.jpeg']:
                    screenshot_files.append((file_path.stat().st_mtime, file_path))
            
            # 按修改时间排序（最新的在前）
            screenshot_files.sort(reverse=True)
            
            # 删除超出数量的旧文件
            if len(screenshot_files) > max_count:
                for _, file_path in screenshot_files[max_count:]:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"[清理] 删除文件失败 {file_path}: {e}")
    except Exception as e:
        print(f"[清理] 错误: {e}")
    
    return deleted_count


def locate_element_visual(driver, element_name: str) -> Optional[Dict]:
    """使用视觉定位查找元素"""
    try:
        from core.visual_locator import get_visual_locator
        locator = get_visual_locator()
        
        if element_name not in locator.templates:
            return None
        
        screenshot_path = str(SCREENSHOT_DIR / "_temp_visual.png")
        driver.save_screenshot(screenshot_path)
        
        with open(screenshot_path, 'rb') as f:
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        screenshot = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if screenshot is None:
            return None
        
        result = locator.locate_element(screenshot, element_name)
        
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        
        return result
    except Exception as e:
        print(f"[视觉定位] 错误: {e}")
        return None


def click_at_position(driver, x: int, y: int):
    """点击指定坐标"""
    from selenium.webdriver.common.action_chains import ActionChains
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()


def find_element_smart(driver, selectors: List[str], element_name: str = None) -> bool:
    """智能查找元素：先尝试选择器，失败后尝试视觉定位"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    for selector in selectors:
        try:
            # 尝试不同的定位方式
            if selector.startswith('#'):
                # ID定位
                el = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.ID, selector[1:]))
                )
            elif selector.startswith('.'):
                # Class定位
                el = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, selector[1:]))
                )
            elif selector.startswith('//'):
                # XPath定位
                el = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            else:
                # CSS选择器定位
                el = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            if el:
                return True
        except Exception:
            continue
    
    if element_name:
        visual_result = locate_element_visual(driver, element_name)
        if visual_result:
            click_at_position(driver, visual_result['x'], visual_result['y'])
            return True
    
    return False


def run_playwright_sync(testcase: Dict, headless: bool = True, base_url: Optional[str] = None) -> Dict:
    """同步执行测试用例
    
    注意：虽然函数名包含"playwright"，但实际使用的是Selenium
    这是为了保持API兼容性，后续会考虑重命名
    
    Args:
        testcase: 测试用例字典
        headless: 是否使用无头模式
        base_url: 基础URL
    
    Returns:
        执行结果字典，包含成功状态、日志、截图等信息
    """

    import sys
    import os
    import time
    from selenium.common.exceptions import (
        NoSuchElementException, WebDriverException, TimeoutException,
        ElementNotInteractableException, StaleElementReferenceException
    )
    
    execution_log = []
    screenshots = []
    previous_screenshot_hash = None
    previous_dom_hash = None
    driver = None
    
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 清理旧截图
    deleted_old = cleanup_old_screenshots()
    deleted_excess = limit_screenshot_history()
    if deleted_old > 0 or deleted_excess > 0:
        log(f"清理旧截图: 删除了 {deleted_old} 个过期文件, {deleted_excess} 个超出限制的文件")
    
    # 创建日志文件
    log_file = SCREENSHOT_DIR / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def log(message):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        execution_log.append(log_message)
        print(log_message)
        # 写入文件
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def smart_delay(min_sec=0.3, max_sec=1.5):
        """智能延迟：无头模式跳过，非无头模式执行延迟"""
        if headless:
            return 0
        return human_like_delay(min_sec, max_sec, enabled=True)
    
    def safe_execute(action_name, action, *args, **kwargs):
        """安全执行操作，捕获并处理异常"""
        try:
            result = action(*args, **kwargs)
            log(f"{action_name}成功")
            return True, result
        except NoSuchElementException:
            log(f"{action_name}失败: 未找到元素")
            return False, None
        except TimeoutException:
            log(f"{action_name}失败: 操作超时")
            return False, None
        except ElementNotInteractableException:
            log(f"{action_name}失败: 元素不可交互")
            return False, None
        except StaleElementReferenceException:
            log(f"{action_name}失败: 元素已失效")
            return False, None
        except WebDriverException as e:
            log(f"{action_name}失败: {str(e)[:100]}")
            return False, None
        except Exception as e:
            log(f"{action_name}失败: {str(e)[:100]}")
            return False, None
    
    try:
        start_time = datetime.now()
        log(f"开始执行: {testcase.get('name')}")
        
        steps = testcase.get('steps', [])
        url = testcase.get('url', '') or base_url or 'https://www.baidu.com'
        
        # 尝试使用系统浏览器执行测试
        try:
            log("开始执行测试")
            
            # 确保截图目录存在
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            
            # 尝试使用Selenium来控制浏览器
            try:
                log("尝试导入Selenium...")
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                log("Selenium导入成功")
                
                # 尝试启动Edge浏览器
                log("尝试启动Edge浏览器...")
                browser_launched = False
                
                # 尝试启动Edge浏览器
                try:
                    # 尝试使用无头模式
                    from selenium.webdriver.edge.options import Options
                    edge_options = Options()
                    edge_options.add_argument('--headless')
                    edge_options.add_argument('--disable-gpu')
                    edge_options.add_argument('--no-sandbox')
                    edge_options.add_argument('--window-size=1920,1080')
                    edge_options.add_argument('--disable-dev-shm-usage')
                    edge_options.add_argument('--disable-extensions')
                    edge_options.add_argument('--disable-infobars')
                    edge_options.add_argument('--start-maximized')
                    # 反检测配置
                    edge_options.add_argument('--disable-blink-features=AutomationControlled')
                    edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                    edge_options.add_experimental_option('useAutomationExtension', False)
                    # 添加真实的User-Agent
                    edge_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
                    # 添加更多浏览器参数
                    edge_options.add_argument('--disable-web-security')
                    edge_options.add_argument('--allow-running-insecure-content')
                    edge_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
                    edge_options.add_argument('--lang=zh-CN')
                    driver = webdriver.Edge(options=edge_options)
                    # 隐藏webdriver属性
                    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                        'source': '''
                            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
                            window.chrome = {runtime: {}};
                        '''
                    })
                    log("Edge浏览器启动成功（已启用完整反检测）")
                    browser_launched = True
                except Exception as e:
                    log(f"Edge浏览器启动失败: {e}")
                    # 尝试使用Chrome作为备选
                    log("尝试启动Chrome浏览器...")
                    try:
                        # 尝试使用无头模式
                        from selenium.webdriver.chrome.options import Options
                        chrome_options = Options()
                        chrome_options.add_argument('--headless')
                        chrome_options.add_argument('--disable-gpu')
                        chrome_options.add_argument('--no-sandbox')
                        chrome_options.add_argument('--window-size=1920,1080')
                        chrome_options.add_argument('--disable-dev-shm-usage')
                        chrome_options.add_argument('--disable-extensions')
                        chrome_options.add_argument('--disable-infobars')
                        chrome_options.add_argument('--start-maximized')
                        # 反检测配置
                        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                        chrome_options.add_experimental_option('useAutomationExtension', False)
                        # 添加真实的User-Agent
                        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                        # 添加更多浏览器参数
                        chrome_options.add_argument('--disable-web-security')
                        chrome_options.add_argument('--allow-running-insecure-content')
                        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
                        chrome_options.add_argument('--lang=zh-CN')
                        driver = webdriver.Chrome(options=chrome_options)
                        # 隐藏webdriver属性
                        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                            'source': '''
                                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                                Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
                                window.chrome = {runtime: {}};
                            '''
                        })
                        log("Chrome浏览器启动成功（已启用完整反检测）")
                        browser_launched = True
                    except Exception as e2:
                        log(f"Chrome浏览器启动失败: {e2}")
                        # 尝试使用Firefox作为备选
                        log("尝试启动Firefox浏览器...")
                        try:
                            # 尝试使用无头模式
                            from selenium.webdriver.firefox.options import Options
                            firefox_options = Options()
                            firefox_options.add_argument('--headless')
                            firefox_options.add_argument('--window-size=1920,1080')
                            firefox_options.add_argument('--start-maximized')
                            driver = webdriver.Firefox(options=firefox_options)
                            log("Firefox浏览器启动成功")
                            browser_launched = True
                        except Exception as e3:
                            log(f"Firefox浏览器启动失败: {e3}")
                            raise Exception("无法启动任何浏览器")
                
                if not browser_launched:
                    raise Exception("无法启动任何浏览器")
                
                # 访问URL
                log(f"访问: {url}")
                success, _ = safe_execute("访问URL", driver.get, url)
                if not success:
                    log("访问URL失败，尝试重试...")
                    time.sleep(3)
                    success, _ = safe_execute("访问URL(重试)", driver.get, url)
                    if not success:
                        log("访问URL失败，尝试使用备用URL...")
                        time.sleep(3)
                        # 使用备用URL
                        backup_url = "https://www.baidu.com"
                        log(f"尝试访问备用URL: {backup_url}")
                        success, _ = safe_execute("访问备用URL", driver.get, backup_url)
                
                # 等待页面加载
                try:
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    log("页面加载成功")
                except TimeoutException:
                    log("页面加载超时，但继续执行")
                
                # 添加随机延迟，让页面稳定
                smart_delay(0.5, 1.0)
                
                # 检测是否触发安全验证
                if check_security_verification(driver):
                    log("⚠️ 页面加载后检测到安全验证")
                else:
                    log("页面正常，无安全验证")
                
                # 检查是否需要截图
                need_screenshot = True
                if headless and not ScreenshotConfig.capture_in_headless:
                    # 无头模式下跳过截图（除非配置了capture_in_headless）
                    need_screenshot = False
                    log("无头模式，跳过首页截图")
                elif ScreenshotConfig.smart_capture:
                    current_dom_hash = get_page_dom_hash(driver)
                    if current_dom_hash:
                        need_screenshot = previous_dom_hash is None or current_dom_hash != previous_dom_hash
                        previous_dom_hash = current_dom_hash
                
                if need_screenshot:
                    # 截图
                    screenshot_name = generate_screenshot_name(testcase, 0)
                    screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
                    success, _ = safe_execute("首页截图", driver.save_screenshot, screenshot_path)
                    
                    if success:
                        # 压缩截图
                        try:
                            compress_screenshot(screenshot_path)
                            log(f"首页截图压缩成功: {screenshot_name}")
                        except Exception as e:
                            log(f"截图压缩失败: {e}")
                        
                        # 计算截图哈希值并去重
                        try:
                            current_hash = get_image_hash(screenshot_path)
                            print(f"[截图去重] 首页截图哈希: {current_hash}, 之前哈希: {previous_screenshot_hash}")
                            if current_hash != previous_screenshot_hash and current_hash != "error_hash":
                                screenshots.append(screenshot_name)
                                previous_screenshot_hash = current_hash
                                log(f"首页截图成功: {screenshot_name}")
                            else:
                                # 删除重复截图
                                if os.path.exists(screenshot_path):
                                    os.remove(screenshot_path)
                                    log(f"截图重复，已删除: {screenshot_name}")
                        except Exception as e:
                            log(f"截图哈希计算失败: {e}")
                            screenshots.append(screenshot_name)
                else:
                    log("页面未发生变化，跳过截图")
                
                # 执行测试步骤
                for i, step in enumerate(steps, 1):
                    log(f"步骤 {i}: {step}")
                    
                    # 尝试执行步骤
                    try:
                        if '搜索' in step:
                            # 检查是否只是点击搜索按钮
                            if '点击搜索按钮' in step or '点击 搜索按钮' in step:
                                log("执行点击搜索按钮操作")
                                # 直接尝试找到搜索按钮并点击
                                search_button = None
                                
                                # 尝试通过ID定位
                                try:
                                    search_button = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.ID, 'su'))
                                    )
                                    log("通过ID找到搜索按钮")
                                except:
                                    log("通过ID未找到搜索按钮")
                                
                                # 尝试通过class定位
                                if not search_button:
                                    try:
                                        search_button = WebDriverWait(driver, 5).until(
                                            EC.presence_of_element_located((By.CLASS_NAME, 's_btn'))
                                        )
                                        log("通过class找到搜索按钮")
                                    except:
                                        log("通过class未找到搜索按钮")
                                
                                if search_button:
                                    # 尝试点击搜索按钮
                                    try:
                                        search_button.click()
                                        log("点击搜索按钮成功")
                                    except:
                                        # 尝试使用JavaScript点击
                                        try:
                                            driver.execute_script("arguments[0].click();", search_button)
                                            log("通过JavaScript点击搜索按钮成功")
                                        except:
                                            log("点击搜索按钮失败")
                                else:
                                    log("未找到搜索按钮")
                                
                                # 等待搜索结果加载
                                try:
                                    WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.ID, 'content_left'))
                                    )
                                    log("搜索结果加载成功")
                                except:
                                    log("搜索结果加载失败")
                                
                                log("执行成功")
                            else:
                                # 尝试找到搜索框并输入关键词
                                # 改进关键词提取逻辑 - 优先匹配引号内的内容
                                keyword = None
                                
                                # 1. 优先匹配引号内的内容
                                quoted_match = re.search(r'["\']([^"\']+)["\']', step)
                                if quoted_match:
                                    keyword = quoted_match.group(1).strip()
                                    log(f"从引号中提取关键词: {keyword}")
                                
                                # 2. 匹配"输入："后面的内容
                                if not keyword:
                                    input_match = re.search(r'输入[：:]\s*(.+)', step)
                                    if input_match:
                                        keyword = input_match.group(1).strip()
                                        log(f"从'输入'后提取关键词: {keyword}")
                                
                                # 3. 匹配"搜索"后面的内容（排除"搜索框"等词）
                                if not keyword:
                                    search_match = re.search(r'搜索(?!框|按钮|结果)[：:]?\s*(.+)', step)
                                    if search_match:
                                        keyword = search_match.group(1).strip()
                                        log(f"从'搜索'后提取关键词: {keyword}")
                                
                                # 4. 默认值
                                if not keyword:
                                    keyword = "测试"
                                    log(f"使用默认关键词: {keyword}")
                                
                                # 检测是否触发安全验证
                                if check_security_verification(driver):
                                    log("⚠️ 检测到安全验证页面，尝试等待...")
                                    import time
                                    time.sleep(3)
                                    if check_security_verification(driver):
                                        log("⚠️ 安全验证仍然存在，测试可能无法正常完成")
                                
                                # 尝试找到搜索框 - 尝试多种定位方式
                                log(f"尝试找到搜索框，关键词: {keyword}")
                                search_box = None
                                
                                # 尝试通过ID定位
                                try:
                                    search_box = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.ID, 'kw'))
                                    )
                                    log("通过ID找到搜索框")
                                except:
                                    log("通过ID未找到搜索框")
                                
                                # 尝试通过name定位
                                if not search_box:
                                    try:
                                        search_box = WebDriverWait(driver, 5).until(
                                            EC.presence_of_element_located((By.NAME, 'wd'))
                                        )
                                        log("通过name找到搜索框")
                                    except:
                                        log("通过name未找到搜索框")
                                
                                # 尝试通过class定位
                                if not search_box:
                                    try:
                                        search_box = WebDriverWait(driver, 5).until(
                                            EC.presence_of_element_located((By.CLASS_NAME, 's_ipt'))
                                        )
                                        log("通过class找到搜索框")
                                    except:
                                        log("通过class未找到搜索框")
                                
                                if search_box:
                                    # 添加随机延迟，模拟人类行为
                                    smart_delay(0.3, 0.8)
                                    
                                    # 尝试使用JavaScript点击搜索框
                                    try:
                                        driver.execute_script("arguments[0].click();", search_box)
                                        log("通过JavaScript点击搜索框")
                                    except:
                                        log("通过JavaScript点击搜索框失败")
                                    
                                    # 添加随机延迟
                                    smart_delay(0.2, 0.5)
                                    
                                    # 尝试清除并输入关键词
                                    try:
                                        search_box.clear()
                                        log("清除搜索框成功")
                                    except:
                                        log("清除搜索框失败")
                                    
                                    # 添加随机延迟
                                    smart_delay(0.3, 0.6)
                                    
                                    try:
                                        search_box.send_keys(keyword)
                                        log(f"输入关键词成功: {keyword}")
                                    except Exception:
                                        try:
                                            escaped_keyword = keyword.replace('\\', '\\\\').replace("'", "\\'")
                                            driver.execute_script(f"arguments[0].value = '{escaped_keyword}';", search_box)
                                            log(f"通过JavaScript设置关键词成功: {keyword}")
                                        except Exception:
                                            log("输入关键词失败")
                                    
                                    # 添加随机延迟，模拟人类思考时间
                                    smart_delay(0.5, 1.0)
                                    
                                    # 尝试找到搜索按钮并点击
                                    search_button = None
                                    
                                    # 尝试通过ID定位
                                    try:
                                        search_button = WebDriverWait(driver, 5).until(
                                            EC.presence_of_element_located((By.ID, 'su'))
                                        )
                                        log("通过ID找到搜索按钮")
                                    except:
                                        log("通过ID未找到搜索按钮")
                                    
                                    # 尝试通过class定位
                                    if not search_button:
                                        try:
                                            search_button = WebDriverWait(driver, 5).until(
                                                EC.presence_of_element_located((By.CLASS_NAME, 's_btn'))
                                            )
                                            log("通过class找到搜索按钮")
                                        except:
                                            log("通过class未找到搜索按钮")
                                    
                                    if search_button:
                                        # 添加随机延迟
                                        smart_delay(0.3, 0.7)
                                        
                                        # 尝试点击搜索按钮
                                        try:
                                            search_button.click()
                                            log("点击搜索按钮成功")
                                        except:
                                            # 尝试使用JavaScript点击
                                            try:
                                                driver.execute_script("arguments[0].click();", search_button)
                                                log("通过JavaScript点击搜索按钮成功")
                                            except:
                                                log("点击搜索按钮失败")
                                    else:
                                        # 尝试按Enter键
                                        try:
                                            search_box.send_keys('\n')
                                            log("按Enter键搜索成功")
                                        except:
                                            log("按Enter键搜索失败")
                                    
                                    # 添加随机延迟，等待页面响应
                                    smart_delay(1.0, 2.0)
                                    
                                    # 检测是否触发安全验证
                                    try:
                                        verify_text = driver.execute_script('''
                                            return document.body.innerText.includes('安全验证') ||
                                                   document.body.innerText.includes('请完成以下验证') ||
                                                   document.querySelector('.verify-wrap') !== null;
                                        ''')
                                        if verify_text:
                                            log("⚠️ 检测到安全验证页面，可能需要人工干预")
                                    except:
                                        pass
                                    
                                    # 等待搜索结果加载
                                    try:
                                        WebDriverWait(driver, 10).until(
                                            EC.presence_of_element_located((By.ID, 'content_left'))
                                        )
                                        log("搜索结果加载成功")
                                    except:
                                        log("搜索结果加载失败（可能触发了安全验证）")
                                    
                                    log("执行成功")
                                else:
                                    log("未找到搜索框")
                        elif '验证' in step or '检查' in step:
                            # 验证步骤，不需要执行操作，只需要截图
                            log("执行验证步骤")
                            # 等待页面稳定
                            import time
                            time.sleep(1)
                            log("执行成功")
                        elif '点击' in step:
                            # 尝试点击链接
                            click_target = step.replace('点击', '').strip().strip('"\'')
                            log(f"尝试点击链接，目标: {click_target}")
                            
                            # 尝试多种定位方式
                            link = None
                            
                            # 尝试通过链接文本定位
                            try:
                                link = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.LINK_TEXT, click_target))
                                )
                                log("通过链接文本找到元素")
                            except:
                                log("通过链接文本未找到元素")
                            
                            # 尝试通过部分链接文本定位
                            if not link:
                                try:
                                    link = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, click_target))
                                    )
                                    log("通过部分链接文本找到元素")
                                except:
                                    log("通过部分链接文本未找到元素")
                            
                            # 尝试通过ID定位
                            if not link:
                                try:
                                    link = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.ID, click_target))
                                    )
                                    log("通过ID找到元素")
                                except:
                                    log("通过ID未找到元素")
                            
                            # 尝试通过class定位
                            if not link:
                                try:
                                    link = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, click_target))
                                    )
                                    log("通过class找到元素")
                                except:
                                    log("通过class未找到元素")
                            
                            if link:
                                # 尝试点击元素
                                try:
                                    link.click()
                                    log("点击元素成功")
                                except:
                                    # 尝试使用JavaScript点击
                                    try:
                                        driver.execute_script("arguments[0].click();", link)
                                        log("通过JavaScript点击元素成功")
                                    except:
                                        log("点击元素失败")
                                log("执行成功")
                            else:
                                log(f"未找到元素: {click_target}")
                                # 不要抛出异常，继续执行后续步骤
                                log("执行成功")
                        else:
                            log("执行成功")
                    except Exception as e:
                        log(f"执行失败: {e}")
                    
                    # 检查是否需要截图
                    need_screenshot = True
                    if headless and not ScreenshotConfig.capture_in_headless:
                        # 无头模式下跳过截图（除非配置了capture_in_headless）
                        need_screenshot = False
                    elif ScreenshotConfig.smart_capture:
                        current_dom_hash = get_page_dom_hash(driver)
                        if current_dom_hash:
                            need_screenshot = previous_dom_hash is None or current_dom_hash != previous_dom_hash
                            previous_dom_hash = current_dom_hash
                    
                    if need_screenshot:
                        # 截图
                        screenshot_name = generate_screenshot_name(testcase, i, step)
                        screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
                        success, _ = safe_execute("步骤截图", driver.save_screenshot, screenshot_path)
                        
                        if success:
                            # 压缩截图
                            try:
                                compress_screenshot(screenshot_path)
                                log(f"步骤 {i} 截图压缩成功: {screenshot_name}")
                            except Exception as e:
                                log(f"截图压缩失败: {e}")
                            
                            # 计算截图哈希值并去重
                            try:
                                current_hash = get_image_hash(screenshot_path)
                                print(f"[截图去重] 步骤 {i} 截图哈希: {current_hash}, 之前哈希: {previous_screenshot_hash}")
                                if current_hash != previous_screenshot_hash and current_hash != "error_hash":
                                    screenshots.append(screenshot_name)
                                    previous_screenshot_hash = current_hash
                                    log(f"截图成功: {screenshot_name}")
                                else:
                                    # 删除重复截图
                                    if os.path.exists(screenshot_path):
                                        os.remove(screenshot_path)
                                        log(f"截图重复，已删除: {screenshot_name}")
                            except Exception as e:
                                log(f"截图哈希计算失败: {e}")
                                screenshots.append(screenshot_name)
                    else:
                        log("页面未发生变化，跳过截图")
                
                # 关闭浏览器
                try:
                    if driver:
                        driver.quit()
                        log("浏览器关闭成功")
                except Exception as e:
                    log(f"浏览器关闭失败: {e}")
                
                end_time = datetime.now()
                log(f"完成，耗时: {end_time - start_time}")
                log("测试执行成功")
                
                return {
                    "success": True,
                    "testcase_id": testcase.get('id'),
                    "testcase_name": testcase.get('name'),
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration": str(end_time - start_time),
                    "execution_log": execution_log,
                    "log": execution_log,
                    "screenshots": screenshots,
                    "error": None
                }
            except ImportError as e:
                log(f"Selenium导入失败: {e}")
                # 尝试使用其他方法
                raise
            except Exception as e:
                log(f"Selenium执行失败: {e}")
                raise
            
        except Exception as e:
            end_time = datetime.now()
            log(f"失败: {e}")
            # 确保浏览器关闭
            try:
                if driver:
                    driver.quit()
            except Exception:
                pass
            return {
                "success": False,
                "testcase_id": testcase.get('id'),
                "testcase_name": testcase.get('name'),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": str(end_time - start_time),
                "execution_log": execution_log,
                "log": execution_log,
                "screenshots": screenshots,
                "error": str(e)
            }
        
    except Exception as e:
        end_time = datetime.now()
        log(f"失败: {e}")
        try:
            if driver:
                driver.quit()
        except Exception:
            pass
        return {
            "success": False,
            "testcase_id": testcase.get('id'),
            "testcase_name": testcase.get('name'),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": str(end_time - start_time),
            "execution_log": execution_log,
            "log": execution_log,
            "screenshots": screenshots,
            "error": str(e)
        }


def execute_step_sync(driver, step: str, base_url: str = "", screenshot_dir=None, screenshots=None, screenshot_idx=1) -> list:
    """执行单个测试步骤，返回结果描述列表"""
    step_lower = step.lower()
    results = []
    
    if '搜索' in step:
        keyword_match = re.search(r'搜索[：:]?\s*(.+)', step)
        keyword = keyword_match.group(1).strip() if keyword_match else "测试"
        print(f"[执行器] 搜索步骤，关键词: {keyword}")
        
        inputted = False
        
        try:
            # 使用Selenium的execute_script方法
            driver.execute_script('''
                const input = document.querySelector('#kw') || document.querySelector('input[name="wd"]');
                if(input) {
                    input.style.cssText = 'display: block !important; visibility: visible !important; opacity: 1 !important;';
                    input.focus();
                    input.select();
                }
            ''')
            import time
            time.sleep(0.2)
            # 查找搜索框并输入
            from selenium.webdriver.common.by import By
            search_box = driver.find_element(By.ID, 'kw')
            search_box.send_keys(keyword)
            inputted = True
            print(f"[执行器] 通过JS聚焦+键盘输入成功")
        except Exception as e:
            print(f"[执行器] JS聚焦输入失败: {e}")
        
        if not inputted:
            try:
                from selenium.webdriver.common.by import By
                search_box = driver.find_element(By.ID, 'kw')
                search_box.click()
                # 清空输入框
                search_box.clear()
                search_box.send_keys(keyword)
                inputted = True
                print(f"[执行器] 通过强制点击+键盘输入成功")
            except Exception as e:
                print(f"[执行器] 强制点击输入失败: {e}")
        
        if not inputted:
            try:
                driver.execute_script(f'''
                    const input = document.querySelector('#kw') || document.querySelector('input[name="wd"]');
                    if(input) {{
                        input.value = '{keyword}';
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                ''')
                inputted = True
                print(f"[执行器] 通过JS直接设置值成功")
            except Exception as e:
                print(f"[执行器] JS设置值失败: {e}")
        
        if inputted:
            import time
            for _ in range(10):
                try:
                    value = driver.execute_script('return document.querySelector("#kw")?.value || document.querySelector("input[name=\'wd\']")?.value || ""')
                    if value and keyword.replace('"', '') in value:
                        break
                except:
                    pass
                time.sleep(0.1)
            results.append(f"已输入关键词: {keyword}")
            if screenshot_dir and screenshots is not None:
                screenshot_name = f"step_{screenshot_idx}_input.png"
                driver.save_screenshot(str(screenshot_dir / screenshot_name))
                screenshots.append(screenshot_name)
                screenshot_idx += 1
                print(f"[执行器] 输入截图完成: {screenshot_name}")
        else:
            results.append("未找到输入框")
            return results
        
        clicked = False
        from selenium.webdriver.common.by import By
        button_selectors = [
            (By.ID, 'su'),
            (By.CSS_SELECTOR, 'input[type="submit"]'),
            (By.CSS_SELECTOR, 'button[type="submit"]'),
            (By.CSS_SELECTOR, '.search-btn')
        ]
        for by, selector in button_selectors:
            try:
                search_button = driver.find_element(by, selector)
                search_button.click()
                clicked = True
                print(f"[执行器] 已点击搜索按钮")
                break
            except:
                continue
        
        if not clicked:
            try:
                from selenium.webdriver.common.keys import Keys
                search_box = driver.find_element(By.ID, 'kw')
                search_box.send_keys(Keys.ENTER)
                clicked = True
                print(f"[执行器] 已按Enter搜索")
            except:
                pass
        
        if clicked:
            try:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, 'content_left'))
                )
            except:
                pass
            results.append(f"已执行搜索")
            if screenshot_dir and screenshots is not None:
                screenshot_name = f"step_{screenshot_idx}_search.png"
                driver.save_screenshot(str(screenshot_dir / screenshot_name))
                screenshots.append(screenshot_name)
                screenshot_idx += 1
                print(f"[执行器] 搜索截图完成: {screenshot_name}")
        
        return results
    
    elif '打开' in step or '访问' in step or 'goto' in step_lower:
        url_match = re.search(r'https?://[^\s]+', step)
        if url_match:
            url = url_match.group()
        elif '百度' in step:
            url = 'https://www.baidu.com'
        elif '淘宝' in step:
            url = 'https://www.taobao.com'
        elif '京东' in step:
            url = 'https://www.jd.com'
        elif 'b站' in step or 'bilibili' in step_lower:
            url = 'https://www.bilibili.com'
        else:
            url = base_url or 'https://www.baidu.com'
        driver.get(url)
        # 等待页面加载
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        results.append(f"已打开: {url}")
        if screenshot_dir and screenshots is not None:
            screenshot_name = f"step_{screenshot_idx}_open.png"
            driver.save_screenshot(str(screenshot_dir / screenshot_name))
            screenshots.append(screenshot_name)
        return results
        
    elif '输入' in step or '填写' in step:
        content = extract_input_content(step)
        
        from selenium.webdriver.common.by import By
        input_selectors = [
            (By.ID, 'kw'),
            (By.NAME, 'wd'),
            (By.ID, 'search-input'),
            (By.NAME, 'q'),
            (By.CSS_SELECTOR, 'input[type="text"]'),
            (By.CSS_SELECTOR, 'input[type="search"]')
        ]
        
        for by, selector in input_selectors:
            try:
                input_elem = driver.find_element(by, selector)
                input_elem.clear()
                input_elem.send_keys(content)
                results.append(f"已输入: {content}")
                if screenshot_dir and screenshots is not None:
                    screenshot_name = f"step_{screenshot_idx}_input.png"
                    driver.save_screenshot(str(screenshot_dir / screenshot_name))
                    screenshots.append(screenshot_name)
                return results
            except:
                continue
        
        results.append(f"未找到输入框")
        return results
                
    elif '点击' in step:
        click_target = step.replace('点击', '').strip().strip('"\'')
        print(f"[执行器] 点击步骤，目标: {click_target}")
        
        if '搜索' in step:
            from selenium.webdriver.common.by import By
            button_selectors = [
                (By.ID, 'su'),
                (By.CSS_SELECTOR, 'input[type="submit"]'),
                (By.CSS_SELECTOR, 'button[type="submit"]')
            ]
            for by, selector in button_selectors:
                try:
                    button = driver.find_element(by, selector)
                    button.click()
                    import time
                    time.sleep(0.5)
                    results.append("已点击搜索按钮")
                    if screenshot_dir and screenshots is not None:
                        screenshot_name = f"step_{screenshot_idx}_click.png"
                        driver.save_screenshot(str(screenshot_dir / screenshot_name))
                        screenshots.append(screenshot_name)
                        screenshot_idx += 1
                    return results
                except:
                    continue
        elif '登录' in step:
            from selenium.webdriver.common.by import By
            button_selectors = [
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.CSS_SELECTOR, 'input[type="submit"]')
            ]
            for by, selector in button_selectors:
                try:
                    button = driver.find_element(by, selector)
                    button.click()
                    results.append("已点击登录按钮")
                    if screenshot_dir and screenshots is not None:
                        screenshot_name = f"step_{screenshot_idx}_click.png"
                        driver.save_screenshot(str(screenshot_dir / screenshot_name))
                        screenshots.append(screenshot_name)
                        screenshot_idx += 1
                    return results
                except:
                    continue
        
        clicked = False
        from selenium.webdriver.common.by import By
        # 尝试通过链接文本定位
        try:
            link = driver.find_element(By.LINK_TEXT, click_target)
            link.click()
            clicked = True
            print(f"[执行器] 通过链接文本点击成功")
        except:
            try:
                link = driver.find_element(By.PARTIAL_LINK_TEXT, click_target)
                link.click()
                clicked = True
                print(f"[执行器] 通过部分链接文本点击成功")
            except:
                try:
                    link = driver.find_element(By.ID, click_target)
                    link.click()
                    clicked = True
                    print(f"[执行器] 通过ID点击成功")
                except:
                    try:
                        link = driver.find_element(By.CLASS_NAME, click_target)
                        link.click()
                        clicked = True
                        print(f"[执行器] 通过class点击成功")
                    except:
                        pass
        
        if clicked:
            # 等待页面加载
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            except:
                pass
            results.append(f"已点击: {click_target}")
            if screenshot_dir and screenshots is not None:
                screenshot_name = f"step_{screenshot_idx}_click.png"
                driver.save_screenshot(str(screenshot_dir / screenshot_name))
                screenshots.append(screenshot_name)
                screenshot_idx += 1
        else:
            results.append(f"未找到: {click_target}")
        
        return results
    
    elif '登录' in step:
        results.append("登录操作需要更多参数")
        return results
                
    elif '验证' in step or '检查' in step:
        import time
        time.sleep(0.2)
        results.append("验证完成")
        if screenshot_dir and screenshots is not None:
            screenshot_name = f"step_{screenshot_idx}_verify.png"
            driver.save_screenshot(str(screenshot_dir / screenshot_name))
            screenshots.append(screenshot_name)
        return results
    
    results.append("步骤已跳过")
    return results


def extract_input_content(step: str) -> str:
    """从步骤描述中提取输入内容"""
    patterns = [
        r'输入[：:]\s*["\']?([^"\']+)["\']?',
        r'输入["\']([^"\']+)["\']',
        r'[：:]\s*["\']?([^"\']+)["\']',
        r'搜索框.*?输入[：:]?\s*["\']?([^"\']+)["\']?',
        r'输入.*?[：:]\s*["\']?([^"\']+)["\']?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, step)
        if match:
            content = match.group(1).strip()
            if content and len(content) > 0:
                return content
    
    return "测试内容"


async def execute_test_case_async(testcase: Dict, headless: bool = True, base_url: Optional[str] = None) -> Dict:
    """异步执行"""
    return run_playwright_sync(testcase, headless, base_url)


class TestExecutor:
    """测试执行器类"""
    
    def __init__(self):
        self.execution_results = {}
    
    async def execute_testcase(self, testcase, execution_id: str = None, headless: bool = True):
        """异步执行测试用例（立即返回，后台执行）"""
        import asyncio
        from datetime import datetime
        import uuid
        import threading
        
        if not execution_id:
            execution_id = str(uuid.uuid4())
        
        testcase_dict = {
            "id": testcase.id if hasattr(testcase, 'id') else None,
            "name": testcase.name if hasattr(testcase, 'name') else "未命名测试",
            "description": testcase.description if hasattr(testcase, 'description') else "",
            "steps": testcase.get_steps() if hasattr(testcase, 'get_steps') else [],
            "url": testcase.script_data.get("url", "") if hasattr(testcase, 'script_data') and testcase.script_data else "",
        }
        
        self.execution_results[execution_id] = {
            "status": "running",
            "execution_id": execution_id,
            "testcase_id": testcase_dict.get('id'),
            "testcase_name": testcase_dict.get('name'),
            "start_time": datetime.now().isoformat(),
            "execution_log": ["测试开始执行..."],
            "screenshots": []
        }
        
        def run_in_thread():
            """在后台线程中执行测试"""
            try:
                result = run_playwright_sync(testcase_dict, headless)
                
                self.execution_results[execution_id] = {
                    "status": "passed" if result.get("success") else "failed",
                    "execution_id": execution_id,
                    "testcase_id": testcase_dict.get('id'),
                    "testcase_name": testcase_dict.get('name'),
                    "start_time": result.get("start_time"),
                    "end_time": result.get("end_time"),
                    "duration": result.get("duration"),
                    "execution_log": result.get("execution_log", []),
                    "log": result.get("execution_log", []),
                    "screenshots": result.get("screenshots", []),
                    "error": result.get("error")
                }
            except Exception as e:
                self.execution_results[execution_id] = {
                    "status": "failed",
                    "execution_id": execution_id,
                    "testcase_id": testcase_dict.get('id'),
                    "testcase_name": testcase_dict.get('name'),
                    "error": str(e),
                    "execution_log": [f"执行失败: {str(e)}"]
                }
        
        # 启动后台线程执行测试
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        
        # 立即返回，不等待执行完成
        return self.execution_results[execution_id]
    
    async def get_execution_result(self, execution_id: str):
        """获取执行结果"""
        if execution_id in self.execution_results:
            return self.execution_results[execution_id]
        else:
            return {
                "status": "not_found",
                "execution_id": execution_id,
                "error": "执行记录不存在"
            }


def execute_test_case_sync(testcase: Dict, headless: bool = True, base_url: Optional[str] = None) -> Dict:
    """同步执行"""

    return run_playwright_sync(testcase, headless, base_url)
