import pytest
import sys
sys.path.insert(0, 'backend')

from unittest.mock import MagicMock, patch


class TestProgressCalculation:
    def test_progress_pending(self):
        from api.v2.endpoints import calculate_progress
        result = {"status": "pending"}
        assert calculate_progress(result) == 0
    
    def test_progress_running(self):
        from api.v2.endpoints import calculate_progress
        result = {"status": "running"}
        assert calculate_progress(result) == 50
    
    def test_progress_passed(self):
        from api.v2.endpoints import calculate_progress
        result = {"status": "passed"}
        assert calculate_progress(result) == 100
    
    def test_progress_failed(self):
        from api.v2.endpoints import calculate_progress
        result = {"status": "failed"}
        assert calculate_progress(result) == 100
    
    def test_progress_success(self):
        from api.v2.endpoints import calculate_progress
        result = {"status": "success"}
        assert calculate_progress(result) == 100
    
    def test_progress_unknown(self):
        from api.v2.endpoints import calculate_progress
        result = {"status": "unknown"}
        assert calculate_progress(result) == 0


class TestExecutorIntegration:
    def test_executor_initialization(self):
        from core.executor import TestExecutor
        executor = TestExecutor()
        assert executor.execution_results == {}
    
    @pytest.mark.asyncio
    async def test_executor_execute_testcase(self):
        from core.executor import TestExecutor
        executor = TestExecutor()
        
        mock_testcase = MagicMock()
        mock_testcase.id = 1
        mock_testcase.name = "测试用例1"
        mock_testcase.description = "测试描述"
        mock_testcase.script_data = {"steps": ["打开百度"], "url": "https://www.baidu.com"}
        mock_testcase.get_steps = MagicMock(return_value=["打开百度"])
        
        with patch('core.executor.run_playwright_sync') as mock_run:
            mock_run.return_value = {
                'success': True,
                'testcase_id': 1,
                'testcase_name': '测试用例1',
                'execution_log': ['步骤完成'],
                'screenshots': [],
                'start_time': '2026-05-10T10:00:00',
                'end_time': '2026-05-10T10:01:00',
                'duration': '60'
            }
            
            import uuid
            execution_id = str(uuid.uuid4())
            result = await executor.execute_testcase(mock_testcase, execution_id, True)
            
            assert result["status"] in ["running", "passed"]
            assert result["execution_id"] == execution_id
            assert result["testcase_id"] == 1
    
    @pytest.mark.asyncio
    async def test_executor_get_result(self):
        from core.executor import TestExecutor
        executor = TestExecutor()
        
        execution_id = "test-exec-id"
        executor.execution_results[execution_id] = {
            "status": "passed",
            "execution_id": execution_id,
            "testcase_id": 1,
            "testcase_name": "测试用例1",
            "start_time": "2026-05-10T10:00:00",
            "end_time": "2026-05-10T10:01:00",
            "duration": "60",
            "execution_log": ["步骤1完成"],
            "screenshots": []
        }
        
        result = await executor.get_execution_result(execution_id)
        
        assert result["status"] == "passed"
        assert result["testcase_id"] == 1
        assert len(result["execution_log"]) == 1
    
    @pytest.mark.asyncio
    async def test_executor_get_result_not_found(self):
        from core.executor import TestExecutor
        executor = TestExecutor()
        
        result = await executor.get_execution_result("invalid-id")
        
        assert result["status"] == "not_found"
        assert "error" in result


class TestAPIEndpoints:
    def test_api_execute_endpoint_exists(self):
        from api.v2.endpoints import router
        routes = [route.path for route in router.routes]
        assert "/execute" in routes
    
    def test_api_execution_result_endpoint_exists(self):
        from api.v2.endpoints import router
        routes = [route.path for route in router.routes]
        assert "/execution/{execution_id}" in routes
    
    def test_api_execution_status_endpoint_exists(self):
        from api.v2.endpoints import router
        routes = [route.path for route in router.routes]
        assert "/execution/{execution_id}/status" in routes
    
    def test_api_execution_logs_endpoint_exists(self):
        from api.v2.endpoints import router
        routes = [route.path for route in router.routes]
        assert "/execution/{execution_id}/logs" in routes
    
    def test_api_batch_execute_endpoint_exists(self):
        from api.v2.endpoints import router
        routes = [route.path for route in router.routes]
        assert "/execute/batch" in routes
