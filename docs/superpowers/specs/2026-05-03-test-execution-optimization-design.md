# 测试执行优化设计文档

**日期**: 2026-05-03
**方案**: 渐进式优化
**优先级**: 稳定性优先

---

## 1. 概述

### 1.1 目标
优化测试用例的测试执行，提升执行稳定性、速度、步骤解析准确性和并发能力。

### 1.2 优化范围
- 执行速度
- 执行稳定性（优先）
- 步骤解析
- 并发执行
- 日志简化

### 1.3 稳定性问题
- 安全验证拦截
- 元素定位失败
- 等待时间不足
- 步骤解析不准确

---

## 2. 架构设计

### 2.1 模块结构

```
backend/core/
├── executor.py          # 主执行器（重构）
├── smart_wait.py        # 智能等待器（新增）
├── retry_strategy.py    # 重试策略（新增）
├── step_parser.py       # 步骤解析器（新增）
├── execution_logger.py  # 执行日志器（新增）
├── security_handler.py  # 安全验证处理（新增）
└── concurrent_executor.py # 并发执行器（新增）
```

### 2.2 数据流

```
测试用例 → 步骤解析器 → 操作队列
                ↓
        并发执行器（可选）
                ↓
        ┌───────────────────┐
        │   单步执行循环    │
        │  ┌─────────────┐  │
        │  │ 智能等待    │  │
        │  │     ↓       │  │
        │  │ 重试策略    │  │
        │  │     ↓       │  │
        │  │ 安全验证检测│  │
        │  │     ↓       │  │
        │  │ 执行操作    │  │
        │  │     ↓       │  │
        │  │ 日志记录    │  │
        │  └─────────────┘  │
        └───────────────────┘
                ↓
           执行结果
```

---

## 3. 模块详细设计

### 3.1 智能等待器 (smart_wait.py)

**职责**: 动态等待元素和页面状态

**核心类**:
```python
class SmartWait:
    def __init__(self, driver, default_timeout=10)
    def wait_for_element(self, locators: List[tuple], timeout=None) -> Element
    def wait_for_page_stable(self, timeout=5)
    def wait_for_ajax_complete(self, timeout=10)
    def wait_for_clickable(self, locator: tuple, timeout=None) -> Element
```

**特性**:
- 多定位器回退：一个定位器失败后自动尝试下一个
- 页面稳定检测：等待 DOM 不再变化
- AJAX 完成：等待异步请求完成
- 可配置超时：不同操作可设置不同超时时间

### 3.2 重试策略 (retry_strategy.py)

**职责**: 操作失败时自动重试

**核心类**:
```python
@dataclass
class RetryResult:
    success: bool
    result: Any
    error: Exception
    attempts: int

class RetryStrategy:
    def __init__(self, max_retries=3, base_delay=1.0, backoff=2.0)
    def execute_with_retry(self, action: Callable, action_name: str) -> RetryResult
```

**重试层级**:

| 层级 | 场景 | 重试次数 | 延迟策略 |
|------|------|----------|----------|
| 元素定位 | 找不到元素 | 3次 | 指数退避 |
| 元素交互 | 点击/输入失败 | 2次 | 固定延迟 |
| 页面加载 | 超时 | 2次 | 线性递增 |
| 安全验证 | 检测到验证 | 1次 | 等待5秒 |

### 3.3 步骤解析器 (step_parser.py)

**职责**: 解析自然语言测试步骤

**核心类**:
```python
@dataclass
class ParsedStep:
    raw: str
    operation: str
    params: dict
    target: Optional[str]
    value: Optional[str]

class StepParser:
    OPERATIONS = {
        'open': ['打开', '访问', 'goto', 'navigate'],
        'input': ['输入', '填写', 'type', 'enter'],
        'click': ['点击', 'click', 'press'],
        'search': ['搜索', 'search'],
        'verify': ['验证', '检查', 'verify', 'assert'],
        'wait': ['等待', 'wait'],
        'scroll': ['滚动', 'scroll'],
        'hover': ['悬停', 'hover'],
    }
    
    def parse(self, step: str) -> ParsedStep
    def _detect_operation(self, step: str) -> str
    def _extract_params(self, step: str, operation: str) -> dict
```

**支持的步骤格式**:

| 操作类型 | 示例步骤 | 解析结果 |
|----------|----------|----------|
| 打开 | `打开https://www.baidu.com` | `{operation: 'open', url: '...'}` |
| 输入 | `在搜索框中输入：人工智能` | `{operation: 'input', target: '搜索框', value: '人工智能'}` |
| 点击 | `点击登录按钮` | `{operation: 'click', target: '登录按钮'}` |
| 搜索 | `搜索"Python教程"` | `{operation: 'search', keyword: 'Python教程'}` |
| 验证 | `验证页面包含"成功"` | `{operation: 'verify', expected: '成功'}` |
| 等待 | `等待3秒` | `{operation: 'wait', duration: 3}` |

### 3.4 执行日志器 (execution_logger.py)

**职责**: 分级日志记录

**核心类**:
```python
class ExecutionLogger:
    LEVELS = {
        'minimal': 0,    # 仅关键信息
        'normal': 1,     # 常规信息
        'verbose': 2,    # 详细信息
        'debug': 3,      # 调试信息
    }
    
    def __init__(self, headless: bool = False, level: str = 'normal')
    def log(self, message: str, category: str = 'info', importance: int = 1)
    def log_screenshot(self, name: str, action: str)
    def log_element_located(self, by: str, value: str)
    def get_logs(self) -> List[str]
```

