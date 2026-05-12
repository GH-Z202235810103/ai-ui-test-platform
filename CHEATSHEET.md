# AI UI自动化测试平台 - 速查表

## 📋 项目信息

- **项目名称**: AI UI自动化测试平台
- **技术栈**: Python + FastAPI + Vue.js 3 + Element Plus + Playwright
- **后端端口**: 8001
- **前端端口**: 3000
- **数据库**: SQLite

## 🚀 常用命令

### 技能安装

```bash
# ===== Skills 安装 =====

# 安装 superpowers 技能包（包含 brainstorming, tdd, writing-plans 等）
npx skills add https://github.com/obra/superpowers.git --agent 'trae-cn'

# 安装 planning-with-files 技能（Manus风格持久化规划）
npx skills add https://github.com/OthmanAdi/planning-with-files --agent 'trae-cn'

# 安装 UI UX Pro Max 技能（专业UI/UX设计智能）
npx skills add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --agent 'trae-cn'

# ===== Plugins 安装 =====

# 安装 code-review 插件（代码审查）
npx skills add https://github.com/anthropics/claude-code-plugins --agent 'trae-cn' --skill code-review

# 安装 code-simplifier 插件（代码简化）
npx skills add https://github.com/anthropics/claude-code-plugins --agent 'trae-cn' --skill code-simplifier

# 安装 ralph-loop 插件（自主迭代循环）
npx skills add https://github.com/anthropics/claude-code-plugins --agent 'trae-cn' --skill ralph-loop

# 安装 commit-commands 插件（Git工作流命令）
npx skills add https://github.com/anthropics/claude-code-plugins --agent 'trae-cn' --skill commit-commands

# 安装 feature-dev 插件（功能开发流程）
npx skills add https://github.com/anthropics/claude-code-plugins --agent 'trae-cn' --skill feature-dev

# 安装 security-guidance 插件（安全指导）
npx skills add https://github.com/anthropics/claude-code-plugins --agent 'trae-cn' --skill security-guidance
```

### 技能使用

| 技能 | 命令 | 用途 | 使用例子 |
|------|------|------|----------|
| brainstorming | `/brainstorming` | 头脑风暴，设计前需求分析 | `/brainstorming 设计用户登录功能` |
| planning-with-files | `/plan` | 持久化任务规划 | `/plan 实现批量执行测试用例` |
| writing-plans | `/writing-plans` | 编写详细实施计划 | `/writing-plans 重构执行器模块` |
| test-driven-development | `/tdd` | 测试驱动开发 | `/tdd 实现截图去重功能` |
| systematic-debugging | 自动激活 | 系统性调试，根因分析 | `调试这个错误：TypeError...` |
| code-review | `/codex` | 代码审查（安全、性能、可维护性） | `/codex 审查 executor.py` |
| code-simplifier | 自动激活 | 代码简化，提升可读性 | `帮我简化这段代码` |
| webapp-testing | 自动激活 | Web应用自动化测试（Playwright） | `测试登录流程` |
| ralph-loop | `/ralph-loop` | 自主迭代循环，持续执行直到完成 | `/ralph-loop "修复所有测试失败"` |
| find-skills | 自动激活 | 发现和安装新技能 | `有什么技能可以帮我做X` |
| UI UX Pro Max | 自动激活 | UI/UX设计智能建议 | 自动分析界面设计问题 |
| commit-commands | `/commit` | Git提交工作流 | `/commit 推送并创建PR` |
| feature-dev | `/feature-dev` | 七阶段功能开发流程 | `/feature-dev 实现用户认证` |
| security-guidance | 自动激活 | 安全漏洞检测和警告 | 自动检测代码安全问题 |

### 启动项目

<br />

```bash
# 启动后端服务
cd backend
python app.py

# 后端服务地址
http://localhost:8001

# API文档地址
http://localhost:8001/docs

# 启动前端服务（新终端）
cd frontend
npm run dev

# 前端服务地址
http://localhost:3000
```

## 📁 项目结构

```
ai-ui-test-platform/
├── backend/                 # 后端代码
│   ├── api/                # API接口
│   │   └── v2/            # v2版本API
│   │       └── endpoints.py
│   ├── core/              # 核心功能
│   │   ├── executor.py    # 测试执行器
│   │   ├── recorder.py    # 录制功能
│   │   ├── visual_locator.py  # 视觉定位
│   │   ├── nlp_generator.py   # NLP生成
│   │   └── screenshot.py      # 截图工具
│   ├── data/              # 数据文件
│   │   ├── test_cases.json
│   │   └── recordings.json
│   ├── utils/             # 工具函数
│   ├── database.py        # 数据库模型
│   └── app.py            # 主应用
├── frontend/              # 前端代码
│   └── index.html        # 单页应用
├── ai_services/          # AI服务
│   ├── demo_llm.py       # LLM集成
│   └── intelligent_binder.py  # 智能绑定
├── .env.example          # 环境变量示例
├── requirements.txt      # Python依赖
└── README.md            # 项目说明
```

