import pytest
import sys
sys.path.insert(0, 'backend')
from core.execution_logger import ExecutionLogger


class TestExecutionLogger:
    def test_log_normal_level(self):
        logger = ExecutionLogger(headless=False, level='normal')
        logger.log("测试消息", importance=1)
        
        assert len(logger.get_logs()) == 1
        assert "测试消息" in logger.get_logs()[0]
    
    def test_log_filtered_by_importance(self):
        logger = ExecutionLogger(headless=False, level='normal')
        logger.log("重要消息", importance=1)
        logger.log("次要消息", importance=2)
        
        logs = logger.get_logs()
        assert len(logs) == 1
        assert "重要消息" in logs[0]
    
    def test_headless_mode_reduces_logs(self):
        logger = ExecutionLogger(headless=True, level='normal')
        logger.log("关键信息", importance=0)
        logger.log("详细信息", importance=2)
        
        logs = logger.get_logs()
        assert len(logs) == 1
        assert "关键信息" in logs[0]
    
    def test_minimal_level_only_critical(self):
        logger = ExecutionLogger(headless=False, level='minimal')
        logger.log("成功", importance=0)
        logger.log("步骤", importance=1)
        
        logs = logger.get_logs()
        assert len(logs) == 1
    
    def test_verbose_level_shows_more(self):
        logger = ExecutionLogger(headless=False, level='verbose')
        logger.log("关键", importance=0)
        logger.log("普通", importance=1)
        logger.log("详细", importance=2)
        
        logs = logger.get_logs()
        assert len(logs) == 3
    
    def test_log_screenshot_in_normal_mode(self):
        logger = ExecutionLogger(headless=False, level='normal')
        logger.log_screenshot("test.png", "测试截图")
        
        logs = logger.get_logs()
        assert len(logs) == 1
        assert "test.png" in logs[0]
    
    def test_log_screenshot_skipped_in_headless(self):
        logger = ExecutionLogger(headless=True, level='normal')
        logger.log_screenshot("test.png", "测试截图")
        
        logs = logger.get_logs()
        assert len(logs) == 0
    
    def test_log_element_located(self):
        logger = ExecutionLogger(headless=False, level='verbose')
        logger.log_element_located("ID", "kw")
        
        logs = logger.get_logs()
        assert len(logs) == 1
        assert "ID" in logs[0] and "kw" in logs[0]
    
    def test_log_element_located_skipped_in_headless(self):
        logger = ExecutionLogger(headless=True, level='verbose')
        logger.log_element_located("ID", "kw")
        
        logs = logger.get_logs()
        assert len(logs) == 0
    
    def test_clear_logs(self):
        logger = ExecutionLogger(headless=False, level='normal')
        logger.log("消息1")
        logger.log("消息2")
        
        assert len(logger.get_logs()) == 2
        logger.clear()
        assert len(logger.get_logs()) == 0
