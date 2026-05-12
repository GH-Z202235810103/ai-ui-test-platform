"""
优化后的测试执行器 - 集成日志记录、重试机制、智能等待和数据库持久化

主要改进：
1. 使用 ExecutionLogger 进行结构化日志记录
2. 使用 RetryStrategy 进行智能重试
3. 使用 SmartWait 进行智能等待
4. 使用 StepParser 进行步骤解析
5. 添加数据库持久化功能
6. 改进错误处理和异常捕获
7. 支持并发执行
"""

import re
import uuid
import time
import threading
import traceback
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException,
    ElementNotInteractableException, StaleElementReferenceException
)

from core.step_parser import StepParser, ParsedStep
from core.retry_strategy import RetryStrategy, RetryResult
from core.execution_logger import ExecutionLogger
from core.smart_wait import SmartWait
from database import db_manager, TestReport, ReportStep, TestCase, TestTask

SCREENSHOT_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


class ExecutionResult:
    """执行结果数据类"""
    
    def __init__(self, execution_id: str, testcase_id: int, testcase_name: str):
        self.execution_id = execution_id
        self.testcase_id = testcase_id
        self.testcase_name = testcase_name
        self.status = "pending"
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.duration: Optional[str] = None
        self.execution_log: List[str] = []
        self.screenshots: List[str] = []
        self.steps: List[Dict[str, Any]] = []
        self.error: Optional[str] = None
        self.driver = None
        self.report_id: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "execution_id": self.execution_id,
            "testcase_id": self.testcase_id,
            "testcase_name": self.testcase_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "execution_log": self.execution_log,
            "screenshots": self.screenshots,
            "steps": self.steps,
            "error": self.error,
            "report_id": self.report_id
        }