**日志级别**:

| 级别 | 输出内容 | 适用场景 |
|------|----------|----------|
| minimal | 成功/失败/错误 | 生产环境、CI/CD |
| normal | + 步骤执行、关键操作 | 日常测试 |
| verbose | + 元素定位、等待详情 | 问题排查 |
| debug | + 截图描述、DOM检测 | 开发调试 |

**无头模式优化**:
- 自动使用 minimal 级别
- 跳过截图描述
- 跳过元素定位详情
- 跳过等待信息

### 3.5 安全验证处理器 (security_handler.py)

**职责**: 检测和处理安全验证

**核心类**:
```python
@dataclass
class VerifyInfo:
    type: str
    detected: bool
    element: Optional[Element] = None

@dataclass
class HandleResult:
    success: bool
    need_manual: bool
    message: str

class SecurityHandler:
    VERIFY_PATTERNS = {
        'slider': ['滑块验证', '拖动滑块', 'slider'],
        'click': ['点击验证', '请点击', 'click to verify'],
        'image': ['图片验证', '选择包含', 'select images'],
        'captcha': ['验证码', 'captcha', '输入验证码'],
    }
    
    def detect_verification(self, driver) -> Optional[VerifyInfo]
    def handle_verification(self, driver, verify_info: VerifyInfo) -> HandleResult
```

**处理策略**:

| 验证类型 | 自动处理 | 等待时间 | 失败后 |
|----------|----------|----------|--------|
| 滑块验证 | 是 | 5秒 | 标记需人工 |
| 点击验证 | 是 | 3秒 | 标记需人工 |
| 图片验证 | 否 | - | 标记需人工 |
| 验证码 | 否 | - | 标记需人工 |
| 未知类型 | 否 | - | 标记需人工 |

### 3.6 并发执行器 (concurrent_executor.py)

**职责**: 批量并发执行测试用例

**核心类**:
```python
@dataclass
class BatchResult:
    total: int
    passed: int
    failed: int
    errors: int
    duration: timedelta
    details: List[Dict]
    
    @property
    def success_rate(self) -> float

class BrowserPool:
    def __init__(self, pool_size: int = 3)
    def acquire(self, timeout: int = 30) -> WebDriver
    def release(self, driver: WebDriver)

class ConcurrentExecutor:
    def __init__(self, max_workers: int = 3)
    async def execute_batch(self, testcases: List[Dict], headless: bool) -> BatchResult
```

**并发控制**:

| 参数 | 默认值 | 说明 |
|------|--------|------|
| max_workers | 3 | 最大并发数 |
| browser_pool_size | 3 | 浏览器实例池大小 |
| timeout | 300s | 单个测试超时时间 |

---

## 4. 执行器重构

### 4.1 主执行器改造

将 `executor.py` 中的 `run_playwright_sync` 函数重构为使用新模块：

```python
def run_playwright_sync(testcase: Dict, headless: bool = True, base_url: Optional[str] = None) -> Dict:
    logger = ExecutionLogger(headless=headless, level='normal')
    smart_wait = SmartWait(driver)
    retry = RetryStrategy()
    security = SecurityHandler()
    parser = StepParser()
    
    for step in steps:
        parsed = parser.parse(step)
        
        # 安全验证检测
        verify_info = security.detect_verification(driver)
        if verify_info:
            result = security.handle_verification(driver, verify_info)
            if result.need_manual:
                logger.log(f"需要人工处理验证: {verify_info.type}")
        
        # 执行操作（带重试）
        retry.execute_with_retry(
            lambda: execute_operation(driver, parsed, smart_wait),
            f"步骤: {step}"
        )
```

---

## 5. 测试策略

### 5.1 单元测试

| 模块 | 测试重点 |
|------|----------|
| step_parser | 步骤解析正确性、边界情况 |
| smart_wait | 等待超时、元素定位 |
| retry_strategy | 重试次数、延迟计算 |
| execution_logger | 日志级别过滤 |
| security_handler | 验证检测、处理结果 |

### 5.2 集成测试

- 完整测试用例执行流程
- 并发执行正确性
- 错误恢复能力

### 5.3 端到端测试

- 百度搜索测试用例
- 多步骤复杂场景
- 安全验证触发场景

---

## 6. 实施计划

### 阶段 1: 核心模块（优先）
1. step_parser.py - 步骤解析器
2. smart_wait.py - 智能等待器
3. retry_strategy.py - 重试策略

### 阶段 2: 增强模块
4. execution_logger.py - 执行日志器
5. security_handler.py - 安全验证处理器

### 阶段 3: 高级功能
6. concurrent_executor.py - 并发执行器
7. executor.py 重构 - 整合所有模块

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 重构引入新 bug | 高 | TDD 开发，充分测试 |
| 并发资源竞争 | 中 | 浏览器池、线程锁 |
| 安全验证误判 | 低 | 多模式检测、人工确认 |

---

## 8. 成功指标

| 指标 | 当前值 | 目标值 |
|------|--------|--------|
| 测试成功率 | ~70% | >90% |
| 平均执行时间 | 基准 | 减少 20% |
| 元素定位成功率 | ~80% | >95% |
| 日志体积 | 基准 | 减少 50%（无头模式） |
