# 测试报告生成与可视化设计文档

**日期**: 2026-05-03
**方案**: 渐进式开发（后端优先）
**技术栈**: Vue3 + TypeScript + FastAPI + ECharts + pdfkit

---

## 1. 概述

### 1.1 目标
为 UI 自动化测试平台开发完整的测试报告生成与可视化模块，支持报告自动生成、数据存储、可视化展示和导出功能。

### 1.2 核心功能
- 报告自动生成：任务执行完毕后自动生成结构化报告
- 数据存储：新增 report_steps 表，扩展 test_reports 表
- 单次报告页：摘要卡片 + ECharts 饼图 + 可展开截图对比
- 历史趋势页：ECharts 折线图/柱状图 + 历史任务列表
- 导出功能：PDF 和 HTML 导出

### 1.3 开发顺序
1. 数据库扩展
2. 后端 API
3. 前端组件
4. 导出功能

---

## 2. 数据库设计

### 2.1 扩展 TestReport 表

```python
class TestReport(Base):
    __tablename__ = "test_reports"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id"))
    
    # 统计字段
    total_count = Column(Integer, default=0)
    pass_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    skip_count = Column(Integer, default=0)
    
    # 保留现有字段
    summary = Column(JSON)
    details = Column(Text)
    duration = Column(Integer)  # 执行耗时（秒）
    screenshot_refs = Column(JSON)
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # 报告状态
    status = Column(String(20), default="completed")  # completed, partial, error
    
    # 关系
    task = relationship("TestTask", back_populates="test_reports")
    steps = relationship("ReportStep", back_populates="report", cascade="all, delete-orphan")
```

### 2.2 新建 ReportStep 表

```python
class ReportStep(Base):
    __tablename__ = "report_steps"
    
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"))
    
    step_index = Column(Integer)  # 步骤序号
    step_name = Column(String(255))  # 步骤名称
    step_desc = Column(Text)  # 步骤描述
    
    status = Column(String(20))  # passed, failed, skipped
    duration = Column(Integer)  # 步骤耗时（毫秒）
    error_message = Column(Text)  # 错误信息
    
    # 截图路径
    expected_screenshot = Column(String(500))
    actual_screenshot = Column(String(500))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # 关系
    report = relationship("TestReport", back_populates="steps")
```

### 2.3 数据迁移
- 使用手动迁移脚本
- 保留现有数据，新字段使用默认值

---

## 3. 后端 API 设计

### 3.1 报告详情接口

```
GET /api/v2/reports/{report_id}
```

**响应结构**：
```json
{
  "success": true,
  "data": {
    "id": 1,
    "task_id": 1,
    "task_name": "登录功能测试",
    "total_count": 5,
    "pass_count": 4,
    "fail_count": 1,
    "skip_count": 0,
    "duration": 120,
    "status": "completed",
    "pass_rate": 80.0,
    "generated_at": "2026-05-03T10:00:00",
    "steps": [
      {
        "id": 1,
        "step_index": 1,
        "step_name": "打开登录页面",
        "status": "passed",
        "duration": 2000,
        "expected_screenshot": "/screenshots/step_1_expected.png",
        "actual_screenshot": "/screenshots/step_1_actual.png"
      }
    ]
  }
}
```

### 3.2 趋势数据接口

```
GET /api/v2/reports/trends?project_id={id}&days=30
```

**响应结构**：
```json
{
  "success": true,
  "data": {
    "project_id": 1,
    "date_range": {
      "start": "2026-04-03",
      "end": "2026-05-03"
    },
    "trends": [
      {
        "date": "2026-05-01",
        "total": 10,
        "passed": 8,
        "failed": 2,
        "pass_rate": 80.0,
        "avg_duration": 45
      }
    ],
    "summary": {
      "total_reports": 30,
      "avg_pass_rate": 85.5,
      "total_tests": 150
    }
  }
}
```

### 3.3 导出接口

```
GET /api/v2/reports/{report_id}/export?format=pdf|html
```

**响应**：
- PDF: `application/pdf` 文件流
- HTML: `text/html` 文件流

### 3.4 截图访问接口

```
GET /api/v2/screenshots/{filename}
```

**功能**：
- 返回截图文件
- 支持懒加载
- JWT 校验

---

## 4. 前端组件设计

### 4.1 ReportDetail.vue（单次报告页）

**组件结构**：
```
ReportDetail.vue
├── 摘要卡片区域
│   ├── 状态卡片（通过/失败/跳过计数）
│   ├── 耗时卡片（总耗时）
│   └── 通过率卡片（百分比显示）
├── ECharts 饼图区域
│   └── 测试结果分布饼图
├── 步骤详情表格
│   ├── 可展开行
│   ├── 状态标签（红/绿/灰）
│   └── 截图对比（左右布局）
└── 操作按钮
    ├── 导出 PDF
    └── 导出 HTML
```

### 4.2 ProjectTrends.vue（历史趋势页）

**组件结构**：
```
ProjectTrends.vue
├── 筛选区域
│   ├── 项目选择器
│   └── 时间范围选择器
├── ECharts 折线图
│   └── 通过率趋势（近30天）
├── ECharts 柱状图
│   └── 耗时趋势
├── 统计摘要卡片
│   ├── 总报告数
│   ├── 平均通过率
│   └── 总测试数
└── 历史任务列表
    └── 可点击跳转报告详情
```

### 4.3 目录结构

