"""
测试优化后的执行引擎

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

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.executor_optimized import (
    OptimizedTestExecutor,
    ExecutionResult,
    execute_testcase_sync,
    execute_testcase_async
)
from database import SessionLocal, TestReport, ReportStep, init_database


class TestOptimizedExecutor:
    """测试优化后的执行器"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前准备"""
        init_database()
        self.executor = OptimizedTestExecutor(
            headless=True, 
            log_level='verbose',
            timeout=30,
            retry_count=3,
            screenshot_quality=80
        )
        
        self.testcase = {
            "id": 999,
            "name": "测试用例",
            "description": "这是一个测试用例",
            "url": "https://www.baidu.com",
            "steps": [
                "打开百度首页",
                "在搜索框中输入：测试关键词",
                "点击搜索按钮",
                "等待2秒",
                "验证页面包含：测试"
            ]
        }
    
    def test_executor_initialization(self):
        """测试执行器初始化"""
        assert self.executor is not None
        assert self.executor.headless == True
        assert self.executor.log_level == 'verbose'
        assert self.executor.timeout == 30
        assert self.executor.retry_count == 3
        assert self.executor.screenshot_quality == 80
        assert isinstance(self.executor.execution_results, dict)
    
    def test_execution_result_creation(self):
        """测试执行结果对象创建"""
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
    
    def test_execution_result_to_dict(self):
        """测试执行结果转换为字典"""
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
        assert 'execution_log' in result_dict
        assert 'screenshots' in result_dict
    
    def test_execute_testcase_sync(self):
        """测试同步执行测试用例"""
        result = execute_testcase_sync(
            testcase=self.testcase,
            headless=True,
            save_to_db=False,
            log_level='normal',
            timeout=30,
            retry_count=3,
            screenshot_quality=80
        )
        
        assert isinstance(result, dict)
        assert 'execution_id' in result
        assert 'testcase_id' in result
        assert 'testcase_name' in result
        assert 'status' in result
        assert 'execution_log' in result
        assert 'screenshots' in result
        assert 'steps' in result
        
        assert result['testcase_id'] == 999
        assert result['testcase_name'] == "测试用例"
        assert isinstance(result['execution_log'], list)
        assert len(result['execution_log']) > 0
    
    @pytest.mark.asyncio
    async def test_execute_testcase_async(self):
        """测试异步执行测试用例"""
        result = await execute_testcase_async(
            testcase=self.testcase,
            headless=True,
            save_to_db=False,
            log_level='normal'
        )
        
        assert isinstance(result, dict)
        assert 'execution_id' in result
        assert 'status' in result
        assert result['testcase_id'] == 999
    
    def test_database_persistence(self):
        """测试数据库持久化功能"""
        result = execute_testcase_sync(
            testcase=self.testcase,
            headless=True,
            save_to_db=True,
            log_level='normal'
        )
        
        db = None
        try:
            db = SessionLocal()
            
            reports = db.query(TestReport).filter(
                TestReport.summary['testcase_id'].as_integer() == 999
            ).all()
            
            assert len(reports) > 0
            
            report = reports[-1]
            
            assert report.summary is not None
            assert report.summary.get('testcase_name') == "测试用例"
            assert report.status in ['passed', 'failed']
            
            steps = db.query(ReportStep).filter(
                ReportStep.report_id == report.id
            ).all()
            
            assert len(steps) > 0
            
        finally:
            if db:
                db.close()
    
    def test_error_handling(self):
        """测试错误处理功能"""
        invalid_testcase = {
            "id": 998,
            "name": "错误测试用例",
            "url": "https://invalid-url-that-does-not-exist.com",
            "steps": [
                "打开页面",
                "执行不存在的操作"
            ]
        }
        
        result = execute_testcase_sync(
            testcase=invalid_testcase,
            headless=True,
            save_to_db=False,
            log_level='normal'
        )
        
        assert isinstance(result, dict)
        assert 'error' in result
        assert result['error'] is not None or result['status'] == 'failed'
    
    def test_screenshot_capture(self):
        """测试截图功能"""
        result = execute_testcase_sync(
            testcase=self.testcase,
            headless=True,
            save_to_db=False,
            log_level='normal'
        )
        
        assert isinstance(result['screenshots'], list)
        
        if len(result['screenshots']) > 0:
            screenshot_dir = Path(__file__).parent.parent.parent / "screenshots"
            for screenshot in result['screenshots']:
                screenshot_path = screenshot_dir / screenshot
                if screenshot_path.exists():
                    assert screenshot_path.stat().st_size > 0
    
    def test_step_execution(self):
        """测试步骤执行功能"""
        result = execute_testcase_sync(
            testcase=self.testcase,
            headless=True,
            save_to_db=False,
            log_level='verbose'
        )
        
        assert isinstance(result['steps'], list)
        assert len(result['steps']) > 0
        
        for step in result['steps']:
            assert 'step_index' in step
            assert 'step_desc' in step
            assert 'success' in step
            assert 'start_time' in step
            assert 'end_time' in step
    
    def test_execution_logger_integration(self):
        """测试日志记录器集成"""
        result = execute_testcase_sync(
            testcase=self.testcase,
            headless=True,
            save_to_db=False,
            log_level='verbose'
        )
        
        assert len(result['execution_log']) > 0
        
        log_str = '\n'.join(result['execution_log'])
        
        assert '开始执行' in log_str or '步骤' in log_str


def test_convenience_functions():
    """测试便捷函数"""
    testcase = {
        "id": 997,
        "name": "便捷函数测试",
        "url": "https://www.baidu.com",
        "steps": ["打开百度首页"]
    }
    
    result = execute_testcase_sync(
        testcase=testcase,
        headless=True,
        save_to_db=False
    )
    
    assert isinstance(result, dict)
    assert result['testcase_id'] == 997


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
