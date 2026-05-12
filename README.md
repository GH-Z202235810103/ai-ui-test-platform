# ai-ui-test-platform

本科毕业设计项目。本项目旨在开发一个智能化的UI自动化测试平台，通过集成计算机视觉(CV)进行辅助定位，并利用大语言模型(LLM)生成测试用例，以显著提升测试脚本的鲁棒性和开发效率，为中小型团队提供一套低成本、高可用的解决方案。

# 🤖 AI UI自动化测试平台

基于AI与行为驱动的UI自动化测试平台 - 完整可运行的成品

## 📋 项目概述

这是一个功能完整的AI UI自动化测试平台，集成了以下核心功能：

### ✨ 核心功能

1. **智能录制回放模块** (论文第3.1节)
   - 基于Playwright的无侵入式Web操作录制
   - 多策略元素定位机制（CSS选择器、XPath、文本内容、视觉定位）
   - 智能等待和错误重试机制
   - 回放成功率：97%
2. **AI视觉定位模块** (论文第3.2节)
   - 基于OpenCV的计算机视觉定位
   - 多尺度模板匹配算法（0.8-1.2倍缩放）
   - 动态阈值评估和被动学习机制
   - 定位成功率：94%
3. **自然语言用例生成模块** (论文第3.3节)
   - 基于大语言模型的测试用例生成
   - 优化的提示工程模板
   - 生成质量保障机制
   - 生成结果直接可用率：84%
4. **完整的数据模型设计** (论文第2.4节)
   - 项目管理表 (projects)
   - 测试用例表 (test\_cases)
   - 测试任务表 (test\_tasks)
   - 测试报告表 (test\_reports)
   - 视觉元素特征表 (visual\_elements)
   - 录制操作表 (recorded\_actions)
5. **完整的API接口设计** (论文第2.5节)
   - 项目管理接口
   - 测试用例接口
   - AI服务接口
   - 测试执行接口
   - 测试报告接口

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- Windows 10/11、macOS 或 Linux
- Chrome、Firefox 或 Edge 浏览器
- 至少 4GB 内存
- 至少 10GB 磁盘空间

### 2. 安装依赖

```bash
# 安装后端依赖
pip install -r backend/requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 验证安装
playwright install --check
```

### 3. 配置系统

#### 3.1 环境变量配置

创建 `.env` 文件（可选）：

```env
# 服务器配置
API_HOST=0.0.0.0
API_PORT=8001
API_PREFIX=/api

# 跨域配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8001,http://127.0.0.1:8001

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# 数据库配置
DATABASE_URL=sqlite:///ai_test_platform.db

# LLM配置（可选）
LLM_API_KEY=your_api_key
LLM_MODEL=deepseek-chat
```

#### 3.2 目录结构配置

系统会自动创建以下目录：

- `backend/screenshots/` - 存储测试截图
- `backend/visual_templates/` - 存储视觉元素模板
- `backend/logs/` - 存储系统日志

### 4. 启动系统

```bash
# 使用一键启动脚本（推荐）
python start_server_new.py

# 或手动启动
cd backend
python app.py
```

启动脚本会自动：

- ✅ 检查依赖包
- ✅ 安装Playwright浏览器
- ✅ 创建必要目录
- ✅ 初始化数据库
- ✅ 启动后端服务
- ✅ 打开前端页面

### 5. 访问系统

启动成功后，系统会自动打开浏览器，你也可以手动访问：

- **前端页面**: <http://localhost:3000/>
- **后端API文档**: <http://localhost:8001/docs>
- **系统状态**: <http://localhost:8001/api/v2/statistics>
- **健康检查**: <http://localhost:8001/health>

## 📖 使用说明

### 基础功能

1. **查看测试用例**
   - 页面加载后自动显示5个演示测试用例
   - 点击测试用例可以查看详细信息
2. **执行测试用例**
   - 选择测试用例后点击"开始执行测试"按钮
   - 查看实时执行日志和测试结果
   - 查看测试截图了解执行情况
3. **AI智能生成测试用例**
   - 在左侧"AI智能生成测试"区域输入自然语言描述
   - 例如："测试百度搜索'人工智能'的功能，验证搜索结果的相关性和准确性"
   - 点击"生成测试用例"按钮
   - 系统会自动生成结构化的测试用例
4. **智能录制回放**
   - 输入目标URL，选择录制模式
   - 点击"开始录制"按钮
   - 在打开的浏览器中执行操作
   - 点击"停止录制"按钮保存操作
   - 点击"回放录制"按钮执行录制的操作
5. **AI视觉定位**
   - 在"AI视觉定位"模块上传元素模板
   - 保存视觉模板到系统
   - 使用上传的截图进行元素定位测试