```
frontend/
├── src/
│   ├── views/
│   │   ├── ReportDetail.vue
│   │   └── ProjectTrends.vue
│   ├── components/
│   │   ├── report/
│   │   │   ├── SummaryCard.vue
│   │   │   ├── StepTable.vue
│   │   │   ├── ScreenshotCompare.vue
│   │   │   └── ExportButton.vue
│   │   └── charts/
│   │       ├── PieChart.vue
│   │       ├── LineChart.vue
│   │       └── BarChart.vue
│   ├── api/
│   │   └── report.ts
│   └── types/
│       └── report.ts
```

### 4.4 技术实现

| 功能 | 技术方案 |
|------|----------|
| 图表 | ECharts 5.x |
| UI 组件 | Element Plus |
| 状态管理 | Pinia（可选） |
| 路由 | Vue Router |
| HTTP | Axios |
| 截图懒加载 | Intersection Observer API |

---

## 5. 导出功能设计

### 5.1 HTML 模板

**模板结构** (`report_template.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>测试报告 - {{ report.task_name }}</title>
    <style>
        body { font-family: 'Microsoft YaHei', sans-serif; }
        .summary-card { /* 摘要卡片样式 */ }
        .step-table { /* 步骤表格样式 */ }
        .status-pass { color: #67C23A; }
        .status-fail { color: #F56C6C; }
    </style>
</head>
<body>
    <header>测试报告</header>
    <section class="summary"><!-- 摘要 --></section>
    <section class="steps"><!-- 步骤表格 --></section>
</body>
</html>
```

### 5.2 PDF 导出配置

```python
PDF_OPTIONS = {
    'encoding': 'UTF-8',
    'page-size': 'A4',
    'orientation': 'Portrait',
    'margin-top': '15mm',
    'margin-right': '15mm',
    'margin-bottom': '15mm',
    'margin-left': '15mm',
    'enable-local-file-access': None,
}
```

### 5.3 导出服务

```python
class ReportExportService:
    def export_html(self, report_id: int) -> str:
        """导出 HTML 文件"""
        pass
    
    def export_pdf(self, report_id: int) -> bytes:
        """导出 PDF 文件"""
        html_content = self.export_html(report_id)
        return pdfkit.from_string(html_content, False, options=PDF_OPTIONS)
```

### 5.4 文件命名

| 格式 | 命名规则 | 示例 |
|------|----------|------|
| HTML | `report_{task_id}_{date}.html` | `report_1_20260503.html` |
| PDF | `report_{task_id}_{date}.pdf` | `report_1_20260503.pdf` |

---

## 6. 报告自动生成逻辑

### 6.1 触发时机

测试任务执行完成 → 自动生成报告

### 6.2 报告生成服务

```python
class ReportGenerator:
    def generate_report(self, task_id: int, execution_result: Dict) -> TestReport:
        """生成测试报告"""
        # 1. 创建报告主记录
        report = TestReport(
            task_id=task_id,
            total_count=execution_result['total_steps'],
            pass_count=execution_result['passed_steps'],
            fail_count=execution_result['failed_steps'],
            skip_count=execution_result['skipped_steps'],
            duration=execution_result['duration'],
            status="completed" if execution_result['success'] else "partial",
            summary=self._generate_summary(execution_result),
        )
        
        # 2. 创建步骤记录
        for idx, step_result in enumerate(execution_result['steps'], 1):
            step = ReportStep(
                report_id=report.id,
                step_index=idx,
                step_name=step_result.get('name', f'步骤{idx}'),
                status=step_result['status'],
                duration=step_result.get('duration', 0),
                error_message=step_result.get('error'),
                actual_screenshot=step_result.get('screenshot')
            )
        
        return report
```

### 6.3 执行结果数据结构

```python
execution_result = {
    "success": True,
    "task_id": 1,
    "total_steps": 5,
    "passed_steps": 4,
    "failed_steps": 1,
    "skipped_steps": 0,
    "duration": 120,
    "steps": [
        {
            "name": "打开登录页面",
            "status": "passed",
            "duration": 2000,
            "error": None,
            "screenshot": "/screenshots/step_1.png"
        }
    ]
}
```

---

## 7. 测试策略

### 7.1 单元测试

| 模块 | 测试重点 |
|------|----------|
| ReportGenerator | 报告生成逻辑、步骤记录 |
| ReportExportService | HTML/PDF 导出 |
| API 端点 | 请求响应格式、权限校验 |

### 7.2 集成测试

- 报告详情接口完整流程
- 趋势数据计算正确性
- 导出文件生成

### 7.3 端到端测试

- 完整测试任务执行 → 报告生成 → 查看 → 导出

---

## 8. 实施计划

### 阶段 1：数据库扩展
1. 扩展 TestReport 模型
2. 创建 ReportStep 模型
3. 数据迁移脚本

### 阶段 2：后端 API
4. 报告详情接口
5. 趋势数据接口
6. 截图访问接口
7. 报告生成服务

### 阶段 3：导出功能
8. HTML 模板
9. PDF 导出服务
10. 导出接口

### 阶段 4：前端组件
11. ReportDetail.vue
12. ProjectTrends.vue
13. 图表组件
14. 路由配置

---

## 9. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| pdfkit 依赖外部程序 | 中 | 文档说明安装步骤 |
| 截图文件过大 | 低 | 压缩截图、懒加载 |
| 前端图表性能 | 低 | 数据分页、虚拟滚动 |

---

## 10. 依赖

### 后端
```
pdfkit>=1.0.2
Jinja2>=3.0.0
```

### 系统依赖
- wkhtmltopdf（PDF 导出）

### 前端
```
echarts>=5.4.0
element-plus>=2.3.0
axios>=1.0.0
```
