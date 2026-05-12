# 项目配置统一与代码优化 Spec

## Why
项目前后端配置不一致，后端默认端口是 8000，但前端代理配置指向 8001，导致用户启动后端后访问空白页面。需要统一配置并清理无用代码。

## What Changes
- **BREAKING** 统一后端默认端口从 8000 改为 8001
- 更新前端代理配置与后端端口保持一致
- 检查并清理重复/无用的代码文件
- 优化项目启动脚本和文档

## Impact
- Affected specs: 后端配置、前端代理配置
- Affected code: 
  - `backend/config.py` - API端口配置
  - `frontend/vite.config.ts` - 前端代理配置
  - `backend/app.py` - 静态文件挂载逻辑
  - 相关文档和配置文件

## ADDED Requirements

### Requirement: 统一端口配置
系统 SHALL 使用统一的端口配置，确保前后端配置一致。

#### Scenario: 启动后端后前端可正常访问
- **WHEN** 用户启动后端服务器
- **THEN** 前端代理能够正确连接到后端API
- **AND** 用户访问前端页面能够正常加载数据

### Requirement: 清理无用代码
系统 SHALL 移除重复和无用的代码文件，保持项目整洁。

#### Scenario: 项目结构清晰
- **WHEN** 开发者查看项目结构
- **THEN** 不存在重复的API文件
- **AND** 不存在无用的测试文件
- **AND** 配置文件之间保持一致

## MODIFIED Requirements

### Requirement: 后端端口配置
后端默认端口 SHALL 从 8000 改为 8001，与前端代理配置保持一致。

### Requirement: 前端代理配置
前端代理配置 SHALL 指向后端实际运行的端口。

## REMOVED Requirements

### Requirement: 重复的API文件
**Reason**: 项目中存在 `backend/api/endpoints.py` 和 `backend/api/v2/endpoints.py` 两个文件，功能重复
**Migration**: 保留 v2 版本，移除旧版本或明确区分用途

### Requirement: 无用的静态文件挂载
**Reason**: `backend/app.py` 中挂载了前端静态文件，但前端应该独立运行开发服务器
**Migration**: 移除静态文件挂载，前端通过 Vite 开发服务器独立运行