class OptimizedTestExecutor:
    """优化后的测试执行器"""
    
    def __init__(self, headless: bool = True, log_level: str = 'normal', 
                 timeout: int = 30, retry_count: int = 3, screenshot_quality: int = 80,
                 screenshot_enabled: bool = True):
        self.headless = headless
        self.log_level = log_level
        self.timeout = timeout
        self.retry_count = retry_count
        self.screenshot_quality = screenshot_quality
        self.screenshot_enabled = screenshot_enabled
        self.execution_results: Dict[str, ExecutionResult] = {}
        self._lock = threading.Lock()
    
    def create_driver(self) -> Optional[webdriver.Remote]:
        """创建浏览器驱动，支持多浏览器回退"""
        browsers = [
            ('Edge', self._create_edge_driver),
            ('Chrome', self._create_chrome_driver),
            ('Firefox', self._create_firefox_driver),
        ]
        
        for name, create_func in browsers:
            try:
                driver = create_func()
                if driver:
                    print(f"[执行器] {name} 浏览器启动成功")
                    return driver
            except Exception as e:
                print(f"[执行器] {name} 浏览器启动失败: {e}")
                continue
        
        return None
    
    def _create_edge_driver(self) -> Optional[webdriver.Remote]:
        """创建 Edge 浏览器驱动"""
        from selenium.webdriver.edge.options import Options
        
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Edge(options=options)
        
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
            })
        except Exception:
            pass
        
        return driver
    
    def _create_chrome_driver(self) -> Optional[webdriver.Remote]:
        """创建 Chrome 浏览器驱动"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
            })
        except Exception:
            pass
        
        return driver
    
    def _create_firefox_driver(self) -> Optional[webdriver.Remote]:
        """创建 Firefox 浏览器驱动"""
        from selenium.webdriver.firefox.options import Options
        
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Firefox(options=options)
        return driver
    
    def execute_testcase(
        self, 
        testcase: Dict, 
        execution_id: Optional[str] = None,
        save_to_db: bool = True
    ) -> ExecutionResult:
        """执行测试用例
        
        Args:
            testcase: 测试用例字典
            execution_id: 执行ID，如果不提供则自动生成
            save_to_db: 是否保存到数据库
        
        Returns:
            ExecutionResult: 执行结果对象
        """
        if not execution_id:
            execution_id = str(uuid.uuid4())
        
        result = ExecutionResult(
            execution_id=execution_id,
            testcase_id=testcase.get('id'),
            testcase_name=testcase.get('name', '未命名测试')
        )
        
        logger = ExecutionLogger(headless=self.headless, level=self.log_level)
        retry_strategy = RetryStrategy(max_retries=self.retry_count, base_delay=1.0, backoff=2.0)
        step_parser = StepParser()
        
        with self._lock:
            self.execution_results[execution_id] = result
        
        try:
            logger.log(f"开始执行测试用例: {result.testcase_name}", category='info')
            logger.log(f"执行参数: 无头模式={self.headless}, 超时={self.timeout}秒, 重试次数={self.retry_count}, 截图质量={self.screenshot_quality}%", category='info')
            result.status = "running"
            
            driver = self.create_driver()
            if not driver:
                raise Exception("无法启动任何浏览器")
            
            result.driver = driver
            smart_wait = SmartWait(driver, default_timeout=self.timeout)
            
            steps = testcase.get('steps', [])
            url = testcase.get('url') or 'https://www.baidu.com'
            
            # 从步骤描述中提取URL
            if not url or url == 'https://www.baidu.com':
                if steps:
                    for step in steps:
                        # step 可能是字典或字符串
                        step_text = step if isinstance(step, str) else step.get('description', '') or step.get('url', '')
                        if step_text:
                            match = re.search(r'(https?://[^\s]+)', step_text)
                            if match:
                                url = match.group(1)
                                break
            
            # 验证URL格式
            if not url or not url.startswith(('http://', 'https://')):
                url = 'https://www.baidu.com'
                logger.log_warning(f"URL无效或为空，使用默认URL: {url}")
            
            logger.log_step(0, f"访问页面: {url}")
            try:
                driver.get(url)
                smart_wait.wait_for_page_stable(timeout=self.timeout)
            except Exception as e:
                logger.log_error(f"访问页面失败: {url}, 错误: {e}")
                raise
            
            screenshot_name = self._take_screenshot(driver, result, 0, "homepage")
            if screenshot_name:
                logger.log_screenshot(screenshot_name, "首页截图")
            
            for idx, step_desc in enumerate(steps, 1):
                # step_desc 可能是字典或字符串，提取描述文本
                step_text = step_desc if isinstance(step_desc, str) else step_desc.get("description", str(step_desc))
                logger.log_step(idx, step_text)
                
                step_result = self._execute_step(
                    driver=driver,
                    step_desc=step_desc,
                    step_parser=step_parser,
                    smart_wait=smart_wait,
                    retry_strategy=retry_strategy,
                    logger=logger,
                    step_idx=idx
                )
                
                result.steps.append(step_result)
                
                if step_result.get("screenshot"):
                    logger.log_screenshot(step_result["screenshot"], f"步骤{idx}截图")
                
                if not step_result.get("success", False):
                    logger.log_error(f"步骤 {idx} 执行失败: {step_result.get('error', '未知错误')}")
                    result.error = f"步骤 {idx} 失败: {step_result.get('error')}"
                    result.status = "failed"
                    break  # 步骤失败，停止后续执行
                else:
                    logger.log_success(f"步骤 {idx} 执行成功")
            
            if result.status != "failed":
                result.status = "passed"
                logger.log_success("测试用例执行完成")
            
        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            logger.log_error(f"测试用例执行失败: {e}")
            logger.log_error(f"错误堆栈: {traceback.format_exc()}")
        
        finally:
            if result.driver:
                try:
                    result.driver.quit()
                    logger.log("浏览器已关闭", category='info')
                except Exception as e:
                    logger.log_error(f"关闭浏览器失败: {e}")
            
            result.end_time = datetime.now()
            result.duration = str(result.end_time - result.start_time)
            result.execution_log = logger.get_logs()
            
            if save_to_db:
                save_success = self._save_to_database(result, testcase)
                if save_success:
                    logger.log_success(f"执行结果已成功保存到数据库，报告ID: {result.report_id}")
                else:
                    logger.log_error("执行结果保存到数据库失败，请检查数据库连接和配置")
        
        return result
    
    def _execute_step(
        self,
        driver: webdriver.Remote,
        step_desc: str,
        step_parser: StepParser,
        smart_wait: SmartWait,
        retry_strategy: RetryStrategy,
        logger: ExecutionLogger,
        step_idx: int
    ) -> Dict[str, Any]:
        """执行单个测试步骤
        
        Args:
            driver: WebDriver 实例
            step_desc: 步骤描述
            step_parser: 步骤解析器
            smart_wait: 智能等待器
            retry_strategy: 重试策略
            logger: 日志记录器
            step_idx: 步骤索引
        
        Returns:
            Dict: 步骤执行结果
        """
        step_result = {
            'step_index': step_idx,
            'step_desc': step_desc,
            'success': False,
            'error': None,
            'screenshot': None,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': None
        }
        
        start_time = datetime.now()
        
        step_text = step_desc if isinstance(step_desc, str) else step_desc.get('description', str(step_desc))
        
        try:
            parsed = step_parser.parse(step_desc)
            logger.log(f"解析步骤: {parsed.operation}, 参数: {parsed.params}", category='debug')
            
            def execute_operation():
                return self._execute_parsed_operation(
                    driver=driver,
                    parsed=parsed,
                    smart_wait=smart_wait,
                    logger=logger
                )
            
            retry_result = retry_strategy.execute_with_retry(
                execute_operation,
                action_name=f"步骤{step_idx}"
            )
            
            if retry_result.success:
                step_result['success'] = True
                step_result['result'] = retry_result.result
                logger.log(f"步骤 {step_idx} 执行成功 (尝试次数: {retry_result.attempts})", category='debug')
            else:
                step_result['success'] = False
                step_result['error'] = str(retry_result.error) if retry_result.error else "执行失败"
                logger.log_error(f"步骤 {step_idx} 执行失败: {step_result['error']}")
        
        except Exception as e:
            step_result['success'] = False
            step_result['error'] = str(e)
            logger.log_error(f"步骤 {step_idx} 执行异常: {e}")
            logger.log_error(f"异常堆栈: {traceback.format_exc()}")
        
        finally:
            safe_step_text = re.sub(r'[^\w\-]', '', step_text)[:20]
            screenshot_name = self._take_screenshot(driver, None, step_idx, safe_step_text)
            if screenshot_name:
                step_result['screenshot'] = screenshot_name
            
            end_time = datetime.now()
            step_result['end_time'] = end_time.isoformat()
            step_result['duration'] = str(end_time - start_time)
        
        return step_result
    
    def _execute_parsed_operation(
        self,
        driver: webdriver.Remote,
        parsed: ParsedStep,
        smart_wait: SmartWait,
        logger: ExecutionLogger
    ) -> Any:
        """执行解析后的操作
        
        Args:
            driver: WebDriver 实例
            parsed: 解析后的步骤
            smart_wait: 智能等待器
            logger: 日志记录器
        
        Returns:
            Any: 操作结果
        """
        operation = parsed.operation
        params = parsed.params
        
        if operation == 'open':
            url = params.get('url', 'https://www.baidu.com')
            logger.log(f"打开页面: {url}", category='action')
            driver.get(url)
            smart_wait.wait_for_page_stable(timeout=10)
            return {'url': url}
        
        elif operation == 'input':
            value = params.get('value', '')
            target = params.get('target', 'default')
            
            logger.log(f"输入内容: {value} 到 {target}", category='action')
            
            selectors = [
                (By.ID, 'kw'),
                (By.NAME, 'wd'),
                (By.CSS_SELECTOR, 'input[type="text"]'),
            ]
            
            element = smart_wait.wait_for_element(selectors, timeout=5)
            element.clear()
            element.send_keys(value)
            
            return {'value': value, 'target': target}
        
        elif operation == 'click':
            target = params.get('target', '')
            logger.log(f"点击元素: {target}", category='action')
            
            selectors = [
                (By.ID, target),
                (By.CLASS_NAME, target),
                (By.LINK_TEXT, target),
                (By.PARTIAL_LINK_TEXT, target),
            ]
            
            element = smart_wait.wait_for_element(selectors, timeout=5)
            element.click()
            
            smart_wait.wait_for_page_stable(timeout=3)
            
            return {'target': target}
        
        elif operation == 'search':
            keyword = params.get('keyword', '')
            logger.log(f"搜索关键词: {keyword}", category='action')
            
            input_selectors = [(By.ID, 'kw'), (By.NAME, 'wd')]
            input_element = smart_wait.wait_for_element(input_selectors, timeout=5)
            input_element.clear()
            input_element.send_keys(keyword)
            
            button_selectors = [(By.ID, 'su'), (By.CSS_SELECTOR, 'input[type="submit"]')]
            try:
                button_element = smart_wait.wait_for_element(button_selectors, timeout=5)
                button_element.click()
            except TimeoutException:
                input_element.send_keys('\n')
            
            smart_wait.wait_for_page_stable(timeout=5)
            
            return {'keyword': keyword}
        
        elif operation == 'wait':
            duration = params.get('duration', 1)
            logger.log(f"等待 {duration} 秒", category='action')
            time.sleep(duration)
            return {'duration': duration}
        
        elif operation == 'verify':
            expected = params.get('expected', '')
            logger.log(f"验证内容: {expected}", category='action')
            
            page_source = driver.page_source
            if expected and expected in page_source:
                return {'verified': True, 'expected': expected}
            else:
                raise Exception(f"验证失败: 页面中未找到 '{expected}'")
        
        else:
            logger.log_warning(f"未知操作: {operation}, 跳过执行")
            return {'operation': operation, 'skipped': True}
    
    def _take_screenshot(
        self,
        driver: webdriver.Remote,
        result: Optional[ExecutionResult],
        step_idx: int,
        desc: str
    ) -> Optional[str]:
        """截图并保存
        
        Args:
            driver: WebDriver 实例
            result: 执行结果对象
            step_idx: 步骤索引
            desc: 截图描述
        
        Returns:
            Optional[str]: 截图文件名，失败返回 None
        """
        if not self.screenshot_enabled:
            return None
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            
            safe_desc = re.sub(r'[^\w\-]', '', desc)[:20]
            screenshot_name = f"step_{step_idx}_{safe_desc}_{timestamp}_{unique_id}.png"
            screenshot_path = SCREENSHOT_DIR / screenshot_name
            
            driver.save_screenshot(str(screenshot_path))
            
            if self.screenshot_quality < 100:
                try:
                    from PIL import Image
                    img = Image.open(screenshot_path)
                    if img.format != 'JPEG':
                        jpg_path = screenshot_path.with_suffix('.jpg')
                        img.save(jpg_path, 'JPEG', quality=self.screenshot_quality, optimize=True)
                        screenshot_name = jpg_path.name
                        screenshot_path.unlink()
                        screenshot_path = jpg_path
                except Exception as e:
                    print(f"[执行器] 图片压缩失败: {e}")
            
            if result:
                result.screenshots.append(screenshot_name)
            
            return screenshot_name
        
        except Exception as e:
            print(f"[执行器] 截图失败: {e}")
            return None
    
    def _save_to_database(self, result: ExecutionResult, testcase: Dict) -> bool:
        """保存执行结果到数据库
        
        Args:
            result: 执行结果对象
            testcase: 测试用例字典
        
        Returns:
            bool: 是否保存成功
        """
        db = None
        try:
            print(f"[执行器] 开始保存执行结果到数据库...")
            print(f"[执行器] 测试用例ID: {result.testcase_id}, 名称: {result.testcase_name}")
            print(f"[执行器] 执行ID: {result.execution_id}, 状态: {result.status}")
            print(f"[执行器] 步骤总数: {len(result.steps)}, 成功: {sum(1 for s in result.steps if s.get('success'))}, 失败: {sum(1 for s in result.steps if not s.get('success'))}")
            
            db = db_manager.get_session()
            
            report = TestReport(
                task_id=None,
                total_count=len(result.steps),
                pass_count=sum(1 for s in result.steps if s.get('success')),
                fail_count=sum(1 for s in result.steps if not s.get('success')),
                skip_count=0,
                summary={
                    'testcase_id': result.testcase_id,
                    'testcase_name': result.testcase_name,
                    'execution_id': result.execution_id,
                    'status': result.status,
                    'error': result.error
                },
                details='\n'.join(result.execution_log),
                duration=int((result.end_time - result.start_time).total_seconds()) if result.end_time and result.start_time else 0,
                screenshot_refs=result.screenshots,
                status=result.status
            )
            
            print(f"[执行器] 创建TestReport对象成功")
            db.add(report)
            print(f"[执行器] 添加report到session")
            db.flush()
            print(f"[执行器] flush成功，report.id: {report.id}")
            
            step_count = 0
            for step in result.steps:
                step_desc_value = step.get('step_desc', '')
                if isinstance(step_desc_value, dict):
                    step_desc_str = step_desc_value.get('description', str(step_desc_value))
                else:
                    step_desc_str = str(step_desc_value) if step_desc_value else ''
                
                report_step = ReportStep(
                    report_id=report.id,
                    step_index=step.get('step_index', 0),
                    step_name=step_desc_str,
                    step_desc=step_desc_str,
                    status='passed' if step.get('success') else 'failed',
                    duration=0,
                    error_message=step.get('error'),
                    actual_screenshot=step.get('screenshot')
                )
                db.add(report_step)
                step_count += 1
            
            print(f"[执行器] 添加了 {step_count} 个ReportStep")
            
            db.commit()
            print(f"[执行器] commit成功")
            
            result.report_id = report.id
            print(f"[执行器] [OK] 执行结果已保存到数据库，报告ID: {report.id}")
            return True
        
        except Exception as e:
            print(f"[执行器] [ERROR] 保存到数据库失败: {e}")
            print(f"[执行器] 错误类型: {type(e).__name__}")
            import traceback
            print(f"[执行器] 错误堆栈:\n{traceback.format_exc()}")
            if db:
                try:
                    db.rollback()
                    print(f"[执行器] 已回滚事务")
                except Exception as rollback_error:
                    print(f"[执行器] 回滚失败: {rollback_error}")
            return False
        
        finally:
            if db:
                try:
                    db.close()
                    print(f"[执行器] 数据库连接已关闭")
                except Exception as close_error:
                    print(f"[执行器] 关闭数据库连接失败: {close_error}")
    
    def get_execution_result(self, execution_id: str) -> Optional[Dict]:
        """获取执行结果
        
        Args:
            execution_id: 执行ID
        
        Returns:
            Optional[Dict]: 执行结果字典，如果不存在返回 None
        """
        with self._lock:
            result = self.execution_results.get(execution_id)
            if result:
                return result.to_dict()
        return None


def execute_testcase_sync(
    testcase: Dict,
    headless: bool = True,
    save_to_db: bool = True,
    log_level: str = 'normal',
    timeout: int = 30,
    retry_count: int = 3,
    screenshot_quality: int = 80,
    screenshot_enabled: bool = True,
    execution_id: Optional[str] = None,
    executor: Optional['OptimizedTestExecutor'] = None
) -> Dict:
    """同步执行测试用例（便捷函数）
    
    Args:
        testcase: 测试用例字典
        headless: 是否使用无头模式
        save_to_db: 是否保存到数据库
        log_level: 日志级别
        timeout: 执行超时时间（秒）
        retry_count: 重试次数
        screenshot_quality: 截图质量
        screenshot_enabled: 是否启用截图
        execution_id: 执行ID，如果不提供则自动生成
        executor: 执行器实例，如果不提供则创建新实例
    
    Returns:
        Dict: 执行结果字典
    """
    if executor is None:
        executor = OptimizedTestExecutor(
            headless=headless, 
            log_level=log_level,
            timeout=timeout,
            retry_count=retry_count,
            screenshot_quality=screenshot_quality,
            screenshot_enabled=screenshot_enabled
        )
    result = executor.execute_testcase(testcase, execution_id=execution_id, save_to_db=save_to_db)
    return result.to_dict()


async def execute_testcase_async(
    testcase: Dict,
    headless: bool = True,
    save_to_db: bool = True,
    log_level: str = 'normal',
    timeout: int = 30,
    retry_count: int = 3,
    screenshot_quality: int = 80,
    screenshot_enabled: bool = True
) -> Dict:
    """异步执行测试用例（便捷函数）
    
    Args:
        testcase: 测试用例字典
        headless: 是否使用无头模式
        save_to_db: 是否保存到数据库
        log_level: 日志级别
        timeout: 执行超时时间（秒）
        retry_count: 重试次数
        screenshot_quality: 截图质量
        screenshot_enabled: 是否启用截图
    
    Returns:
        Dict: 执行结果字典
    """
    import asyncio
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: execute_testcase_sync(testcase, headless, save_to_db, log_level, timeout, retry_count, screenshot_quality, screenshot_enabled)
    )
    
    return result