## 🔧 API端点

### 测试用例管理

```bash
# 获取测试用例列表
GET /api/v2/testcases

# 创建测试用例
POST /api/v2/testcases

# 执行测试用例
POST /api/v2/execute
Body: {"test_case_id": 1, "headless": true}

# 获取执行结果
GET /api/v2/execution/{execution_id}
```

### 录制回放

```bash
# 开始录制
POST /api/v2/recording/start
Body: {"url": "https://www.baidu.com", "headless": false}

# 停止录制
POST /api/v2/recording/stop
Body: {"session_id": "session_id"}

# 回放录制
POST /api/v2/recording/replay
```

### 视觉定位

```bash
# 获取视觉模板列表
GET /api/v2/visual-elements

# 创建视觉模板
POST /api/v2/visual-elements

# 视觉定位
POST /api/v2/visual/locate
```

### 报告导出

```bash
# 导出HTML报告
GET /api/v2/reports/export?format=html

# 导出JSON报告
GET /api/v2/reports/export?format=json
```

## 📝 开发笔记

### AI开发技巧

开发重要或复杂功能时，使用以下"咒语"确保AI按严格工程标准工作：

> **请按照 Superpowers 的完整流程，先 brainstorm（头脑风暴），再 write-plan（写计划），最后 execute-plan（执行计划），并且必须做 TDD（测试驱动开发）和 code review（代码审查）。**

**流程说明**：
1. **brainstorm**: 头脑风暴，充分理解需求和设计方案
2. **write-plan**: 编写详细的实施计划
3. **execute-plan**: 按计划执行开发任务
4. **TDD**: 测试驱动开发，先写测试再写代码
5. **code review**: 代码审查，确保代码质量

### 执行流程

```
前端点击"执行"
    ↓
POST /api/v2/execute
    ↓
TestExecutor.execute_testcase()
    ↓
run_playwright_sync() [使用Selenium]
    ↓
返回执行结果
```

### 文件说明

- **executor.py**: 核心执行引擎，使用Selenium控制浏览器
- **endpoints.py**: API接口层，处理HTTP请求
- **recorder.py**: 智能录制功能，使用Playwright
- **visual\_locator.py**: 视觉定位，使用OpenCV

## 🔄 Git版本管理

### 查看提交历史

```bash
# 查看最近5次提交
git log --oneline -5

# 查看当前完整提交ID
git rev-parse HEAD

# 查看短ID
git rev-parse --short HEAD
```

### 版本回退命令

| 命令 | 用途 | 危险程度 |
|------|------|----------|
| `git checkout <commit_id>` | 查看旧版本（只读） | 🟢 低 |
| `git reset --hard <commit_id>` | 强制回退到指定版本 | 🔴 高 |
| `git revert <commit_id>` | 创建反向提交（安全） | 🟢 低 |
| `git reset --soft HEAD~1` | 撤销最近提交（保留修改） | 🟡 中 |
| `git reset --hard HEAD~1` | 撤销最近提交（丢弃修改） | 🔴 高 |

### 常用场景

```bash
# 回退到上个版本
git reset --hard HEAD~1

# 回退到指定版本（如 441201a）
git reset --hard 441201a

# 安全撤销某次提交（推荐）
git revert HEAD
git push origin main

# 查看某个旧版本代码
git checkout 441201a
```

### GitHub查看提交ID

访问：https://github.com/GH-Z202235810103/ai-ui-test-platform/commits/main

## 🎯 快捷键

### 前端操作

- **F5**: 刷新页面
- **Ctrl+Shift+I**: 打开开发者工具
- **Ctrl+Shift+R**: 强制刷新（清除缓存）

### 后端调试

- **Ctrl+C**: 停止后端服务
- **Ctrl+Break**: 强制停止

## 📚 相关文档

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Selenium文档](https://selenium-python.readthedocs.io/)
- [Playwright文档](https://playwright.dev/python/)
- [Vue.js文档](https://vuejs.org/)
- [OpenCV文档](https://docs.opencv.org/)

## 🔗 有用的链接

- **前端界面**: <http://localhost:3000>
- **后端API文档**: <http://localhost:8001/docs>
- **项目仓库**: <https://github.com/GH-Z202235810103/ai-ui-test-platform>
- **DeepSeek API**: <https://platform.deepseek.com/>

***

**提示**: 这个文件可以随时更新，添加新的命令和备忘信息！
