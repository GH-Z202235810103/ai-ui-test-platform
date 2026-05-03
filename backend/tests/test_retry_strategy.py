import pytest
import sys
import time
sys.path.insert(0, 'backend')
from core.retry_strategy import RetryStrategy, RetryResult


class TestRetryStrategy:
    def setup_method(self):
        self.strategy = RetryStrategy(max_retries=3, base_delay=0.1, backoff=2.0)
    
    def test_success_on_first_attempt(self):
        def successful_action():
            return "success"
        
        result = self.strategy.execute_with_retry(successful_action, "test")
        
        assert result.success is True
        assert result.result == "success"
        assert result.attempts == 1
    
    def test_success_on_second_attempt(self):
        call_count = [0]
        
        def eventually_succeed():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = self.strategy.execute_with_retry(eventually_succeed, "test")
        
        assert result.success is True
        assert result.attempts == 2
    
    def test_failure_after_max_retries(self):
        def always_fail():
            raise ValueError("Always fails")
        
        result = self.strategy.execute_with_retry(always_fail, "test")
        
        assert result.success is False
        assert result.attempts == 3
        assert isinstance(result.error, ValueError)
    
    def test_exponential_backoff_delay(self):
        strategy = RetryStrategy(max_retries=3, base_delay=0.1, backoff=2.0)
        
        call_times = []
        def track_calls():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("Not yet")
            return "done"
        
        start = time.time()
        result = strategy.execute_with_retry(track_calls, "test")
        elapsed = time.time() - start
        
        assert result.success is True
        assert elapsed >= 0.1 + 0.2
    
    def test_custom_retry_count(self):
        strategy = RetryStrategy(max_retries=5, base_delay=0.01, backoff=1.0)
        
        call_count = [0]
        def fail_four_times():
            call_count[0] += 1
            if call_count[0] < 5:
                raise Exception("Not yet")
            return "success"
        
        result = strategy.execute_with_retry(fail_four_times, "test")
        
        assert result.success is True
        assert result.attempts == 5