## 📚 API文档

### 1. 测试用例管理

#### 获取所有测试用例

- **URL**: `/api/testcases`
- **方法**: GET
- **响应**:
  ```json
  [
    {
      "id": "demo_1",
      "name": "百度搜索功能测试",
      "description": "自动化测试百度搜索功能",
      "steps": ["打开百度首页", "输入搜索关键词", "点击搜索按钮", "验证搜索结果"],
      "status": "pending",
      "created_at": "2024-01-01T12:00:00"
    }
  ]
  ```

#### 创建测试用例

- **URL**: `/api/testcases`
- **方法**: POST
- **请求体**:
  ```json
  {
    "name": "测试名称",
    "description": "测试描述",
    "steps": ["步骤1", "步骤2", "步骤3"]
  }
  ```

### 2. AI生成测试用例

#### 自然语言生成测试用例

- **URL**: `/api/generate-from-nlp`
- **方法**: POST
- **请求体**:
  ```json
  {
    "description": "测试百度搜索'人工智能'的功能"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "original_description": "测试百度搜索'人工智能'的功能",
    "ai_generated": {
      "test_case_name": "百度搜索功能测试",
      "test_steps": ["打开百度首页", "输入'人工智能'", "点击搜索按钮", "验证搜索结果"]
    },
    "bound_steps": [...]
  }
  ```

### 3. 测试执行

#### 执行测试用例

- **URL**: `/api/execute`
- **方法**: POST
- **请求体**:
  ```json
  {
    "test_case_id": 1,
    "headless": true,
    "base_url": "https://www.baidu.com"
  }
  ```

#### 执行Playwright测试

- **URL**: `/api/execute-playwright`
- **方法**: POST
- **请求体**:
  ```json
  {
    "testcase_id": "demo_1",
    "browser": "chromium",
    "headless": false
  }
  ```

#### 获取执行结果

- **URL**: `/api/execution/{execution_id}`
- **方法**: GET
- **响应**:
  ```json
  {
    "success": true,
    "execution_id": "exec_20240101_120000",
    "testcase_name": "百度搜索功能测试",
    "status": "passed",
    "duration": "3.2s",
    "log": ["执行步骤1", "执行步骤2"],
    "screenshots": ["screenshot_1.png", "screenshot_2.png"]
  }
  ```

### 4. 录制回放

#### 开始录制

- **URL**: `/api/recording/start`
- **方法**: POST
- **请求体**:
  ```json
  {
    "url": "https://www.baidu.com",
    "headless": false
  }
  ```

#### 停止录制

- **URL**: `/api/recording/stop`
- **方法**: POST
- **请求体**:
  ```json
  {
    "session_id": "session_123"
  }
  ```

#### 回放录制

- **URL**: `/api/recording/replay`
- **方法**: POST
- **请求体**:
  ```json
  {
    "session_id": "session_123",
    "url": "https://www.baidu.com",
    "actions": [...],
    "headless": true
  }
  ```

### 5. 视觉定位

#### 获取视觉模板列表

- **URL**: `/api/visual/templates`
- **方法**: GET

#### 创建视觉模板

- **URL**: `/api/visual/templates`
- **方法**: POST
- **请求体**: 表单数据
  - `file`: 模板图片文件
  - `element_name`: 元素名称
  - `element_type`: 元素类型

#### 获取视觉模板

- **URL**: `/api/visual/templates/{name}`
- **方法**: GET

#### 删除视觉模板

- **URL**: `/api/visual/templates/{name}`
- **方法**: DELETE

### 6. 系统管理

#### 健康检查

- **URL**: `/health`
- **方法**: GET
- **响应**:
  ```json
  {
    "status": "healthy",
    "service": "ai-ui-test-platform",
    "version": "1.0.0"
  }
  ```

#### 调试信息

- **URL**: `/api/debug`
- **方法**: GET

### 7. 性能优化建议

#### 大文件处理优化

- **文件上传限制**: 单个文件不超过10MB
- **图片处理**: 使用OpenCV进行压缩和优化
- **存储策略**: 定期清理过期的截图和模板

#### 并发请求优化

- **异步处理**: 使用FastAPI的异步特性
- **线程池**: 合理使用线程池处理IO密集型任务
- **请求限流**: 实现请求速率限制，防止系统过载

## 🔧 部署指南

### 1. 开发环境部署

```bash
# 克隆代码
git clone https://github.com/yourusername/ai-ui-test-platform.git
cd ai-ui-test-platform

# 安装依赖
pip install -r backend/requirements.txt
playwright install chromium

# 启动开发服务器
python start_server_new.py
```

### 2. 生产环境部署

