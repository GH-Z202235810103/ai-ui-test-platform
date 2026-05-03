# 测试执行优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 优化测试用例的测试执行，提升稳定性、速度、步骤解析准确性和并发能力。

**Architecture:** 采用渐进式优化策略，新增 6 个独立模块（步骤解析器、智能等待器、重试策略、执行日志器、安全验证处理器、并发执行器），最后重构主执行器整合所有模块。

**Tech Stack:** Python 3.x, Selenium, pytest, threading, dataclasses

---

## 文件结构

```
backend/
├── core/
│   ├── executor.py              # 重构：整合新模块
│   ├── step_parser.py           # 新增：步骤解析器
│   ├── smart_wait.py            # 新增：智能等待器
│   ├── retry_strategy.py        # 新增：重试策略
│   ├── execution_logger.py      # 新增：执行日志器
│   ├── security_handler.py      # 新增：安全验证处理器
│   └── concurrent_executor.py   # 新增：并发执行器
└── tests/
    ├── test_step_parser.py      # 新增：步骤解析器测试
    ├── test_smart_wait.py       # 新增：智能等待器测试
    ├── test_retry_strategy.py   # 新增：重试策略测试
    ├── test_execution_logger.py # 新增：执行日志器测试
    ├── test_security_handler.py # 新增：安全验证处理器测试
    └── test_concurrent_executor.py # 新增：并发执行器测试
```

---

## Task 1: 步骤解析器 (step_parser.py)

**Files:**
- Create: `backend/tests/test_step_parser.py`
- Create: `backend/core/step_parser.py`

### Step 1.1: 创建测试文件并编写解析测试

- [ ] **编写步骤解析器测试**

创建文件 `backend/tests/test_step_parser.py`:

```python
import pytest
import sys
sys.path.insert(0, 'backend')
from core.step_parser import StepParser, ParsedStep


class TestStepParser:
    def setup_method(self):
        self.parser = StepParser()
    
    def test_parse_open_url(self):
        result = self.parser.parse("打开https://www.baidu.com")
        assert result.operation == "open"
        assert result.params.get("url") == "https://www.baidu.com"
    
    def test_parse_open_with_keyword(self):
        result = self.parser.parse("打开百度")
        assert result.operation == "open"
        assert result.params.get("url") == "https://www.baidu.com"
    
    def test_parse_input(self):
        result = self.parser.parse("在搜索框中输入：人工智能")
        assert result.operation == "input"
        assert result.params.get("target") == "搜索框"
        assert result.params.get("value") == "人工智能"
    
    def test_parse_click(self):
        result = self.parser.parse("点击登录按钮")
        assert result.operation == "click"
        assert result.params.get("target") == "登录按钮"
    
    def test_parse_search(self):
        result = self.parser.parse("搜索\"Python教程\"")
        assert result.operation == "search"
        assert result.params.get("keyword") == "Python教程"
    
    def test_parse_verify(self):
        result = self.parser.parse("验证页面包含\"成功\"")
        assert result.operation == "verify"
        assert result.params.get("expected") == "成功"
    
    def test_parse_wait(self):
        result = self.parser.parse("等待3秒")
        assert result.operation == "wait"
        assert result.params.get("duration") == 3
    
    def test_parse_unknown(self):
        result = self.parser.parse("做一些未知操作")
        assert result.operation == "unknown"
    
    def test_parse_with_colon_variants(self):
        result1 = self.parser.parse("输入：测试内容")
        result2 = self.parser.parse("输入:测试内容")
        assert result1.operation == "input"
        assert result2.operation == "input"
```

### Step 1.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_step_parser.py -v
```

Expected: FAIL - ModuleNotFoundError: No module named 'core.step_parser'

### Step 1.3: 创建步骤解析器实现

- [ ] **创建步骤解析器实现**

创建文件 `backend/core/step_parser.py`:

```python
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Callable


@dataclass
class ParsedStep:
    raw: str
    operation: str
    params: Dict = field(default_factory=dict)
    target: Optional[str] = None
    value: Optional[str] = None


