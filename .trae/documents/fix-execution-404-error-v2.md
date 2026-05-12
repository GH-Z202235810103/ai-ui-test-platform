# 测试执行功能404错误修复计划

## 问题分析

### 核心问题
前端调用 `GET /api/v2/execution/{execution_id}` 时返回 404 错误，原因是执行结果无法被找到。

### 根本原因

1. **`endpoints.py` 第779行严重Bug**：
   ```python
   executor=executor  # executor 变量未定义！
   ```
   在 `/execute` 接口中，`executor` 变量被引用但从未定义。这会导致 `NameError`，线程执行失败，执行结果永远不会被存储。

2. **`executor_optimized.py` 缺少 `threading` 导入**：
   - 第87行使用了 `threading.Lock()`
   - 但文件头部没有 `import threading`
   - 这会导致 `NameError: name 'threading' is not defined`

3. **线程安全问题**：
   - `get_execution_result` 方法读取数据时没有使用锁保护
   - 可能导致并发读取问题

4. **执行结果存储时机问题**：
   - 执行结果在 `execute_testcase` 方法开始时存储
   - 但如果线程启动失败，结果永远不会被存储

## 修复方案

### 任务1：修复 `endpoints.py` 中的 executor 变量未定义问题

**文件**: `D:\毕设git\ai-ui-test-platform\backend\api\v2\endpoints.py`

**修改位置**: 第736-803行的 `api_execute_testcase` 函数

**修改内容**:
```python
@router.post("/execute")
async def api_execute_testcase(request: dict = Body(...), db: Session = Depends(get_db)):
    """执行测试用例"""
    # ... 现有代码 ...
    
    from core.executor_optimized import execute_testcase_sync
    import uuid
    import threading
    
    executor = get_executor()  # 添加这一行：获取全局执行器实例
    execution_id = str(uuid.uuid4())
    
    def run_in_thread():
        try:
            execute_testcase_sync(
                testcase=testcase_dict,
                headless=headless,
                save_to_db=save_to_db,
                log_level='normal',
                timeout=timeout,
                retry_count=retry_count,
                screenshot_quality=screenshot_quality,
                execution_id=execution_id,
                executor=executor  # 现在可以正确引用
            )
        except Exception as e:
            print(f"[执行错误] {e}")
    
    # ... 其余代码 ...
```

### 任务2：修复 `executor_optimized.py` 中缺少的 threading 导入

**文件**: `D:\毕设git\ai-ui-test-platform\backend\core\executor_optimized.py`

**修改位置**: 文件头部导入区域（第13-28行）

**修改内容**:
```python
import re
import uuid
import time
import threading  # 添加这一行
import traceback
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path
```

### 任务3：增强 `get_execution_result` 方法的线程安全性

**文件**: `D:\毕设git\ai-ui-test-platform\backend\core\executor_optimized.py`

**修改位置**: 第578-590行的 `get_execution_result` 方法

**修改内容**:
```python
def get_execution_result(self, execution_id: str) -> Optional[Dict]:
    """获取执行结果
    
    Args:
        execution_id: 执行ID
    
    Returns:
        Optional[Dict]: 执行结果字典，如果不存在返回 None
    """
    with self._lock:  # 添加锁保护
        result = self.execution_results.get(execution_id)
        if result:
            return result.to_dict()
    return None
```

### 任务4：添加执行结果的初始状态存储

**文件**: `D:\毕设git\ai-ui-test-platform\backend\api\v2\endpoints.py`

**修改位置**: `api_execute_testcase` 函数

**修改内容**: 在线程启动前，先存储一个初始状态的执行结果，确保前端可以立即查询到执行记录

```python
@router.post("/execute")
async def api_execute_testcase(request: dict = Body(...), db: Session = Depends(get_db)):
    # ... 现有代码 ...
    
    executor = get_executor()
    execution_id = str(uuid.uuid4())
    
    # 添加：在线程启动前存储初始状态
    from core.executor_optimized import ExecutionResult
    initial_result = ExecutionResult(
        execution_id=execution_id,
        testcase_id=testcase.id,
        testcase_name=testcase.name
    )
    initial_result.status = "pending"
    with executor._lock:
        executor.execution_results[execution_id] = initial_result
    
    def run_in_thread():
        # ... 现有代码 ...
    
    # ... 其余代码 ...
```

### 任务5：添加错误处理和日志记录

**文件**: `D:\毕设git\ai-ui-test-platform\backend\api\v2\endpoints.py`

**修改内容**: 在线程函数中添加更详细的错误处理

```python
def run_in_thread():
    try:
        execute_testcase_sync(
            testcase=testcase_dict,
            headless=headless,
            save_to_db=save_to_db,
            log_level='normal',
            timeout=timeout,
            retry_count=retry_count,
            screenshot_quality=screenshot_quality,
            execution_id=execution_id,
            executor=executor
        )
    except Exception as e:
        import traceback
        print(f"[执行错误] 执行ID: {execution_id}")
        print(f"[执行错误] 错误信息: {e}")
        print(f"[执行错误] 堆栈跟踪:\n{traceback.format_exc()}")
        
        # 更新执行结果为失败状态
        with executor._lock:
            if execution_id in executor.execution_results:
                result = executor.execution_results[execution_id]
                result.status = "failed"
                result.error = str(e)
```

### 任务6：优化批量执行接口

**文件**: `D:\毕设git\ai-ui-test-platform\backend\api\v2\endpoints.py`

**修改位置**: `api_execute_batch` 函数（第901-976行）

**修改内容**: 确保批量执行也使用全局执行器实例，并添加初始状态存储

## 验证步骤

1. **重启后端服务**
   - 停止当前运行的后端服务
   - 重新启动后端服务

2. **测试单个用例执行**
   - 在前端点击"执行"按钮
   - 观察执行进度对话框是否正常显示
   - 检查是否能正常轮询执行状态
   - 验证执行结果是否正确显示

3. **测试批量执行**
   - 选择多个测试用例
   - 点击批量执行
   - 验证每个用例的执行状态是否正确

4. **检查后端日志**
   - 确认没有 `NameError` 或其他异常
   - 确认执行器正确初始化
   - 确认执行结果正确存储

## 预期结果

- ✅ 执行测试用例时不再出现 404 错误
- ✅ 执行进度对话框能正常显示实时进度
- ✅ 执行日志和截图能正确加载
- ✅ 执行完成后能正确显示成功/失败状态
- ✅ 批量执行功能正常工作

## 风险评估

- **风险等级**: 低
- **影响范围**: 仅修改执行相关代码，不影响其他功能
- **回滚方案**: 如果出现问题，可以快速回滚到修改前的代码

## 实施顺序

1. 先修复 `executor_optimized.py` 的 threading 导入问题（任务2）
2. 再修复 `endpoints.py` 的 executor 变量未定义问题（任务1）
3. 增强 `get_execution_result` 的线程安全性（任务3）
4. 添加初始状态存储（任务4）
5. 添加错误处理和日志（任务5）
6. 优化批量执行接口（任务6）
7. 重启服务并验证
