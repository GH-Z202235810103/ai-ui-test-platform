# Checklist

## 配置统一
- [x] backend/config.py 中 API_PORT 默认值改为 8001
- [x] frontend/vite.config.ts 代理目标指向 http://localhost:8001
- [x] .env.example 中端口配置示例正确

## 代码清理
- [x] 重复的API文件已处理（保留v2或明确区分）
- [x] 无用的静态文件挂载已移除
- [x] 项目结构清晰，无冗余文件

## 文档更新
- [x] README.md 启动说明已更新
- [x] CHEATSHEET.md 端口配置已更新
- [x] 项目启动指南清晰明确

## 功能验证
- [x] 后端服务器能在 8001 端口正常启动
- [x] 前端服务器能在 3000 端口正常启动
- [x] 前端能正确代理请求到后端
- [x] 所有API接口正常响应