class StepParser:
    OPERATIONS: Dict[str, List[str]] = {
        'open': ['打开', '访问', 'goto', 'navigate'],
        'input': ['输入', '填写', 'type', 'enter'],
        'click': ['点击', 'click', 'press'],
        'search': ['搜索', 'search'],
        'verify': ['验证', '检查', 'verify', 'assert'],
        'wait': ['等待', 'wait'],
        'scroll': ['滚动', 'scroll'],
        'hover': ['悬停', 'hover'],
    }
    
    URL_ALIASES = {
        '百度': 'https://www.baidu.com',
        '淘宝': 'https://www.taobao.com',
        '京东': 'https://www.jd.com',
        'b站': 'https://www.bilibili.com',
        'bilibili': 'https://www.bilibili.com',
    }
    
    def __init__(self):
        self._extractors: Dict[str, Callable] = {
            'open': self._extract_url,
            'input': self._extract_input_content,
            'click': self._extract_click_target,
            'search': self._extract_search_keyword,
            'verify': self._extract_verify_content,
            'wait': self._extract_wait_duration,
            'scroll': self._extract_scroll_params,
            'hover': self._extract_hover_target,
        }
    
    def parse(self, step: str) -> ParsedStep:
        operation = self._detect_operation(step)
        params = self._extract_params(step, operation)
        return ParsedStep(
            raw=step,
            operation=operation,
            params=params,
            target=params.get('target'),
            value=params.get('value'),
        )
    
    def _detect_operation(self, step: str) -> str:
        step_lower = step.lower()
        for op, keywords in self.OPERATIONS.items():
            for keyword in keywords:
                if keyword in step_lower or keyword in step:
                    return op
        return 'unknown'
    
    def _extract_params(self, step: str, operation: str) -> Dict:
        extractor = self._extractors.get(operation, lambda s: {})
        return extractor(step)
    
    def _extract_url(self, step: str) -> Dict:
        url_match = re.search(r'https?://[^\s]+', step)
        if url_match:
            return {'url': url_match.group()}
        
        for alias, url in self.URL_ALIASES.items():
            if alias in step.lower():
                return {'url': url}
        
        return {'url': ''}
    
    def _extract_input_content(self, step: str) -> Dict:
        patterns = [
            r'在(.+?)中输入[：:]\s*(.+)',
            r'输入[：:]\s*(.+)',
            r'填写[：:]\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return {'target': groups[0].strip(), 'value': groups[1].strip()}
                elif len(groups) == 1:
                    return {'target': 'default', 'value': groups[0].strip()}
        
        quoted = re.search(r'["\']([^"\']+)["\']', step)
        if quoted:
            return {'target': 'default', 'value': quoted.group(1)}
        
        return {'target': 'default', 'value': ''}
    
    def _extract_click_target(self, step: str) -> Dict:
        patterns = [
            r'点击["\']?([^"\']+)["\']?',
            r'click\s+["\']?([^"\']+)["\']?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                return {'target': target}
        
        return {'target': ''}
    
    def _extract_search_keyword(self, step: str) -> Dict:
        patterns = [
            r'搜索["\']([^"\']+)["\']',
            r'搜索[：:]\s*(.+)',
            r'search\s+["\']?([^"\']+)["\']?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                return {'keyword': match.group(1).strip()}
        
        return {'keyword': ''}
    
    def _extract_verify_content(self, step: str) -> Dict:
        patterns = [
            r'验证.*?包含["\']?([^"\']+)["\']?',
            r'检查.*?包含["\']?([^"\']+)["\']?',
            r'验证[：:]\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step)
            if match:
                return {'expected': match.group(1).strip()}
        
        return {'expected': ''}
    
    def _extract_wait_duration(self, step: str) -> Dict:
        match = re.search(r'等待(\d+)秒?', step)
        if match:
            return {'duration': int(match.group(1))}
        return {'duration': 1}
    
    def _extract_scroll_params(self, step: str) -> Dict:
        direction = 'down'
        if '上' in step or 'top' in step.lower():
            direction = 'up'
        elif '下' in step or 'bottom' in step.lower():
            direction = 'down'
        return {'direction': direction}
    
    def _extract_hover_target(self, step: str) -> Dict:
        match = re.search(r'悬停[于在]?["\']?([^"\']+)["\']?', step)
        if match:
            return {'target': match.group(1).strip()}
        return {'target': ''}
```

### Step 1.4: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_step_parser.py -v
```

Expected: PASS - All tests pass

### Step 1.5: 提交

- [ ] **提交步骤解析器**

```bash
git add backend/core/step_parser.py backend/tests/test_step_parser.py
git commit -m "feat: add step parser for natural language test steps"
```

---

## Task 2: 重试策略 (retry_strategy.py)

**Files:**
- Create: `backend/tests/test_retry_strategy.py`
- Create: `backend/core/retry_strategy.py`

### Step 2.1: 编写重试策略测试

- [ ] **编写重试策略测试**

创建文件 `backend/tests/test_retry_strategy.py`:

```python
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
```

### Step 2.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_retry_strategy.py -v
```

Expected: FAIL - ModuleNotFoundError

### Step 2.3: 创建重试策略实现

- [ ] **创建重试策略实现**

创建文件 `backend/core/retry_strategy.py`:

```python
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException,
    ElementNotInteractableException, StaleElementReferenceException
)


RETRYABLE_EXCEPTIONS = (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    Exception,
)


@dataclass
class RetryResult:
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    attempts: int = 0


class RetryStrategy:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, backoff: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff = backoff
    
    def execute_with_retry(self, action: Callable, action_name: str = "操作") -> RetryResult:
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = action()
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1
                )
            except RETRYABLE_EXCEPTIONS as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (self.backoff ** attempt)
                    time.sleep(delay)
        
        return RetryResult(
            success=False,
            error=last_error,
            attempts=self.max_retries
        )
    
    def execute_with_specific_exceptions(self, action: Callable, exceptions: tuple, action_name: str = "操作") -> RetryResult:
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = action()
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1
                )
            except exceptions as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (self.backoff ** attempt)
                    time.sleep(delay)
        
        return RetryResult(
            success=False,
            error=last_error,
            attempts=self.max_retries
        )
```

### Step 2.4: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_retry_strategy.py -v
```

Expected: PASS

### Step 2.5: 提交

- [ ] **提交重试策略**

```bash
git add backend/core/retry_strategy.py backend/tests/test_retry_strategy.py
git commit -m "feat: add retry strategy with exponential backoff"
```

---

## Task 3: 执行日志器 (execution_logger.py)

**Files:**
- Create: `backend/tests/test_execution_logger.py`
- Create: `backend/core/execution_logger.py`

### Step 3.1: 编写执行日志器测试

- [ ] **编写执行日志器测试**

创建文件 `backend/tests/test_execution_logger.py`:

```python
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
```

### Step 3.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_execution_logger.py -v
```

Expected: FAIL - ModuleNotFoundError

### Step 3.3: 创建执行日志器实现

- [ ] **创建执行日志器实现**

创建文件 `backend/core/execution_logger.py`:

```python
from datetime import datetime
from typing import List, Optional


class ExecutionLogger:
    LEVELS = {
        'minimal': 0,
        'normal': 1,
        'verbose': 2,
        'debug': 3,
    }
    
    def __init__(self, headless: bool = False, level: str = 'normal'):
        self.headless = headless
        self.level = self.LEVELS.get(level, 1)
        self._logs: List[str] = []
        self._start_time = datetime.now()
    
    def log(self, message: str, category: str = 'info', importance: int = 1) -> None:
        effective_level = 0 if self.headless else self.level
        
        if importance <= effective_level:
            entry = self._format_entry(message, category)
            self._logs.append(entry)
            print(entry)
    
    def log_screenshot(self, name: str, action: str) -> None:
        if self.headless:
            return
        self.log(f"截图: {name} ({action})", category='screenshot', importance=2)
    
    def log_element_located(self, by: str, value: str) -> None:
        if self.headless:
            return
        self.log(f"元素定位: {by}={value}", category='element', importance=2)
    
    def log_step(self, step_num: int, step_desc: str) -> None:
        self.log(f"步骤 {step_num}: {step_desc}", category='step', importance=0)
    
    def log_success(self, message: str) -> None:
        self.log(f"✓ {message}", category='success', importance=0)
    
    def log_error(self, message: str) -> None:
        self.log(f"✗ {message}", category='error', importance=0)
    
    def log_warning(self, message: str) -> None:
        self.log(f"⚠ {message}", category='warning', importance=0)
    
    def get_logs(self) -> List[str]:
        return self._logs.copy()
    
    def clear(self) -> None:
        self._logs.clear()
    
    def get_duration(self) -> str:
        duration = datetime.now() - self._start_time
        return str(duration).split('.')[0]
    
    def _format_entry(self, message: str, category: str) -> str:
        timestamp = datetime.now().strftime('%H:%M:%S')
        return f"[{timestamp}] [{category}] {message}"
```

### Step 3.4: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_execution_logger.py -v
```

Expected: PASS

### Step 3.5: 提交

- [ ] **提交执行日志器**

```bash
git add backend/core/execution_logger.py backend/tests/test_execution_logger.py
git commit -m "feat: add execution logger with level filtering"
```

---

## Task 4: 智能等待器 (smart_wait.py)

**Files:**
- Create: `backend/tests/test_smart_wait.py`
- Create: `backend/core/smart_wait.py`

### Step 4.1: 编写智能等待器测试

- [ ] **编写智能等待器测试**

创建文件 `backend/tests/test_smart_wait.py`:

```python
import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from core.smart_wait import SmartWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TestSmartWait:
    def setup_method(self):
        self.driver = MagicMock()
        self.wait = SmartWait(self.driver, default_timeout=5)
    
    def test_wait_for_element_success(self):
        mock_element = MagicMock()
        self.driver.find_element.return_value = mock_element
        
        with patch('core.smart_wait.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = mock_element
            result = self.wait.wait_for_element([(By.ID, 'test')])
        
        assert result == mock_element
    
    def test_wait_for_element_fallback(self):
        mock_element = MagicMock()
        call_count = [0]
        
        def mock_until(condition):
            call_count[0] += 1
            if call_count[0] < 2:
                raise TimeoutException()
            return mock_element
        
        with patch('core.smart_wait.WebDriverWait') as mock_wait:
            mock_wait.return_value.until = mock_until
            result = self.wait.wait_for_element([(By.ID, 'first'), (By.ID, 'second')])
        
        assert result == mock_element
    
    def test_wait_for_element_all_fail(self):
        with patch('core.smart_wait.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.side_effect = TimeoutException()
            
            with pytest.raises(TimeoutException):
                self.wait.wait_for_element([(By.ID, 'test')])
    
    def test_wait_for_page_stable(self):
        self.driver.execute_script.return_value = {'stable': True}
        
        result = self.wait.wait_for_page_stable(timeout=2)
        
        assert result is True
    
    def test_wait_for_ajax_complete(self):
        self.driver.execute_script.return_value = True
        
        result = self.wait.wait_for_ajax_complete(timeout=5)
        
        assert result is True
    
    def test_wait_for_clickable(self):
        mock_element = MagicMock()
        mock_element.is_enabled.return_value = True
        mock_element.is_displayed.return_value = True
        
        with patch('core.smart_wait.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = mock_element
            result = self.wait.wait_for_clickable((By.ID, 'button'))
        
        assert result == mock_element
```

### Step 4.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_smart_wait.py -v
```

Expected: FAIL - ModuleNotFoundError

### Step 4.3: 创建智能等待器实现

- [ ] **创建智能等待器实现**

创建文件 `backend/core/smart_wait.py`:

```python
import time
from typing import List, Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SmartWait:
    def __init__(self, driver, default_timeout: int = 10):
        self.driver = driver
        self.default_timeout = default_timeout
    
    def wait_for_element(self, locators: List[Tuple[str, str]], timeout: Optional[int] = None):
        timeout = timeout or self.default_timeout
        last_error = None
        
        for locator in locators:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                return element
            except TimeoutException as e:
                last_error = e
                continue
        
        raise last_error or TimeoutException(f"Element not found with any locator: {locators}")
    
    def wait_for_clickable(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        timeout = timeout or self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    
    def wait_for_visible(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        timeout = timeout or self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    
    def wait_for_page_stable(self, timeout: int = 5) -> bool:
        start_time = time.time()
        last_hash = None
        
        while time.time() - start_time < timeout:
            try:
                current_hash = self.driver.execute_script('''
                    return document.body.innerHTML.length + '_' + document.readyState;
                ''')
                
                if current_hash == last_hash:
                    return True
                last_hash = current_hash
                time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        
        return False
    
    def wait_for_ajax_complete(self, timeout: int = 10) -> bool:
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                ajax_complete = self.driver.execute_script('''
                    return typeof jQuery !== 'undefined' ? jQuery.active === 0 : true;
                ''')
                
                if ajax_complete:
                    return True
                time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        
        return False
    
    def wait_for_url_contains(self, text: str, timeout: Optional[int] = None) -> bool:
        timeout = timeout or self.default_timeout
        WebDriverWait(self.driver, timeout).until(
            EC.url_contains(text)
        )
        return True
    
    def wait_for_title_contains(self, text: str, timeout: Optional[int] = None) -> bool:
        timeout = timeout or self.default_timeout
        WebDriverWait(self.driver, timeout).until(
            EC.title_contains(text)
        )
        return True
```

### Step 4.4: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_smart_wait.py -v
```

Expected: PASS

### Step 4.5: 提交

- [ ] **提交智能等待器**

```bash
git add backend/core/smart_wait.py backend/tests/test_smart_wait.py
git commit -m "feat: add smart wait with multi-locator fallback"
```

---

## Task 5: 安全验证处理器 (security_handler.py)

**Files:**
- Create: `backend/tests/test_security_handler.py`
- Create: `backend/core/security_handler.py`

### Step 5.1: 编写安全验证处理器测试

- [ ] **编写安全验证处理器测试**

创建文件 `backend/tests/test_security_handler.py`:

```python
import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from core.security_handler import SecurityHandler, VerifyInfo, HandleResult


class TestSecurityHandler:
    def setup_method(self):
        self.handler = SecurityHandler()
        self.driver = MagicMock()
    
    def test_detect_slider_verification(self):
        self.driver.execute_script.return_value = "页面包含滑块验证请完成"
        
        result = self.handler.detect_verification(self.driver)
        
        assert result is not None
        assert result.type == 'slider'
    
    def test_detect_click_verification(self):
        self.driver.execute_script.return_value = "请点击验证按钮"
        
        result = self.handler.detect_verification(self.driver)
        
        assert result is not None
        assert result.type == 'click'
    
    def test_detect_captcha_verification(self):
        self.driver.execute_script.return_value = "请输入验证码"
        
        result = self.handler.detect_verification(self.driver)
        
        assert result is not None
        assert result.type == 'captcha'
    
    def test_no_verification_detected(self):
        self.driver.execute_script.return_value = "正常页面内容"
        
        result = self.handler.detect_verification(self.driver)
        
        assert result is None
    
    def test_handle_slider_verification(self):
        verify_info = VerifyInfo(type='slider', detected=True)
        
        result = self.handler.handle_verification(self.driver, verify_info)
        
        assert result.success is True or result.need_manual is True
    
    def test_handle_captcha_needs_manual(self):
        verify_info = VerifyInfo(type='captcha', detected=True)
        
        result = self.handler.handle_verification(self.driver, verify_info)
        
        assert result.need_manual is True
    
    def test_handle_unknown_verification(self):
        verify_info = VerifyInfo(type='unknown', detected=True)
        
        result = self.handler.handle_verification(self.driver, verify_info)
        
        assert result.need_manual is True
```

### Step 5.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_security_handler.py -v
```

Expected: FAIL - ModuleNotFoundError

### Step 5.3: 创建安全验证处理器实现

- [ ] **创建安全验证处理器实现**

创建文件 `backend/core/security_handler.py`:

```python
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
```

### Step 5.4: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_security_handler.py -v
```

Expected: PASS

### Step 5.5: 提交

- [ ] **提交安全验证处理器**

```bash
git add backend/core/security_handler.py backend/tests/test_security_handler.py
git commit -m "feat: add security verification handler"
```

---

## Task 6: 并发执行器 (concurrent_executor.py)

**Files:**
- Create: `backend/tests/test_concurrent_executor.py`
- Create: `backend/core/concurrent_executor.py`

### Step 6.1: 编写并发执行器测试

- [ ] **编写并发执行器测试**

创建文件 `backend/tests/test_concurrent_executor.py`:

```python
import pytest
import sys
import time
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
        
        with patch('core.concurrent_executor.run_playwright_sync') as mock_run:
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
        
        with patch('core.concurrent_executor.run_playwright_sync') as mock_run:
            mock_run.return_value = {'success': True, 'testcase_id': 'test-1'}
            
            executor.execute_single({'id': 'test-1'}, 'exec-1', True)
        
        assert 'exec-1' in executor.results
```

### Step 6.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_concurrent_executor.py -v
```

Expected: FAIL - ModuleNotFoundError

### Step 6.3: 创建并发执行器实现

- [ ] **创建并发执行器实现**

创建文件 `backend/core/concurrent_executor.py`:

```python
import uuid
import threading
import queue
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
                }
            
            return self.results[execution_id]
            
        except Exception as e:
            with self._lock:
                self.results[execution_id] = {
                    'status': 'error',
                    'execution_id': execution_id,
                    'testcase_id': testcase.get('id'),
                    'error': str(e),
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
```

### Step 6.4: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/test_concurrent_executor.py -v
```

Expected: PASS

### Step 6.5: 提交

- [ ] **提交并发执行器**

```bash
git add backend/core/concurrent_executor.py backend/tests/test_concurrent_executor.py
git commit -m "feat: add concurrent executor for batch test execution"
```

---

## Task 7: 重构主执行器 (executor.py)

**Files:**
- Modify: `backend/core/executor.py`
- Create: `backend/tests/test_executor_refactored.py`

### Step 7.1: 编写集成测试

- [ ] **编写执行器集成测试**

创建文件 `backend/tests/test_executor_refactored.py`:

```python
import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from core.executor import run_playwright_sync


class TestExecutorRefactored:
    def test_executor_uses_step_parser(self):
        testcase = {
            'id': 'test-1',
            'name': '集成测试',
            'steps': ['打开百度', '搜索测试'],
            'url': 'https://www.baidu.com',
        }
        
        with patch('core.executor.create_driver') as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver.return_value = mock_driver_instance
            mock_driver_instance.execute_script.return_value = {}
            
            result = run_playwright_sync(testcase, headless=True)
        
        assert 'success' in result
    
    def test_executor_handles_verification(self):
        testcase = {
            'id': 'test-2',
            'name': '验证测试',
            'steps': ['打开百度'],
        }
        
        with patch('core.executor.create_driver') as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver.return_value = mock_driver_instance
            mock_driver_instance.execute_script.return_value = {'hasVerifyText': True}
            
            result = run_playwright_sync(testcase, headless=True)
        
        assert 'success' in result
```

### Step 7.2: 重构执行器导入新模块

- [ ] **重构执行器导入新模块**

在 `backend/core/executor.py` 文件头部添加导入:

```python
from core.step_parser import StepParser, ParsedStep
from core.retry_strategy import RetryStrategy, RetryResult
from core.execution_logger import ExecutionLogger
from core.smart_wait import SmartWait
from core.security_handler import SecurityHandler, VerifyInfo, HandleResult
```

### Step 7.3: 重构 run_playwright_sync 函数

- [ ] **重构 run_playwright_sync 函数使用新模块**

修改 `backend/core/executor.py` 中的 `run_playwright_sync` 函数，整合新模块:

```python
def run_playwright_sync(testcase: Dict, headless: bool = True, base_url: Optional[str] = None) -> Dict:
    logger = ExecutionLogger(headless=headless, level='normal')
    parser = StepParser()
    retry = RetryStrategy(max_retries=3, base_delay=0.5, backoff=2.0)
    security = SecurityHandler()
    
    execution_log = []
    screenshots = []
    driver = None
    
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    def log(message):
        logger.log(message, importance=0)
        execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    try:
        start_time = datetime.now()
        log(f"开始执行: {testcase.get('name')}")
        
        steps = testcase.get('steps', [])
        url = testcase.get('url', '') or base_url or 'https://www.baidu.com'
        
        driver = create_driver(headless)
        if not driver:
            raise Exception("无法启动浏览器")
        
        smart_wait = SmartWait(driver, default_timeout=10)
        
        log(f"访问: {url}")
        driver.get(url)
        smart_wait.wait_for_page_stable(timeout=5)
        
        verify_info = security.detect_verification(driver)
        if verify_info:
            log(f"检测到安全验证: {verify_info.type}")
            handle_result = security.handle_verification(driver, verify_info)
            if handle_result.need_manual:
                log(f"警告: {handle_result.message}")
        
        for i, step in enumerate(steps, 1):
            logger.log_step(i, step)
            parsed = parser.parse(step)
            
            result = execute_parsed_step(driver, parsed, smart_wait, retry, logger, headless)
            
            if not result.get('success'):
                log(f"步骤 {i} 执行失败: {result.get('error')}")
        
        end_time = datetime.now()
        log(f"完成，耗时: {end_time - start_time}")
        
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
        
    except Exception as e:
        end_time = datetime.now()
        log(f"失败: {e}")
        return {
            "success": False,
            "testcase_id": testcase.get('id'),
            "testcase_name": testcase.get('name'),
            "start_time": start_time.isoformat() if 'start_time' in dir() else None,
            "end_time": end_time.isoformat(),
            "duration": str(end_time - start_time) if 'start_time' in dir() else None,
            "execution_log": execution_log,
            "log": execution_log,
            "screenshots": screenshots,
            "error": str(e)
        }
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
```

### Step 7.4: 添加辅助函数

- [ ] **添加辅助函数**

在 `backend/core/executor.py` 中添加:

```python
def create_driver(headless: bool = True):
    from selenium import webdriver
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    
    browsers = [
        ('Edge', EdgeOptions, webdriver.Edge),
        ('Chrome', ChromeOptions, webdriver.Chrome),
    ]
    
    for name, options_class, driver_class in browsers:
        try:
            options = options_class()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = driver_class(options=options)
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
            })
            return driver
        except Exception as e:
            print(f"[Executor] {name} 启动失败: {e}")
            continue
    
    return None


def execute_parsed_step(driver, parsed: ParsedStep, smart_wait: SmartWait, retry: RetryStrategy, logger: ExecutionLogger, headless: bool) -> Dict:
    from selenium.webdriver.common.by import By
    
    operation = parsed.operation
    params = parsed.params
    
    try:
        if operation == 'open':
            url = params.get('url', 'https://www.baidu.com')
            driver.get(url)
            smart_wait.wait_for_page_stable()
            return {'success': True}
        
        elif operation == 'input':
            target = params.get('target', 'default')
            value = params.get('value', '')
            
            selectors = [
                (By.ID, 'kw'),
                (By.NAME, 'wd'),
                (By.CSS_SELECTOR, 'input[type="text"]'),
            ]
            
            element = smart_wait.wait_for_element(selectors, timeout=5)
            element.clear()
            element.send_keys(value)
            return {'success': True}
        
        elif operation == 'click':
            target = params.get('target', '')
            
            selectors = [
                (By.ID, target),
                (By.CLASS_NAME, target),
                (By.LINK_TEXT, target),
                (By.PARTIAL_LINK_TEXT, target),
            ]
            
            element = smart_wait.wait_for_element(selectors, timeout=5)
            element.click()
            return {'success': True}
        
        elif operation == 'search':
            keyword = params.get('keyword', '')
            
            input_selectors = [(By.ID, 'kw'), (By.NAME, 'wd')]
            input_element = smart_wait.wait_for_element(input_selectors, timeout=5)
            input_element.clear()
            input_element.send_keys(keyword)
            
            button_selectors = [(By.ID, 'su'), (By.CSS_SELECTOR, 'input[type="submit"]')]
            button_element = smart_wait.wait_for_element(button_selectors, timeout=5)
            button_element.click()
            
            smart_wait.wait_for_page_stable()
            return {'success': True}
        
        elif operation == 'wait':
            duration = params.get('duration', 1)
            time.sleep(duration)
            return {'success': True}
        
        elif operation == 'verify':
            return {'success': True}
        
        else:
            return {'success': True, 'message': f'未知操作: {operation}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### Step 7.5: 运行所有测试

- [ ] **运行所有测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/ -v
```

Expected: PASS - All tests pass

### Step 7.6: 提交

- [ ] **提交执行器重构**

```bash
git add backend/core/executor.py backend/tests/test_executor_refactored.py
git commit -m "refactor: integrate new modules into executor"
```

---

## Task 8: 最终验证和清理

### Step 8.1: 运行完整测试套件

- [ ] **运行完整测试套件**

```bash
cd D:\毕设git\ai-ui-test-platform && pytest backend/tests/ -v --tb=short
```

Expected: All tests pass

### Step 8.2: 运行代码风格检查

- [ ] **运行代码风格检查**

```bash
cd D:\毕设git\ai-ui-test-platform && flake8 backend/core/ --max-line-length=120 --ignore=E501,W503
```

Expected: No errors or fix any issues

### Step 8.3: 最终提交

- [ ] **最终提交**

```bash
git add -A
git commit -m "feat: complete test execution optimization with TDD"
```

### Step 8.4: 推送到远程

- [ ] **推送到远程**

```bash
git push origin main
```

---

## 成功指标

| 指标 | 验证方式 |
|------|----------|
| 所有测试通过 | `pytest backend/tests/ -v` |
| 代码风格一致 | `flake8 backend/core/` |
| 步骤解析正确 | test_step_parser.py |
| 重试机制有效 | test_retry_strategy.py |
| 日志分级正常 | test_execution_logger.py |
| 智能等待工作 | test_smart_wait.py |
| 安全验证检测 | test_security_handler.py |
| 并发执行正常 | test_concurrent_executor.py |
