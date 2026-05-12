# Edge浏览器执行失败修复计划

## 问题分析

### 错误信息
```
Message: invalid argument
  (Session info: MicrosoftEdge=148.0.3967.54)
```

### 根本原因

1. **URL参数为空字符串**：
   - `endpoints.py` 第759行从 `testcase.script_data.get("url", "")` 获取URL
   - 如果 `script_data` 中没有 `url` 字段，返回空字符串 `""`
   - `executor_optimized.py` 第220行使用 `testcase.get('url', 'https://www.baidu.com')`
   - **关键问题**：空字符串 `""` 是有效值，不会触发默认值 `'https://www.baidu.com'`
   - `driver.get("")` 导致 "invalid argument" 错误

2. **测试用例数据结构问题**：
   - 测试用例的步骤描述包含URL（如"打开https://www.baidu.com"）
   - 但 `script_data` 字段可能没有 `url` 字段
   - 导致URL参数为空

## 修复方案

### 任务1：修复URL参数处理逻辑

**文件**: `D:\毕设git\ai-ui-test-platform\backend\core\executor_optimized.py`

**修改位置**: 第220行

**修改内容**:
```python
# 原代码
url = testcase.get('url', 'https://www.baidu.com')

# 修改为
url = testcase.get('url') or 'https://www.baidu.com'
```

**说明**: 使用 `or` 运算符，确保空字符串也会使用默认值

### 任务2：从步骤描述中提取URL

**文件**: `D:\毕设git\ai-ui-test-platform\backend\core\executor_optimized.py`

**修改位置**: 第218-220行

**修改内容**: 添加从步骤描述中提取URL的逻辑

```python
steps = testcase.get('steps', [])
url = testcase.get('url') or 'https://www.baidu.com'

# 如果URL为空，尝试从步骤描述中提取
if not url and steps:
    import re
    for step in steps:
        # 匹配 "打开https://..." 或 "打开 http://..." 等模式
        match = re.search(r'(https?://[^\s]+)', step)
        if match:
            url = match.group(1)
            break
```

### 任务3：增强URL验证

**文件**: `D:\毕设git\ai-ui-test-platform\backend\core\executor_optimized.py`

**修改位置**: 第220-223行

**修改内容**: 添加URL有效性验证

```python
url = testcase.get('url') or 'https://www.baidu.com'

# 从步骤描述中提取URL
if not url or url == 'https://www.baidu.com':
    if steps:
        import re
        for step in steps:
            match = re.search(r'(https?://[^\s]+)', step)
            if match:
                url = match.group(1)
                break

# 验证URL格式
if not url or not url.startswith(('http://', 'https://')):
    url = 'https://www.baidu.com'
    logger.log_warning(f"URL无效或为空，使用默认URL: {url}")
```

### 任务4：优化endpoints.py中的URL获取逻辑

**文件**: `D:\毕设git\ai-ui-test-platform\backend\api\v2\endpoints.py`

**修改位置**: 第759行

**修改内容**:
```python
# 原代码
"url": testcase.script_data.get("url", "") if hasattr(testcase, 'script_data') and testcase.script_data else ""

# 修改为
"url": testcase.script_data.get("url") if hasattr(testcase, 'script_data') and testcase.script_data and testcase.script_data.get("url") else None
```

**说明**: 返回 `None` 而不是空字符串，让executor使用默认值

### 任务5：添加更详细的错误日志

**文件**: `D:\毕设git\ai-ui-test-platform\backend\core\executor_optimized.py`

**修改位置**: execute_testcase方法

**修改内容**: 在driver.get(url)前后添加日志

```python
logger.log_step(0, f"访问页面: {url}")
try:
    driver.get(url)
    smart_wait.wait_for_page_stable(timeout=self.timeout)
except Exception as e:
    logger.log_error(f"访问页面失败: {url}, 错误: {e}")
    raise
```

## 验证步骤

1. **重启后端服务**
   - 停止当前运行的后端服务
   - 重新启动后端服务

2. **测试URL提取**
   - 执行"百度搜索功能测试"用例
   - 检查日志，确认URL正确提取为 `https://www.baidu.com`
   - 验证不再出现 "invalid argument" 错误

3. **测试默认URL**
   - 执行没有URL的测试用例
   - 确认使用默认URL `https://www.baidu.com`

4. **测试URL验证**
   - 测试无效URL的情况
   - 确认使用默认URL并记录警告日志

## 预期结果

- ✅ 不再出现 "invalid argument" 错误
- ✅ URL为空时正确使用默认值
- ✅ 能从步骤描述中提取URL
- ✅ 详细的错误日志便于调试

## 风险评估

- **风险等级**: 低
- **影响范围**: 仅修改URL处理逻辑，不影响其他功能
- **回滚方案**: 如果出现问题，可以快速回滚到修改前的代码

## 实施顺序

1. 修复URL参数处理逻辑（任务1）
2. 添加从步骤描述中提取URL的功能（任务2）
3. 增强URL验证（任务3）
4. 优化endpoints.py中的URL获取逻辑（任务4）
5. 添加详细的错误日志（任务5）
6. 重启服务并验证
