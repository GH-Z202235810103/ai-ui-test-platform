"""
测试优化后的执行引擎 - 单元测试（不需要启动浏览器）

测试内容：
1. 执行引擎基本功能
2. 数据库持久化功能
3. 日志记录功能
4. 错误处理功能
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.executor_optimized import (
    OptimizedTestExecutor,
    ExecutionResult,
)
from core.step_parser import StepParser
from core.execution_logger import ExecutionLogger
from core.retry_strategy import RetryStrategy


class TestExecutionResult:
    """测试执行结果类"""
    
    def test_creation(self):
        """测试创建执行结果对象"""
        result = ExecutionResult(
            execution_id="test-123",
            testcase_id=1,
            testcase_name="测试用例"
        )
        
        assert result.execution_id == "test-123"
        assert result.testcase_id == 1
        assert result.testcase_name == "测试用例"
        assert result.status == "pending"
        assert isinstance(result.execution_log, list)
        assert isinstance(result.screenshots, list)
        assert isinstance(result.steps, list)
        assert result.error is None
        assert result.driver is None
    
    def test_to_dict(self):
        """测试转换为字典"""
        result = ExecutionResult(
            execution_id="test-456",
            testcase_id=2,
            testcase_name="字典测试"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['execution_id'] == "test-456"
        assert result_dict['testcase_id'] == 2
        assert result_dict['testcase_name'] == "字典测试"
        assert 'status' in result_dict
        assert 'start_time' in result_dict
        assert 'end_time' in result_dict
        assert 'execution_log' in result_dict
        assert 'screenshots' in result_dict
        assert 'steps' in result_dict
        assert 'error' in result_dict


class TestOptimizedTestExecutor:
    """测试优化后的执行器"""
    
    def test_initialization(self):
        """测试执行器初始化"""
        executor = OptimizedTestExecutor(headless=True, log_level='verbose')
        
        assert executor is not None
        assert executor.headless == True
        assert executor.log_level == 'verbose'
        assert isinstance(executor.execution_results, dict)
    
    def test_get_execution_result(self):
        """测试获取执行结果"""
        executor = OptimizedTestExecutor(headless=True)
        
        result = ExecutionResult(
            execution_id="test-789",
            testcase_id=3,
            testcase_name="获取测试"
        )
        
        executor.execution_results["test-789"] = result
        
        retrieved = executor.get_execution_result("test-789")
        
        assert retrieved is not None
        assert retrieved['execution_id'] == "test-789"
        assert retrieved['testcase_id'] == 3
    
    def test_get_execution_result_not_found(self):
        """测试获取不存在的执行结果"""
        executor = OptimizedTestExecutor(headless=True)
        
        retrieved = executor.get_execution_result("non-existent")
        
        assert retrieved is None
    
    @patch('core.executor_optimized.webdriver.Edge')
    @patch('core.executor_optimized.webdriver.Chrome')
    @patch('core.executor_optimized.webdriver.Firefox')
    def test_create_driver(self, mock_firefox, mock_chrome, mock_edge):
        """测试创建浏览器驱动"""
        executor = OptimizedTestExecutor(headless=True)
        
        mock_driver = Mock()
        mock_edge.return_value = mock_driver
        
        driver = executor.create_driver()
        
        assert driver is not None
        mock_edge.assert_called_once()
    
    @patch('core.executor_optimized.webdriver.Edge')
    @patch('core.executor_optimized.webdriver.Chrome')
    @patch('core.executor_optimized.webdriver.Firefox')
    def test_create_driver_fallback(self, mock_firefox, mock_chrome, mock_edge):
        """测试浏览器驱动回退机制"""
        executor = OptimizedTestExecutor(headless=True)
        
        mock_edge.side_effect = Exception("Edge failed")
        mock_chrome.side_effect = Exception("Chrome failed")
        mock_driver = Mock()
        mock_firefox.return_value = mock_driver
        
        driver = executor.create_driver()
        
        assert driver is not None
        mock_edge.assert_called_once()
        mock_chrome.assert_called_once()
        mock_firefox.assert_called_once()
    
    def test_take_screenshot(self):
        """测试截图功能"""
        executor = OptimizedTestExecutor(headless=True)
        
        mock_driver = Mock()
        mock_driver.save_screenshot = Mock()
        
        result = ExecutionResult(
            execution_id="test-screenshot",
            testcase_id=4,
            testcase_name="截图测试"
        )
        
        screenshot_name = executor._take_screenshot(
            driver=mock_driver,
            result=result,
            step_idx=1,
            desc="test step"
        )
        
        assert screenshot_name is not None
        assert screenshot_name.startswith("step_1_")
        assert screenshot_name.endswith(".png")
        assert screenshot_name in result.screenshots
        
        mock_driver.save_screenshot.assert_called_once()
    
    def test_save_to_database(self):
        """测试保存到数据库"""
        executor = OptimizedTestExecutor(headless=True)
        
        result = ExecutionResult(
            execution_id="test-db",
            testcase_id=5,
            testcase_name="数据库测试"
        )
        result.status = "passed"
        result.end_time = result.start_time
        result.execution_log = ["日志1", "日志2"]
        result.screenshots = ["screenshot1.png"]
        result.steps = [
            {
                'step_index': 1,
                'step_desc': '步骤1',
                'success': True,
                'error': None,
                'screenshot': 'screenshot1.png'
            }
        ]
        
        testcase = {
            "id": 5,
            "name": "数据库测试"
        }
        
        with patch('core.executor_optimized.SessionLocal') as mock_session_local:
            mock_db = Mock()
            mock_session_local.return_value = mock_db
            
            mock_report = Mock()
            mock_report.id = 100
            mock_db.add = Mock()
            mock_db.flush = Mock()
            mock_db.commit = Mock()
            mock_db.rollback = Mock()
            mock_db.close = Mock()
            
            saved = executor._save_to_database(result, testcase)
            
            assert saved == True
            mock_db.add.assert_called()
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()


class TestStepExecution:
    """测试步骤执行"""
    
    def test_execute_parsed_operation_open(self):
        """测试打开页面操作"""
        executor = OptimizedTestExecutor(headless=True)
        
        mock_driver = Mock()
        mock_driver.get = Mock()
        
        from core.smart_wait import SmartWait
        smart_wait = SmartWait(mock_driver, default_timeout=5)
        smart_wait.wait_for_page_stable = Mock()
        
        logger = ExecutionLogger(headless=True, level='normal')
        
        from core.step_parser import ParsedStep
        parsed = ParsedStep(
            raw="打开百度",
            operation='open',
            params={'url': 'https://www.baidu.com'}
        )
        
        result = executor._execute_parsed_operation(
            driver=mock_driver,
            parsed=parsed,
            smart_wait=smart_wait,
            logger=logger
        )
        
        assert result is not None
        assert result['url'] == 'https://www.baidu.com'
        mock_driver.get.assert_called_once_with('https://www.baidu.com')
    
    def test_execute_parsed_operation_input(self):
        """测试输入操作"""
        executor = OptimizedTestExecutor(headless=True)
        
        mock_driver = Mock()
        
        from core.smart_wait import SmartWait
        smart_wait = Mock(spec=SmartWait)
        
        mock_element = Mock()
        mock_element.clear = Mock()
        mock_element.send_keys = Mock()
        smart_wait.wait_for_element = Mock(return_value=mock_element)
        
        logger = ExecutionLogger(headless=True, level='normal')
        
        from core.step_parser import ParsedStep
        parsed = ParsedStep(
            raw="输入测试",
            operation='input',
            params={'value': '测试内容', 'target': 'default'}
        )
        
        result = executor._execute_parsed_operation(
            driver=mock_driver,
            parsed=parsed,
            smart_wait=smart_wait,
            logger=logger
        )
        
        assert result is not None
        assert result['value'] == '测试内容'
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with('测试内容')
    
    def test_execute_parsed_operation_click(self):
        """测试点击操作"""
        executor = OptimizedTestExecutor(headless=True)
        
        mock_driver = Mock()
        
        from core.smart_wait import SmartWait
        smart_wait = Mock(spec=SmartWait)
        
        mock_element = Mock()
        mock_element.click = Mock()
        smart_wait.wait_for_element = Mock(return_value=mock_element)
        smart_wait.wait_for_page_stable = Mock()
        
        logger = ExecutionLogger(headless=True, level='normal')
        
        from core.step_parser import ParsedStep
        parsed = ParsedStep(
            raw="点击按钮",
            operation='click',
            params={'target': 'submit-button'}
        )
        
        result = executor._execute_parsed_operation(
            driver=mock_driver,
            parsed=parsed,
            smart_wait=smart_wait,
            logger=logger
        )
        
        assert result is not None
        assert result['target'] == 'submit-button'
        mock_element.click.assert_called_once()
    
    def test_execute_parsed_operation_wait(self):
        """测试等待操作"""
        executor = OptimizedTestExecutor(headless=True)
        
        mock_driver = Mock()
        
        from core.smart_wait import SmartWait
        smart_wait = Mock(spec=SmartWait)
        
        logger = ExecutionLogger(headless=True, level='normal')
        
        from core.step_parser import ParsedStep
        parsed = ParsedStep(
            raw="等待2秒",
            operation='wait',
            params={'duration': 2}
        )
        
        import time
        with patch.object(time, 'sleep') as mock_sleep:
            result = executor._execute_parsed_operation(
                driver=mock_driver,
                parsed=parsed,
                smart_wait=smart_wait,
                logger=logger
            )
            
            assert result is not None
            assert result['duration'] == 2
            mock_sleep.assert_called_once_with(2)


class TestIntegration:
    """集成测试"""
    
    def test_step_parser_integration(self):
        """测试步骤解析器集成"""
        parser = StepParser()
        
        steps = [
            "打开百度首页",
            "在搜索框中输入：测试",
            "点击搜索按钮",
            "等待2秒",
            "验证页面包含：测试结果"
        ]
        
        for step in steps:
            parsed = parser.parse(step)
            assert parsed is not None
            assert parsed.operation is not None
            assert parsed.raw == step
    
    def test_execution_logger_integration(self):
        """测试日志记录器集成"""
        logger = ExecutionLogger(headless=False, level='verbose')
        
        logger.log("测试消息", category='info')
        logger.log_step(1, "测试步骤")
        logger.log_success("成功消息")
        logger.log_error("错误消息")
        logger.log_warning("警告消息")
        
        logs = logger.get_logs()
        
        assert len(logs) == 5
        assert any("测试消息" in log for log in logs)
        assert any("步骤 1" in log for log in logs)
        assert any("成功消息" in log for log in logs)
        assert any("错误消息" in log for log in logs)
        assert any("警告消息" in log for log in logs)
    
    def test_retry_strategy_integration(self):
        """测试重试策略集成"""
        retry = RetryStrategy(max_retries=3, base_delay=0.1, backoff=2.0)
        
        call_count = [0]
        
        def failing_action():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("临时失败")
            return "成功"
        
        result = retry.execute_with_retry(failing_action, "测试操作")
        
        assert result.success == True
        assert result.result == "成功"
        assert result.attempts == 3
        assert call_count[0] == 3


def test_executor_basic_functionality():
    """测试执行器基本功能"""
    executor = OptimizedTestExecutor(headless=True, log_level='normal')
    
    assert executor is not None
    assert executor.headless == True
    assert executor.log_level == 'normal'
    
    result = ExecutionResult(
        execution_id="basic-test",
        testcase_id=1,
        testcase_name="基本功能测试"
    )
    
    executor.execution_results["basic-test"] = result
    
    retrieved = executor.get_execution_result("basic-test")
    
    assert retrieved is not None
    assert retrieved['execution_id'] == "basic-test"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
