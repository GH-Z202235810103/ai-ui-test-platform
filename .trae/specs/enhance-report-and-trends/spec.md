# 完善趋势分析和测试报告功能 Spec

## Why
用户执行了多次测试用例，但趋势分析页面内容为空，测试报告功能也未完全实现，导致用户无法查看测试历史数据和报告详情。

## What Changes
- 确保测试用例执行结果正确保存到TestReport表
- 完善趋势分析数据展示，包括通过率趋势、耗时趋势、历史报告列表
- 添加测试报告列表页面，展示所有测试报告
- 优化报告详情页面，展示完整的步骤信息和截图
- 添加报告导出功能（HTML/PDF）
- 确保前端组件正确渲染图表和数据

## Impact
- Affected specs: 测试用例执行、测试报告生成、数据分析
- Affected code:
  - `backend/core/executor_optimized.py` - 执行结果保存逻辑
  - `backend/api/v2/endpoints.py` - 报告相关API
  - `frontend/src/views/ProjectTrends.vue` - 趋势分析页面
  - `frontend/src/views/ReportList.vue` - 报告列表页面（新增）
  - `frontend/src/views/ReportDetail.vue` - 报告详情页面
  - `frontend/src/components/charts/*.vue` - 图表组件
  - `frontend/src/components/report/*.vue` - 报告组件

## ADDED Requirements

### Requirement: 测试报告自动生成
系统 SHALL 在测试用例执行完成后自动生成测试报告，包括：
- 执行摘要（总步骤数、通过数、失败数、跳过数）
- 每个步骤的详细信息（步骤描述、状态、截图、错误信息）
- 执行时长统计
- 生成时间戳

#### Scenario: 测试用例执行完成
- **WHEN** 测试用例执行完成
- **THEN** 系统自动生成测试报告并保存到数据库
- **AND** 报告包含完整的执行结果和步骤详情

### Requirement: 趋势分析数据展示
系统 SHALL 提供测试趋势分析功能，包括：
- 通过率趋势图表（折线图）
- 耗时趋势图表（柱状图）
- 历史报告列表（表格）
- 汇总统计卡片（总报告数、平均通过率、总测试数）

#### Scenario: 查看趋势分析
- **WHEN** 用户访问趋势分析页面
- **THEN** 系统显示指定时间范围内的测试趋势数据
- **AND** 图表正确渲染，数据准确

#### Scenario: 筛选趋势数据
- **WHEN** 用户选择项目或时间范围
- **THEN** 系统更新趋势数据展示
- **AND** 图表和列表同步更新

### Requirement: 测试报告列表
系统 SHALL 提供测试报告列表页面，展示所有测试报告，包括：
- 报告ID、名称、状态
- 通过率、总步骤数
- 生成时间
- 操作按钮（查看详情、导出）

#### Scenario: 查看报告列表
- **WHEN** 用户访问报告列表页面
- **THEN** 系统显示所有测试报告
- **AND** 支持按项目、状态、时间筛选

### Requirement: 报告详情完善
系统 SHALL 提供完整的报告详情页面，包括：
- 执行摘要卡片
- 通过率饼图
- 步骤详情表格
- 截图预览
- 导出功能

#### Scenario: 查看报告详情
- **WHEN** 用户点击报告查看详情
- **THEN** 系统显示完整的报告信息
- **AND** 步骤详情表格展示每个步骤的状态和截图

#### Scenario: 导出报告
- **WHEN** 用户点击导出按钮
- **THEN** 系统生成HTML或PDF格式的报告文件
- **AND** 浏览器下载报告文件

## MODIFIED Requirements

### Requirement: 执行结果保存
执行器 SHALL 在测试用例执行完成后自动保存执行结果到TestReport表，确保数据完整性和一致性。

### Requirement: 前端图表渲染
前端图表组件 SHALL 正确渲染ECharts图表，包括折线图、柱状图、饼图等。

## REMOVED Requirements

无
