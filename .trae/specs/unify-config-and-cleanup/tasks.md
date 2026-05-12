# Tasks

- [x] Task 1: 统一端口配置
  - [x] SubTask 1.1: 修改 backend/config.py，将默认端口从 8000 改为 8001
  - [x] SubTask 1.2: 确认 frontend/vite.config.ts 代理配置指向 8001
  - [x] SubTask 1.3: 更新 .env.example 中的端口配置示例

- [x] Task 2: 清理重复的API文件
  - [x] SubTask 2.1: 检查 backend/api/endpoints.py 和 backend/api/v2/endpoints.py 的用途
  - [x] SubTask 2.2: 确定保留策略（保留v2或合并）
  - [x] SubTask 2.3: 移除或标记废弃的重复代码

- [x] Task 3: 优化后端静态文件挂载
  - [x] SubTask 3.1: 检查 backend/app.py 中的静态文件挂载逻辑
  - [x] SubTask 3.2: 移除前端静态文件挂载（前端应独立运行）
  - [x] SubTask 3.3: 保留必要的静态资源挂载（如截图目录）

- [x] Task 4: 更新项目文档
  - [x] SubTask 4.1: 更新 README.md 中的启动说明
  - [x] SubTask 4.2: 更新 CHEATSHEET.md 中的端口配置
  - [x] SubTask 4.3: 添加清晰的项目启动指南

- [x] Task 5: 验证配置一致性
  - [x] SubTask 5.1: 启动后端服务器验证端口
  - [x] SubTask 5.2: 启动前端服务器验证代理
  - [x] SubTask 5.3: 测试前后端联调是否正常

# Task Dependencies
- [Task 5] depends on [Task 1, Task 2, Task 3, Task 4]