#### 使用Gunicorn + Uvicorn

```bash
# 安装生产依赖
pip install gunicorn uvicorn[standard]

# 启动生产服务器
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app:app --bind 0.0.0.0:8001
```

#### 使用Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .

EXPOSE 8001

CMD ["python", "start_server_new.py"]
```

构建和运行:

```bash
docker build -t ai-ui-test-platform .
docker run -p 8001:8001 ai-ui-test-platform
```

### 3. 配置管理

#### 环境变量

| 变量名           | 说明       | 默认值                             |
| ------------- | -------- | ------------------------------- |
| API\_HOST     | 服务器主机    | 0.0.0.0                         |
| API\_PORT     | 服务器端口    | 8001                            |
| API\_PREFIX   | API前缀    | /api                            |
| CORS\_ORIGINS | 允许的跨域来源  | <http://localhost:3000>         |
| LOG\_LEVEL    | 日志级别     | INFO                            |
| DATABASE\_URL | 数据库连接URL | sqlite:///ai\_test\_platform.db |

#### 配置文件

所有配置项都可以在 `backend/config.py` 中修改：

```python
# 服务器配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
API_PREFIX = os.getenv("API_PREFIX", "/api")

# 跨域配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai_test_platform.db")
```

## 🧪 测试覆盖

### 测试用例示例

#### 基础测试用例

1. **百度搜索功能测试**
   - 步骤1: 打开百度首页
   - 步骤2: 输入搜索关键词"人工智能"
   - 步骤3: 点击搜索按钮
   - 步骤4: 验证搜索结果页面加载
2. **用户登录流程测试**
   - 步骤1: 访问登录页面
   - 步骤2: 输入用户名和密码
   - 步骤3: 点击登录按钮
   - 步骤4: 验证登录成功后的页面
3. **电商商品搜索测试**
   - 步骤1: 打开电商首页
   - 步骤2: 搜索商品关键词
   - 步骤3: 使用价格筛选
   - 步骤4: 查看商品详情

#### 边缘情况测试

1. **网络异常处理**
   - 测试目标: 验证系统在网络中断时的处理能力
   - 预期结果: 系统应该优雅处理网络异常，记录错误日志
2. **页面加载超时**
   - 测试目标: 验证系统在页面加载超时时的处理
   - 预期结果: 系统应该设置合理的超时时间，并提供友好的错误提示
3. **元素定位失败**
   - 测试目标: 验证系统在元素定位失败时的降级策略
   - 预期结果: 系统应该尝试多种定位策略，最终使用视觉定位
4. **大文件上传**
   - 测试目标: 验证系统处理大文件上传的能力
   - 预期结果: 系统应该限制文件大小，并提供合理的错误提示
5. **并发请求**
   - 测试目标: 验证系统处理并发请求的能力
   - 预期结果: 系统应该能够同时处理多个测试请求而不崩溃

### 测试执行流程

1. **准备测试环境**
   - 确保所有依赖已安装
   - 启动系统服务
2. **执行测试用例**
   - 使用前端界面执行测试
   - 或使用API接口执行测试
3. **验证测试结果**
   - 检查执行状态和日志
   - 查看测试截图
   - 验证测试报告
4. **分析测试数据**
   - 统计测试成功率
   - 分析失败原因
   - 优化测试用例

## 📊 性能指标

根据论文第4.3节对比实验结果：

| 指标     | 本系统  | Selenium | 提升幅度   |
| ------ | ---- | -------- | ------ |
| 脚本编写时间 | 22分钟 | 58分钟     | 62%    |
| 执行成功率  | 92%  | 63%      | 29个百分点 |
| 维护修复时间 | 8分钟  | 35分钟     | 77%    |

### 非功能性需求 (论文第2.1.2节)

- ✅ 界面响应时间：≤2秒
- ✅ 录制回放成功率：≥95%
- ✅ AI视觉定位响应：≤3秒
- ✅ 视觉定位准确率：≥85%
- ✅ 系统可用性：≥99%
- ✅ 数据持久化可靠性：≥99.9%

### 性能优化措施

1. **代码优化**
   - 使用异步编程提高并发处理能力
   - 优化数据库查询，减少不必要的操作
   - 使用缓存机制减少重复计算
2. **资源管理**
   - 合理使用线程池和进程池
   - 及时释放资源，避免内存泄漏
   - 优化文件IO操作
3. **系统配置**
   - 根据硬件资源调整服务器配置
   - 启用Gzip压缩减少网络传输
   - 配置合理的超时时间
4. **监控与调优**
   - 实现系统监控，及时发现性能瓶颈
   - 定期分析日志，优化系统参数
   - 根据实际使用情况调整配置

## 🏗️ 项目结构

```
ai-ui-test-platform/
├── backend/                    # 后端服务
│   ├── api/                  # API接口
│   │   ├── endpoints.py       # API端点实现
│   │   └── routes.py         # 路由配置
│   ├── core/                  # 核心模块
│   │   ├── recorder.py        # 智能录制回放
│   │   ├── visual_locator.py  # AI视觉定位
│   │   ├── nlp_generator.py   # 自然语言生成
│   │   ├── executor.py        # 测试执行器
│   │   └── screenshot.py      # 截图管理
│   ├── app.py                # FastAPI主程序
│   ├── db.py                 # 数据库管理
│   ├── config.py              # 配置文件
│   └── requirements.txt       # 依赖包
├── frontend/                   # 前端界面
│   ├── index.html            # 主页面
│   ├── app.js               # Vue应用
│   └── style.css            # 样式文件
├── screenshots/                # 测试截图
├── ai_test_platform.db         # SQLite数据库
├── start_server_new.py        # 一键启动脚本
└── README.md                 # 项目文档
```

## 🔧 技术栈

### 后端技术栈 (论文第2.3.2节)

- **开发语言**: Python 3.9+
- **Web框架**: FastAPI
- **测试框架**: Playwright
- **AI技术**: OpenCV (计算机视觉), LangChain (大语言模型集成)
- **数据存储**: SQLite (结构化数据), 文件系统 (截图和日志)

### 前端技术栈 (论文第2.3.2节)

- **开发框架**: Vue.js 3
- **UI组件库**: Bootstrap 5
- **状态管理**: Vue Composition API
- **图标库**: Font Awesome 6

## 📚️ 论文对应关系

本系统严格按照论文要求实现，各章节对应关系：

- **第2章 系统总体设计方案**: 完整实现
  - 2.1 系统需求分析 ✅
  - 2.2 系统架构设计 ✅
  - 2.3 技术选型与配置 ✅
  - 2.4 数据模型设计 ✅
  - 2.5 接口设计规范 ✅
  - 2.6 安全性设计 ✅
  - 2.7 部署架构设计 ✅
- **第3章 系统关键模块实现**: 完整实现
  - 3.1 智能录制回放模块 ✅
  - 3.2 AI视觉定位模块 ✅
  - 3.3 自然语言用例生成模块 ✅
  - 3.4 关键技术问题与解决方案 ✅
- **第4章 系统测试与验证**: 部分实现
  - 4.1 测试环境与测试对象 ✅
  - 4.2 功能测试结果 ✅
  - 4.3 对比实验 ✅
  - 4.4 用户接受度测试 ⚠️ (需实际用户测试)

## 🎯 创新点总结 (论文第5.2节)

1. **多策略视觉定位机制**
   - 针对动态页面元素难以定位的痛点
   - 基于OpenCV的多尺度模板匹配算法
   - 在传统定位失败时自动降级到视觉定位
   - 对界面小幅变化具有自适应能力
2. **自然语言驱动的用例生成**
   - 将大语言模型应用于测试用例生成
   - 设计了面向测试场景的提示工程模板
   - 实现了从自然语言描述到结构化测试脚本的半自动化转换
   - 大幅降低了脚本编写门槛
3. **轻量级一体化平台架构**
   - 采用前后端分离架构
   - 将录制回放、AI服务、测试管理等功能有机整合
   - 构建了一个开箱即用的测试平台
   - 完全开源免费，适合中小团队和个人开发者使用

## ⚠️ 已知限制 (论文第5.3节)

1. **视觉定位的局限性**
   - 当界面发生重大改版时，视觉定位准确率会大幅下降
   - 未来可考虑引入深度学习模型进行元素检测
2. **测试覆盖范围有限**
   - 目前主要支持Web端UI测试
   - 对移动端App的支持尚不完善
3. **生成质量有待进一步提升**
   - 大语言模型生成的测试用例在复杂业务场景下仍需人工调整
   - 未来可收集更多高质量用例进行模型微调
4. **并发执行能力不足**
   - 目前平台主要面向单机使用
   - 分布式任务调度功能尚不完善

## 🔮 未来展望

- [ ] 引入深度学习模型提升视觉定位能力
- [ ] 扩展移动端App测试支持
- [ ] 实现分布式任务调度和集群部署
- [ ] 集成更多大语言模型选项
- [ ] 添加测试报告导出功能
- [ ] 实现定时任务调度
- [ ] 添加用户权限管理

## 📄 许可证

本项目完全开源，遵循MIT许可证。

## 👨‍💻 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue: GitHub Issues
- 邮件联系: \[你的邮箱]

***

**🎉 感谢使用AI UI自动化测试平台！**
