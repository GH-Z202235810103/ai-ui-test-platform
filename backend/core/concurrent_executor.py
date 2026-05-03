import uuid
import threading
import queue
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class BatchResult:
    total: int
    passed: int
    failed: int
    errors: int
    duration: float
    details: List[Dict] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0


class BrowserPool:
    def __init__(self, pool_size: int = 3):
        self.pool_size = pool_size
        self._pool: queue.Queue = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialized = False
    
    def initialize(self, headless: bool = True):
        with self._lock:
            if self._initialized:
                return
            for _ in range(self.pool_size):
                self._pool.put(None)
            self._initialized = True
    
    def acquire(self, timeout: int = 30) -> Any:
        try:
            return self._pool.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError("Browser pool exhausted")
    
    def release(self, driver: Any):
        self._pool.put(driver)
    
    def cleanup(self):
        with self._lock:
            while not self._pool.empty():
                try:
                    driver = self._pool.get_nowait()
                    if driver:
                        driver.quit()
                except Exception:
                    pass


class ConcurrentExecutor:
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.results: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def execute_single(self, testcase: Dict, execution_id: str, headless: bool = True) -> Dict:
        from core.executor import run_playwright_sync
        
        self.results[execution_id] = {
            'status': 'running',
            'execution_id': execution_id,
            'testcase_id': testcase.get('id'),
            'testcase_name': testcase.get('name'),
            'start_time': datetime.now().isoformat(),
        }
        
        try:
            result = run_playwright_sync(testcase, headless)
            
            with self._lock:
                self.results[execution_id] = {
                    'status': 'passed' if result.get('success') else 'failed',
                    'execution_id': execution_id,
                    'testcase_id': testcase.get('id'),
                    'testcase_name': testcase.get('name'),
                    'start_time': result.get('start_time'),
                    'end_time': result.get('end_time'),
                    'duration': result.get('duration'),
                    'execution_log': result.get('execution_log', []),
                    'screenshots': result.get('screenshots', []),
                    'error': result.get('error'),
                    'success': result.get('success'),
                }
            
            return self.results[execution_id]
            
        except Exception as e:
            with self._lock:
                self.results[execution_id] = {
                    'status': 'error',
                    'execution_id': execution_id,
                    'testcase_id': testcase.get('id'),
                    'error': str(e),
                    'success': False,
                }
            return self.results[execution_id]
    
    def execute_batch(self, testcases: List[Dict], headless: bool = True) -> BatchResult:
        start_time = datetime.now()
        details = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for tc in testcases:
                execution_id = str(uuid.uuid4())
                future = executor.submit(
                    self.execute_single,
                    tc, execution_id, headless
                )
                futures[future] = execution_id
            
            for future in as_completed(futures):
                execution_id = futures[future]
                try:
                    result = future.result()
                    details.append(result)
                except Exception as e:
                    details.append({
                        'status': 'error',
                        'execution_id': execution_id,
                        'error': str(e),
                    })
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        passed = sum(1 for d in details if d.get('status') == 'passed')
        failed = sum(1 for d in details if d.get('status') == 'failed')
        errors = sum(1 for d in details if d.get('status') == 'error')
        
        return BatchResult(
            total=len(testcases),
            passed=passed,
            failed=failed,
            errors=errors,
            duration=duration,
            details=details,
        )
    
    def get_result(self, execution_id: str) -> Optional[Dict]:
        return self.results.get(execution_id)
    
    def clear_results(self):
        with self._lock:
            self.results.clear()
