import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from core.concurrent_executor import ConcurrentExecutor, BatchResult


class TestConcurrentExecutor:
    def setup_method(self):
        self.executor = ConcurrentExecutor(max_workers=2)
    
    def test_execute_single_testcase(self):
        mock_testcase = {
            'id': 'test-1',
            'name': '测试用例1',
            'steps': ['打开百度', '搜索测试'],
        }
        
        with patch('core.executor.run_playwright_sync') as mock_run:
            mock_run.return_value = {
                'success': True,
                'testcase_id': 'test-1',
                'execution_log': [],
                'screenshots': [],
            }
            
            result = self.executor.execute_single(mock_testcase, 'exec-1', True)
        
        assert result['success'] is True
    
    def test_batch_result_aggregation(self):
        results = [
            {'success': True, 'testcase_id': '1'},
            {'success': True, 'testcase_id': '2'},
            {'success': False, 'testcase_id': '3'},
        ]
        
        batch_result = BatchResult(
            total=3,
            passed=2,
            failed=1,
            errors=0,
            duration=10.0,
            details=results
        )
        
        assert batch_result.total == 3
        assert batch_result.passed == 2
        assert batch_result.failed == 1
        assert batch_result.success_rate == pytest.approx(0.667, rel=0.01)
    
    def test_max_workers_limit(self):
        executor = ConcurrentExecutor(max_workers=2)
        
        assert executor.max_workers == 2
    
    def test_execution_result_storage(self):
        executor = ConcurrentExecutor(max_workers=2)
        
        with patch('core.executor.run_playwright_sync') as mock_run:
            mock_run.return_value = {'success': True, 'testcase_id': 'test-1'}
            
            executor.execute_single({'id': 'test-1'}, 'exec-1', True)
        
        assert 'exec-1' in executor.results
