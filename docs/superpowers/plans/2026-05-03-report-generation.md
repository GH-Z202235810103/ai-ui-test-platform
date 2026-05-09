# 测试报告生成与可视化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 UI 自动化测试平台开发完整的测试报告生成与可视化模块，支持报告自动生成、数据存储、可视化展示和 PDF/HTML 导出。

**Architecture:** 渐进式开发，后端优先。先扩展数据库模型，再开发后端 API 和报告生成服务，然后实现导出功能，最后开发前端 Vue3 组件。

**Tech Stack:** Python, FastAPI, SQLAlchemy, pdfkit, Jinja2, Vue3, TypeScript, Element Plus, ECharts, Axios

---

## 文件结构

```
backend/
├── database.py                    # 修改：扩展 TestReport，新增 ReportStep
├── core/
│   ├── report_generator.py        # 新增：报告自动生成服务
│   └── report_export.py           # 新增：报告导出服务
├── api/v2/
│   └── endpoints.py               # 修改：新增报告相关接口
├── templates/
│   └── reports/
│       └── report_template.html   # 新增：导出用 HTML 模板
└── tests/
    ├── test_report_generator.py   # 新增
    └── test_report_export.py      # 新增

frontend/
├── package.json                   # 新增：Vue3 项目配置
├── vite.config.ts                 # 新增
├── tsconfig.json                  # 新增
├── index.html                     # 修改：Vue3 入口
└── src/
    ├── main.ts                    # 新增
    ├── App.vue                    # 新增
    ├── router/index.ts            # 新增
    ├── api/report.ts              # 新增
    ├── types/report.ts            # 新增
    ├── views/
    │   ├── ReportDetail.vue       # 新增
    │   └── ProjectTrends.vue      # 新增
    └── components/
        ├── report/
        │   ├── SummaryCard.vue    # 新增
        │   ├── StepTable.vue      # 新增
        │   ├── ScreenshotCompare.vue # 新增
        │   └── ExportButton.vue   # 新增
        └── charts/
            ├── PieChart.vue       # 新增
            ├── LineChart.vue      # 新增
            └── BarChart.vue       # 新增
```

---

## Task 1: 扩展数据库模型

**Files:**
- Modify: `backend/database.py`
- Create: `backend/tests/test_report_models.py`

### Step 1.1: 编写数据库模型测试

- [ ] **编写数据库模型测试**

创建文件 `backend/tests/test_report_models.py`:

```python
import pytest
import sys
sys.path.insert(0, 'backend')
from database import TestReport, ReportStep, Base, engine, SessionLocal


class TestReportModels:
    def setup_method(self):
        Base.metadata.create_all(engine)
        self.session = SessionLocal()
    
    def teardown_method(self):
        self.session.rollback()
        self.session.close()
    
    def test_create_report_with_counts(self):
        report = TestReport(
            task_id=1,
            total_count=5,
            pass_count=4,
            fail_count=1,
            skip_count=0,
            duration=120,
            status="completed",
            summary={"pass_rate": 80.0}
        )
        self.session.add(report)
        self.session.flush()
        
        assert report.id is not None
        assert report.total_count == 5
        assert report.pass_count == 4
        assert report.fail_count == 1
        assert report.skip_count == 0
        assert report.status == "completed"
    
    def test_create_report_step(self):
        report = TestReport(
            task_id=1,
            total_count=1,
            pass_count=1,
            fail_count=0,
            skip_count=0,
            status="completed"
        )
        self.session.add(report)
        self.session.flush()
        
        step = ReportStep(
            report_id=report.id,
            step_index=1,
            step_name="打开页面",
            step_desc="访问 https://example.com",
            status="passed",
            duration=2000,
            actual_screenshot="/screenshots/step_1.png"
        )
        self.session.add(step)
        self.session.flush()
        
        assert step.id is not None
        assert step.report_id == report.id
        assert step.status == "passed"
    
    def test_report_steps_relationship(self):
        report = TestReport(
            task_id=1,
            total_count=2,
            pass_count=2,
            fail_count=0,
            skip_count=0,
            status="completed"
        )
        self.session.add(report)
        self.session.flush()
        
        step1 = ReportStep(report_id=report.id, step_index=1, step_name="步骤1", status="passed")
        step2 = ReportStep(report_id=report.id, step_index=2, step_name="步骤2", status="passed")
        self.session.add_all([step1, step2])
        self.session.flush()
        
        assert len(report.steps) == 2
    
    def test_report_step_fail_with_error(self):
        report = TestReport(
            task_id=1,
            total_count=1,
            pass_count=0,
            fail_count=1,
            skip_count=0,
            status="partial"
        )
        self.session.add(report)
        self.session.flush()
        
        step = ReportStep(
            report_id=report.id,
            step_index=1,
            step_name="点击按钮",
            status="failed",
            error_message="Element not found: #submit-btn"
        )
        self.session.add(step)
        self.session.flush()
        
        assert step.status == "failed"
        assert step.error_message is not None
```

### Step 1.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/test_report_models.py -v
```

Expected: FAIL - ReportStep not defined

### Step 1.3: 扩展数据库模型

- [ ] **扩展 TestReport 和新增 ReportStep 模型**

修改 `backend/database.py`，在 `TestReport` 类中添加新字段，并新增 `ReportStep` 类：

在 `TestReport` 类中添加：

```python
class TestReport(Base):
    """测试报告表"""
    __tablename__ = "test_reports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id"))
    
    total_count = Column(Integer, default=0)
    pass_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    skip_count = Column(Integer, default=0)
    
    summary = Column(JSON)
    details = Column(Text)
    duration = Column(Integer)
    screenshot_refs = Column(JSON)
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(String(20), default="completed")
    
    task = relationship("TestTask", back_populates="test_reports")
    steps = relationship("ReportStep", back_populates="report", cascade="all, delete-orphan")
```

在 `TestReport` 类之后添加 `ReportStep` 类：

```python
class ReportStep(Base):
    """报告步骤表"""
    __tablename__ = "report_steps"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"))
    
    step_index = Column(Integer)
    step_name = Column(String(255))
    step_desc = Column(Text)
    status = Column(String(20))
    duration = Column(Integer)
    error_message = Column(Text)
    expected_screenshot = Column(String(500))
    actual_screenshot = Column(String(500))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    report = relationship("TestReport", back_populates="steps")
```

### Step 1.4: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/test_report_models.py -v
```

Expected: PASS

### Step 1.5: 提交

- [ ] **提交数据库模型扩展**

```bash
git add backend/database.py backend/tests/test_report_models.py
git commit -m "feat: extend TestReport model and add ReportStep model"
```

---

## Task 2: 报告生成服务

**Files:**
- Create: `backend/core/report_generator.py`
- Create: `backend/tests/test_report_generator.py`

### Step 2.1: 编写报告生成器测试

- [ ] **编写报告生成器测试**

创建文件 `backend/tests/test_report_generator.py`:

```python
import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from core.report_generator import ReportGenerator


class TestReportGenerator:
    def setup_method(self):
        self.mock_db = MagicMock()
        self.generator = ReportGenerator(self.mock_db)
    
    def test_generate_report_creates_report_record(self):
        execution_result = {
            "success": True,
            "task_id": 1,
            "total_steps": 5,
            "passed_steps": 4,
            "failed_steps": 1,
            "skipped_steps": 0,
            "duration": 120,
            "steps": [
                {"name": "步骤1", "status": "passed", "duration": 2000, "error": None, "screenshot": "/screenshots/1.png"},
                {"name": "步骤2", "status": "passed", "duration": 3000, "error": None, "screenshot": "/screenshots/2.png"},
                {"name": "步骤3", "status": "failed", "duration": 1000, "error": "Element not found", "screenshot": "/screenshots/3.png"},
                {"name": "步骤4", "status": "passed", "duration": 2500, "error": None, "screenshot": "/screenshots/4.png"},
                {"name": "步骤5", "status": "passed", "duration": 1500, "error": None, "screenshot": "/screenshots/5.png"},
            ]
        }
        
        report = self.generator.generate_report(1, execution_result)
        
        assert report.total_count == 5
        assert report.pass_count == 4
        assert report.fail_count == 1
        assert report.skip_count == 0
        assert report.duration == 120
        assert report.status == "completed"
    
    def test_generate_report_partial_status(self):
        execution_result = {
            "success": False,
            "task_id": 1,
            "total_steps": 3,
            "passed_steps": 1,
            "failed_steps": 2,
            "skipped_steps": 0,
            "duration": 60,
            "steps": [
                {"name": "步骤1", "status": "passed", "duration": 1000, "error": None, "screenshot": None},
                {"name": "步骤2", "status": "failed", "duration": 500, "error": "Timeout", "screenshot": None},
                {"name": "步骤3", "status": "failed", "duration": 0, "error": "Skipped due to previous failure", "screenshot": None},
            ]
        }
        
        report = self.generator.generate_report(1, execution_result)
        
        assert report.status == "partial"
    
    def test_generate_summary(self):
        execution_result = {
            "success": True,
            "total_steps": 4,
            "passed_steps": 3,
            "failed_steps": 1,
            "skipped_steps": 0,
            "duration": 100,
            "steps": []
        }
        
        summary = self.generator._generate_summary(execution_result)
        
        assert summary["pass_rate"] == 75.0
        assert summary["total_duration"] == 100
    
    def test_generate_report_with_steps(self):
        execution_result = {
            "success": True,
            "task_id": 1,
            "total_steps": 2,
            "passed_steps": 2,
            "failed_steps": 0,
            "skipped_steps": 0,
            "duration": 30,
            "steps": [
                {"name": "打开页面", "status": "passed", "duration": 2000, "error": None, "screenshot": "/screenshots/1.png"},
                {"name": "点击按钮", "status": "passed", "duration": 1000, "error": None, "screenshot": "/screenshots/2.png"},
            ]
        }
        
        report = self.generator.generate_report(1, execution_result)
        
        assert self.mock_db.add.call_count >= 3  # 1 report + 2 steps
        assert self.mock_db.commit.called
```

### Step 2.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/test_report_generator.py -v
```

Expected: FAIL - ModuleNotFoundError

### Step 2.3: 创建报告生成器实现

- [ ] **创建报告生成器实现**

创建文件 `backend/core/report_generator.py`:

```python
from datetime import datetime
from typing import Dict, Optional
from database import TestReport, ReportStep


class ReportGenerator:
    def __init__(self, db):
        self.db = db
    
    def generate_report(self, task_id: int, execution_result: Dict) -> TestReport:
        report = TestReport(
            task_id=task_id,
            total_count=execution_result.get('total_steps', 0),
            pass_count=execution_result.get('passed_steps', 0),
            fail_count=execution_result.get('failed_steps', 0),
            skip_count=execution_result.get('skipped_steps', 0),
            duration=execution_result.get('duration', 0),
            status="completed" if execution_result.get('success') else "partial",
            summary=self._generate_summary(execution_result),
            generated_at=datetime.utcnow()
        )
        self.db.add(report)
        self.db.flush()
        
        for idx, step_result in enumerate(execution_result.get('steps', []), 1):
            step = ReportStep(
                report_id=report.id,
                step_index=idx,
                step_name=step_result.get('name', f'步骤{idx}'),
                step_desc=step_result.get('description', ''),
                status=step_result.get('status', 'skipped'),
                duration=step_result.get('duration', 0),
                error_message=step_result.get('error'),
                expected_screenshot=step_result.get('expected_screenshot'),
                actual_screenshot=step_result.get('screenshot') or step_result.get('actual_screenshot')
            )
            self.db.add(step)
        
        self.db.commit()
        return report
    
    def _generate_summary(self, execution_result: Dict) -> Dict:
        total = execution_result.get('total_steps', 0)
        passed = execution_result.get('passed_steps', 0)
        pass_rate = round(passed / total * 100, 2) if total > 0 else 0.0
        
        errors = []
        for step in execution_result.get('steps', []):
            if step.get('error'):
                errors.append({
                    "step": step.get('name', ''),
                    "error": step.get('error')
                })
        
        return {
            "pass_rate": pass_rate,
            "total_duration": execution_result.get('duration', 0),
            "error_summary": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Step 2.4: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/test_report_generator.py -v
```

Expected: PASS

### Step 2.5: 提交

- [ ] **提交报告生成器**

```bash
git add backend/core/report_generator.py backend/tests/test_report_generator.py
git commit -m "feat: add report generator service"
```

---

## Task 3: 后端 API 接口

**Files:**
- Modify: `backend/api/v2/endpoints.py`

### Step 3.1: 编写 API 测试

- [ ] **编写 API 测试**

创建文件 `backend/tests/test_report_api.py`:

```python
import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


class TestReportAPI:
    def setup_method(self):
        pass
    
    def test_get_report_detail_with_steps(self):
        from app import app
        client = TestClient(app)
        
        response = client.get("/api/v2/reports/1")
        
        assert response.status_code in [200, 404]
    
    def test_get_report_trends(self):
        from app import app
        client = TestClient(app)
        
        response = client.get("/api/v2/reports/trends")
        
        assert response.status_code in [200, 404, 422]
    
    def test_export_report_pdf(self):
        from app import app
        client = TestClient(app)
        
        response = client.get("/api/v2/reports/1/export?format=pdf")
        
        assert response.status_code in [200, 404, 500]
    
    def test_export_report_html(self):
        from app import app
        client = TestClient(app)
        
        response = client.get("/api/v2/reports/1/export?format=html")
        
        assert response.status_code in [200, 404, 500]
```

### Step 3.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/test_report_api.py -v
```

Expected: FAIL - endpoints not defined

### Step 3.3: 添加报告详情接口（含步骤）

- [ ] **修改报告详情接口，返回步骤数据**

修改 `backend/api/v2/endpoints.py` 中的 `get_report` 函数：

```python
@router.get("/reports/{report_id}")
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """获取测试报告详情（含步骤）"""
    from database import ReportStep
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="测试报告不存在")
    
    report_data = serialize_model(report)
    
    steps = db.query(ReportStep).filter(ReportStep.report_id == report_id).order_by(ReportStep.step_index).all()
    report_data["steps"] = [serialize_model(s) for s in steps]
    
    total = report.total_count or 0
    report_data["pass_rate"] = round(report.pass_count / total * 100, 2) if total > 0 else 0.0
    
    if report.task_id:
        task = db.query(TestTask).filter(TestTask.id == report.task_id).first()
        if task:
            report_data["task_name"] = task.name
    
    return {"success": True, "data": report_data}
```

### Step 3.4: 添加趋势数据接口

- [ ] **添加趋势数据接口**

在 `backend/api/v2/endpoints.py` 中添加：

```python
@router.get("/reports/trends/overview")
async def get_report_trends(project_id: Optional[int] = None, days: int = 30, db: Session = Depends(get_db)):
    """获取报告趋势数据"""
    from datetime import timedelta
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(TestReport).filter(TestReport.generated_at >= start_date)
    
    if project_id:
        task_ids = db.query(TestTask.id).filter(TestTask.project_id == project_id).all()
        task_ids = [t[0] for t in task_ids]
        query = query.filter(TestReport.task_id.in_(task_ids))
    
    reports = query.order_by(TestReport.generated_at).all()
    
    trends = []
    for report in reports:
        total = report.total_count or 0
        pass_rate = round(report.pass_count / total * 100, 2) if total > 0 else 0.0
        trends.append({
            "date": report.generated_at.strftime("%Y-%m-%d") if report.generated_at else "",
            "total": total,
            "passed": report.pass_count or 0,
            "failed": report.fail_count or 0,
            "pass_rate": pass_rate,
            "avg_duration": report.duration or 0
        })
    
    total_reports = len(reports)
    avg_pass_rate = round(sum(t["pass_rate"] for t in trends) / total_reports, 2) if total_reports > 0 else 0.0
    total_tests = sum(t["total"] for t in trends)
    
    return {
        "success": True,
        "data": {
            "project_id": project_id,
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": datetime.utcnow().strftime("%Y-%m-%d")
            },
            "trends": trends,
            "summary": {
                "total_reports": total_reports,
                "avg_pass_rate": avg_pass_rate,
                "total_tests": total_tests
            }
        }
    }
```

### Step 3.5: 添加导出接口

- [ ] **添加导出接口**

在 `backend/api/v2/endpoints.py` 中添加：

```python
@router.get("/reports/{report_id}/export")
async def export_report(report_id: int, format: str = "html", db: Session = Depends(get_db)):
    """导出测试报告"""
    from core.report_export import ReportExportService
    from fastapi.responses import Response
    
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="测试报告不存在")
    
    export_service = ReportExportService()
    
    try:
        if format == "pdf":
            pdf_bytes = export_service.export_pdf(report_id, db)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
            )
        else:
            html_content = export_service.export_html(report_id, db)
            return Response(
                content=html_content,
                media_type="text/html",
                headers={"Content-Disposition": f"attachment; filename=report_{report_id}.html"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")
```

### Step 3.6: 添加截图访问接口

- [ ] **添加截图访问接口**

在 `backend/api/v2/endpoints.py` 中添加：

```python
@router.get("/screenshots/{filename}")
async def get_screenshot(filename: str):
    """获取截图文件"""
    from fastapi.responses import FileResponse
    from pathlib import Path
    
    screenshots_dir = Path(__file__).parent.parent.parent / "screenshots"
    file_path = screenshots_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="截图文件不存在")
    
    return FileResponse(str(file_path))
```

### Step 3.7: 更新 create_report 接口

- [ ] **更新 create_report 接口，支持新字段**

修改 `backend/api/v2/endpoints.py` 中的 `create_report` 函数：

```python
@router.post("/reports")
async def create_report(task_id: int, summary: Dict, details: Optional[str] = None,
                        duration: Optional[int] = None, screenshot_refs: Optional[List] = None,
                        total_count: int = 0, pass_count: int = 0, fail_count: int = 0, skip_count: int = 0,
                        status: str = "completed",
                        db: Session = Depends(get_db)):
    """创建测试报告"""
    db_report = TestReport(
        task_id=task_id,
        summary=summary,
        details=details,
        duration=duration,
        screenshot_refs=screenshot_refs,
        total_count=total_count,
        pass_count=pass_count,
        fail_count=fail_count,
        skip_count=skip_count,
        status=status
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return {"success": True, "data": serialize_model(db_report)}
```

### Step 3.8: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/test_report_api.py -v
```

Expected: PASS

### Step 3.9: 提交

- [ ] **提交 API 接口**

```bash
git add backend/api/v2/endpoints.py backend/tests/test_report_api.py
git commit -m "feat: add report detail, trends, export and screenshot API endpoints"
```

---

## Task 4: 报告导出服务

**Files:**
- Create: `backend/core/report_export.py`
- Create: `backend/templates/reports/report_template.html`
- Create: `backend/tests/test_report_export.py`

### Step 4.1: 编写导出服务测试

- [ ] **编写导出服务测试**

创建文件 `backend/tests/test_report_export.py`:

```python
import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from core.report_export import ReportExportService


class TestReportExportService:
    def setup_method(self):
        self.service = ReportExportService()
    
    def test_export_html_returns_string(self):
        mock_db = MagicMock()
        mock_report = MagicMock()
        mock_report.id = 1
        mock_report.task_id = 1
        mock_report.total_count = 5
        mock_report.pass_count = 4
        mock_report.fail_count = 1
        mock_report.skip_count = 0
        mock_report.duration = 120
        mock_report.status = "completed"
        mock_report.summary = {"pass_rate": 80.0}
        mock_report.generated_at = "2026-05-03"
        mock_report.steps = []
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_report
        
        result = self.service.export_html(1, mock_db)
        
        assert isinstance(result, str)
        assert "测试报告" in result
    
    def test_export_pdf_calls_pdfkit(self):
        mock_db = MagicMock()
        mock_report = MagicMock()
        mock_report.id = 1
        mock_report.task_id = 1
        mock_report.total_count = 2
        mock_report.pass_count = 2
        mock_report.fail_count = 0
        mock_report.skip_count = 0
        mock_report.duration = 30
        mock_report.status = "completed"
        mock_report.summary = {"pass_rate": 100.0}
        mock_report.generated_at = "2026-05-03"
        mock_report.steps = []
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_report
        
        with patch('core.report_export.pdfkit') as mock_pdfkit:
            mock_pdfkit.from_string.return_value = b"fake-pdf-content"
            result = self.service.export_pdf(1, mock_db)
            
            assert result == b"fake-pdf-content"
            mock_pdfkit.from_string.assert_called_once()
```

### Step 4.2: 运行测试确认失败

- [ ] **运行测试确认失败**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/test_report_export.py -v
```

Expected: FAIL - ModuleNotFoundError

### Step 4.3: 创建 HTML 模板

- [ ] **创建导出用 HTML 模板**

创建目录和文件 `backend/templates/reports/report_template.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - {{ report.task_name or '未知任务' }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f7fa; color: #333; }
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; margin-bottom: 20px; }
        .header h1 { font-size: 24px; margin-bottom: 8px; }
        .header .meta { font-size: 14px; opacity: 0.9; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
        .stat-card { padding: 20px; border-radius: 8px; text-align: center; color: white; }
        .stat-card.total { background: linear-gradient(135deg, #667eea, #764ba2); }
        .stat-card.passed { background: linear-gradient(135deg, #11998e, #38ef7d); }
        .stat-card.failed { background: linear-gradient(135deg, #eb3349, #f45c43); }
        .stat-card.skipped { background: linear-gradient(135deg, #f093fb, #f5576c); }
        .stat-number { font-size: 32px; font-weight: bold; }
        .stat-label { font-size: 13px; opacity: 0.9; margin-top: 5px; }
        .pass-rate { text-align: center; padding: 15px; background: white; border-radius: 8px; margin-bottom: 20px; }
        .pass-rate .value { font-size: 36px; font-weight: bold; color: {% if report.pass_rate >= 80 %}#27ae60{% elif report.pass_rate >= 60 %}#f39c12{% else %}#e74c3c{% endif %}; }
        .pass-rate .label { font-size: 14px; color: #7f8c8d; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
        th { background: #34495e; color: white; padding: 12px 15px; text-align: left; font-size: 14px; }
        td { padding: 12px 15px; border-bottom: 1px solid #ecf0f1; font-size: 14px; }
        tr:hover { background: #f8f9fa; }
        .status-passed { color: #27ae60; font-weight: bold; }
        .status-failed { color: #e74c3c; font-weight: bold; }
        .status-skipped { color: #f39c12; font-weight: bold; }
        .screenshot { max-width: 200px; border: 1px solid #ddd; border-radius: 4px; }
        .footer { text-align: center; margin-top: 20px; color: #95a5a6; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>测试报告</h1>
            <div class="meta">{{ report.task_name or '未知任务' }} | 生成时间: {{ report.generated_at }}</div>
        </div>
        
        <div class="summary">
            <div class="stat-card total">
                <div class="stat-number">{{ report.total_count }}</div>
                <div class="stat-label">总步骤数</div>
            </div>
            <div class="stat-card passed">
                <div class="stat-number">{{ report.pass_count }}</div>
                <div class="stat-label">通过</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-number">{{ report.fail_count }}</div>
                <div class="stat-label">失败</div>
            </div>
            <div class="stat-card skipped">
                <div class="stat-number">{{ report.skip_count }}</div>
                <div class="stat-label">跳过</div>
            </div>
        </div>
        
        <div class="pass-rate">
            <div class="value">{{ "%.1f"|format(report.pass_rate) }}%</div>
            <div class="label">通过率</div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>序号</th>
                    <th>步骤名称</th>
                    <th>状态</th>
                    <th>耗时(ms)</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>
                {% for step in report.steps %}
                <tr>
                    <td>{{ step.step_index }}</td>
                    <td>{{ step.step_name }}</td>
                    <td class="status-{{ step.status }}">{{ step.status }}</td>
                    <td>{{ step.duration }}</td>
                    <td>{{ step.error_message or '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="footer">
            AI UI自动化测试平台 - 测试报告 | 耗时: {{ report.duration }}秒
        </div>
    </div>
</body>
</html>
```

### Step 4.4: 创建导出服务实现

- [ ] **创建导出服务实现**

创建文件 `backend/core/report_export.py`:

```python
from pathlib import Path
from typing import Optional
from jinja2 import Template
from database import TestReport, ReportStep


TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "reports"

PDF_OPTIONS = {
    'encoding': 'UTF-8',
    'page-size': 'A4',
    'orientation': 'Portrait',
    'margin-top': '15mm',
    'margin-right': '15mm',
    'margin-bottom': '15mm',
    'margin-left': '15mm',
    'enable-local-file-access': None,
    'no-stop-slow-scripts': None,
}


class ReportExportService:
    def __init__(self, template_dir: Optional[str] = None):
        if template_dir:
            self.template_dir = Path(template_dir)
        else:
            self.template_dir = TEMPLATE_DIR
    
    def export_html(self, report_id: int, db) -> str:
        report_data = self._get_report_data(report_id, db)
        template = self._load_template("report_template.html")
        return template.render(report=report_data)
    
    def export_pdf(self, report_id: int, db) -> bytes:
        import pdfkit
        html_content = self.export_html(report_id, db)
        return pdfkit.from_string(html_content, False, options=PDF_OPTIONS)
    
    def _get_report_data(self, report_id: int, db) -> dict:
        report = db.query(TestReport).filter(TestReport.id == report_id).first()
        if not report:
            raise ValueError(f"报告不存在: {report_id}")
        
        steps = db.query(ReportStep).filter(ReportStep.report_id == report_id).order_by(ReportStep.step_index).all()
        
        total = report.total_count or 0
        pass_rate = round(report.pass_count / total * 100, 1) if total > 0 else 0.0
        
        task_name = ""
        if report.task_id:
            from database import TestTask
            task = db.query(TestTask).filter(TestTask.id == report.task_id).first()
            if task:
                task_name = task.name
        
        return {
            "id": report.id,
            "task_name": task_name,
            "total_count": report.total_count or 0,
            "pass_count": report.pass_count or 0,
            "fail_count": report.fail_count or 0,
            "skip_count": report.skip_count or 0,
            "pass_rate": pass_rate,
            "duration": report.duration or 0,
            "status": report.status or "completed",
            "generated_at": str(report.generated_at) if report.generated_at else "",
            "steps": [
                {
                    "step_index": s.step_index,
                    "step_name": s.step_name or "",
                    "step_desc": s.step_desc or "",
                    "status": s.status or "skipped",
                    "duration": s.duration or 0,
                    "error_message": s.error_message or "",
                    "expected_screenshot": s.expected_screenshot or "",
                    "actual_screenshot": s.actual_screenshot or "",
                }
                for s in steps
            ]
        }
    
    def _load_template(self, name: str) -> Template:
        template_path = self.template_dir / name
        if not template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as f:
            return Template(f.read())
```

### Step 4.5: 运行测试确认通过

- [ ] **运行测试确认通过**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/test_report_export.py -v
```

Expected: PASS

### Step 4.6: 提交

- [ ] **提交导出服务**

```bash
git add backend/core/report_export.py backend/templates/ backend/tests/test_report_export.py
git commit -m "feat: add report export service with HTML/PDF support"
```

---

## Task 5: 前端项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/types/report.ts`
- Create: `frontend/src/api/report.ts`

### Step 5.1: 初始化 Vue3 项目

- [ ] **初始化 Vue3 + TypeScript 项目**

```bash
cd D:\毕设git\ai-ui-test-platform\frontend; npm create vite@latest . -- --template vue-ts
```

### Step 5.2: 安装依赖

- [ ] **安装项目依赖**

```bash
cd D:\毕设git\ai-ui-test-platform\frontend; npm install; npm install element-plus echarts axios vue-router@4
```

### Step 5.3: 创建类型定义

- [ ] **创建报告类型定义**

创建文件 `frontend/src/types/report.ts`:

```typescript
export interface ReportStep {
  id: number
  step_index: number
  step_name: string
  step_desc: string
  status: 'passed' | 'failed' | 'skipped'
  duration: number
  error_message: string | null
  expected_screenshot: string | null
  actual_screenshot: string | null
}

export interface TestReport {
  id: number
  task_id: number
  task_name: string
  total_count: number
  pass_count: number
  fail_count: number
  skip_count: number
  pass_rate: number
  duration: number
  status: string
  generated_at: string
  steps: ReportStep[]
}

export interface TrendData {
  date: string
  total: number
  passed: number
  failed: number
  pass_rate: number
  avg_duration: number
}

export interface TrendsResponse {
  project_id: number | null
  date_range: { start: string; end: string }
  trends: TrendData[]
  summary: {
    total_reports: number
    avg_pass_rate: number
    total_tests: number
  }
}
```

### Step 5.4: 创建 API 服务

- [ ] **创建报告 API 服务**

创建文件 `frontend/src/api/report.ts`:

```typescript
import axios from 'axios'
import type { TestReport, TrendsResponse } from '../types/report'

const API_BASE = '/api/v2'

export async function getReportDetail(reportId: number): Promise<TestReport> {
  const { data } = await axios.get(`${API_BASE}/reports/${reportId}`)
  return data.data
}

export async function getReportTrends(projectId?: number, days: number = 30): Promise<TrendsResponse> {
  const params: Record<string, any> = { days }
  if (projectId) params.project_id = projectId
  const { data } = await axios.get(`${API_BASE}/reports/trends/overview`, { params })
  return data.data
}

export async function exportReport(reportId: number, format: 'pdf' | 'html'): Promise<Blob> {
  const { data } = await axios.get(`${API_BASE}/reports/${reportId}/export`, {
    params: { format },
    responseType: 'blob'
  })
  return data
}

export async function getReportsList(taskId?: number) {
  const params: Record<string, any> = {}
  if (taskId) params.task_id = taskId
  const { data } = await axios.get(`${API_BASE}/reports`, { params })
  return data
}
```

### Step 5.5: 创建路由配置

- [ ] **创建路由配置**

创建文件 `frontend/src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/reports/trends'
    },
    {
      path: '/reports/trends',
      name: 'ProjectTrends',
      component: () => import('../views/ProjectTrends.vue')
    },
    {
      path: '/reports/:id',
      name: 'ReportDetail',
      component: () => import('../views/ReportDetail.vue'),
      props: true
    }
  ]
})

export default router
```

### Step 5.6: 配置 main.ts

- [ ] **配置 main.ts**

创建文件 `frontend/src/main.ts`:

```typescript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
```

### Step 5.7: 配置 App.vue

- [ ] **配置 App.vue**

创建文件 `frontend/src/App.vue`:

```vue
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
</script>

<style>
body {
  margin: 0;
  font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f5f7fa;
}
</style>
```

### Step 5.8: 提交

- [ ] **提交前端项目初始化**

```bash
cd D:\毕设git\ai-ui-test-platform; git add frontend/
git commit -m "feat: initialize Vue3 frontend project with TypeScript"
```

---

## Task 6: 前端报告详情页

**Files:**
- Create: `frontend/src/views/ReportDetail.vue`
- Create: `frontend/src/components/report/SummaryCard.vue`
- Create: `frontend/src/components/report/StepTable.vue`
- Create: `frontend/src/components/report/ScreenshotCompare.vue`
- Create: `frontend/src/components/report/ExportButton.vue`
- Create: `frontend/src/components/charts/PieChart.vue`

### Step 6.1: 创建 SummaryCard 组件

- [ ] **创建 SummaryCard 组件**

创建文件 `frontend/src/components/report/SummaryCard.vue`:

```vue
<template>
  <el-card class="summary-card" :body-style="{ padding: '20px' }">
    <div class="stat-value" :style="{ color: color }">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  value: number | string
  label: string
  color?: string
}>()
</script>

<style scoped>
.summary-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { font-size: 14px; color: #909399; margin-top: 8px; }
</style>
```

### Step 6.2: 创建 PieChart 组件

- [ ] **创建 PieChart 组件**

创建文件 `frontend/src/components/charts/PieChart.vue`:

```vue
<template>
  <div ref="chartRef" style="width: 100%; height: 300px;"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  passed: number
  failed: number
  skipped: number
}>()

const chartRef = ref<HTMLElement>()

onMounted(() => {
  renderChart()
})

watch(() => [props.passed, props.failed, props.skipped], () => {
  renderChart()
})

function renderChart() {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      data: [
        { value: props.passed, name: '通过', itemStyle: { color: '#67C23A' } },
        { value: props.failed, name: '失败', itemStyle: { color: '#F56C6C' } },
        { value: props.skipped, name: '跳过', itemStyle: { color: '#E6A23C' } },
      ].filter(d => d.value > 0)
    }]
  })
}
</script>
```

### Step 6.3: 创建 StepTable 组件

- [ ] **创建 StepTable 组件**

创建文件 `frontend/src/components/report/StepTable.vue`:

```vue
<template>
  <el-table :data="steps" stripe style="width: 100%">
    <el-table-column type="expand">
      <template #default="{ row }">
        <div style="padding: 15px;">
          <p v-if="row.step_desc"><strong>描述:</strong> {{ row.step_desc }}</p>
          <p v-if="row.error_message" style="color: #F56C6C;"><strong>错误:</strong> {{ row.error_message }}</p>
          <ScreenshotCompare
            v-if="row.actual_screenshot || row.expected_screenshot"
            :expected="row.expected_screenshot"
            :actual="row.actual_screenshot"
          />
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="step_index" label="序号" width="80" />
    <el-table-column prop="step_name" label="步骤名称" />
    <el-table-column prop="status" label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="duration" label="耗时(ms)" width="120" />
  </el-table>
</template>

<script setup lang="ts">
import type { ReportStep } from '../../types/report'
import ScreenshotCompare from './ScreenshotCompare.vue'

defineProps<{
  steps: ReportStep[]
}>()

function statusType(status: string) {
  return status === 'passed' ? 'success' : status === 'failed' ? 'danger' : 'warning'
}

function statusText(status: string) {
  return status === 'passed' ? '通过' : status === 'failed' ? '失败' : '跳过'
}
</script>
```

### Step 6.4: 创建 ScreenshotCompare 组件

- [ ] **创建 ScreenshotCompare 组件**

创建文件 `frontend/src/components/report/ScreenshotCompare.vue`:

```vue
<template>
  <div class="screenshot-compare" v-if="expected || actual">
    <div class="screenshot-item" v-if="expected">
      <h4>预期截图</h4>
      <img :src="expected" loading="lazy" @error="onImgError" />
    </div>
    <div class="screenshot-item" v-if="actual">
      <h4>实际截图</h4>
      <img :src="actual" loading="lazy" @error="onImgError" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  expected: string | null
  actual: string | null
}>()

function onImgError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
.screenshot-compare { display: flex; gap: 20px; margin-top: 10px; }
.screenshot-item { flex: 1; }
.screenshot-item h4 { margin: 0 0 8px; font-size: 14px; color: #606266; }
.screenshot-item img { max-width: 100%; border: 1px solid #ebeef5; border-radius: 4px; }
</style>
```

### Step 6.5: 创建 ExportButton 组件

- [ ] **创建 ExportButton 组件**

创建文件 `frontend/src/components/report/ExportButton.vue`:

```vue
<template>
  <el-dropdown @command="handleExport">
    <el-button type="primary">
      导出报告 <el-icon class="el-icon--right"><arrow-down /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
        <el-dropdown-item command="html">导出 HTML</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ArrowDown } from '@element-plus/icons-vue'
import { exportReport } from '../../api/report'

const props = defineProps<{
  reportId: number
}>()

async function handleExport(format: string) {
  try {
    const blob = await exportReport(props.reportId, format as 'pdf' | 'html')
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `report_${props.reportId}.${format}`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出失败:', error)
  }
}
</script>
```

### Step 6.6: 创建 ReportDetail 页面

- [ ] **创建 ReportDetail 页面**

创建文件 `frontend/src/views/ReportDetail.vue`:

```vue
<template>
  <div class="report-detail" v-loading="loading">
    <div class="page-header">
      <el-page-header @back="goBack" :content="'测试报告 #' + id" />
      <ExportButton v-if="report" :report-id="Number(id)" />
    </div>

    <template v-if="report">
      <el-row :gutter="20" class="summary-row">
        <el-col :span="6"><SummaryCard :value="report.total_count" label="总步骤数" color="#409EFF" /></el-col>
        <el-col :span="6"><SummaryCard :value="report.pass_count" label="通过" color="#67C23A" /></el-col>
        <el-col :span="6"><SummaryCard :value="report.fail_count" label="失败" color="#F56C6C" /></el-col>
        <el-col :span="6"><SummaryCard :value="report.skip_count" label="跳过" color="#E6A23C" /></el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <PieChart :passed="report.pass_count" :failed="report.fail_count" :skipped="report.skip_count" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <div class="info-list">
              <div class="info-item"><span class="label">通过率</span><span class="value" :style="{ color: report.pass_rate >= 80 ? '#67C23A' : '#F56C6C' }">{{ report.pass_rate }}%</span></div>
              <div class="info-item"><span class="label">总耗时</span><span class="value">{{ report.duration }}秒</span></div>
              <div class="info-item"><span class="label">状态</span><span class="value">{{ report.status }}</span></div>
              <div class="info-item"><span class="label">生成时间</span><span class="value">{{ report.generated_at }}</span></div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="steps-card">
        <template #header><span>步骤详情</span></template>
        <StepTable :steps="report.steps" />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getReportDetail } from '../api/report'
import type { TestReport } from '../types/report'
import SummaryCard from '../components/report/SummaryCard.vue'
import StepTable from '../components/report/StepTable.vue'
import PieChart from '../components/charts/PieChart.vue'
import ExportButton from '../components/report/ExportButton.vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const loading = ref(false)
const report = ref<TestReport | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    report.value = await getReportDetail(Number(id))
  } catch (error) {
    console.error('加载报告失败:', error)
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push('/reports/trends')
}
</script>

<style scoped>
.report-detail { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.summary-row { margin-bottom: 20px; }
.info-list { padding: 10px; }
.info-item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #ebeef5; }
.info-item .label { color: #909399; }
.info-item .value { font-weight: bold; }
.steps-card { margin-top: 20px; }
</style>
```

### Step 6.7: 提交

- [ ] **提交前端报告详情页**

```bash
cd D:\毕设git\ai-ui-test-platform; git add frontend/src/
git commit -m "feat: add ReportDetail page with charts and step table"
```

---

## Task 7: 前端历史趋势页

**Files:**
- Create: `frontend/src/views/ProjectTrends.vue`
- Create: `frontend/src/components/charts/LineChart.vue`
- Create: `frontend/src/components/charts/BarChart.vue`

### Step 7.1: 创建 LineChart 组件

- [ ] **创建 LineChart 组件**

创建文件 `frontend/src/components/charts/LineChart.vue`:

```vue
<template>
  <div ref="chartRef" style="width: 100%; height: 350px;"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  data: { date: string; value: number }[]
  title: string
  color?: string
}>()

const chartRef = ref<HTMLElement>()

onMounted(() => { renderChart() })
watch(() => props.data, () => { renderChart() }, { deep: true })

function renderChart() {
  if (!chartRef.value || !props.data.length) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: props.title, left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.data.map(d => d.date) },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{
      data: props.data.map(d => d.value),
      type: 'line',
      smooth: true,
      itemStyle: { color: props.color || '#409EFF' },
      areaStyle: { opacity: 0.1 }
    }]
  })
}
</script>
```

### Step 7.2: 创建 BarChart 组件

- [ ] **创建 BarChart 组件**

创建文件 `frontend/src/components/charts/BarChart.vue`:

```vue
<template>
  <div ref="chartRef" style="width: 100%; height: 350px;"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  data: { date: string; value: number }[]
  title: string
  color?: string
}>()

const chartRef = ref<HTMLElement>()

onMounted(() => { renderChart() })
watch(() => props.data, () => { renderChart() }, { deep: true })

function renderChart() {
  if (!chartRef.value || !props.data.length) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: props.title, left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.data.map(d => d.date) },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}s' } },
    series: [{
      data: props.data.map(d => d.value),
      type: 'bar',
      itemStyle: { color: props.color || '#67C23A', borderRadius: [4, 4, 0, 0] }
    }]
  })
}
</script>
```

### Step 7.3: 创建 ProjectTrends 页面

- [ ] **创建 ProjectTrends 页面**

创建文件 `frontend/src/views/ProjectTrends.vue`:

```vue
<template>
  <div class="project-trends" v-loading="loading">
    <div class="page-header">
      <h2>测试趋势</h2>
      <div class="filters">
        <el-select v-model="projectId" placeholder="选择项目" clearable style="width: 200px; margin-right: 10px;">
          <el-option label="全部项目" :value="null" />
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-select v-model="days" style="width: 120px;">
          <el-option label="近7天" :value="7" />
          <el-option label="近30天" :value="30" />
          <el-option label="近90天" :value="90" />
        </el-select>
      </div>
    </div>

    <template v-if="trendsData">
      <el-row :gutter="20" class="summary-row">
        <el-col :span="8"><SummaryCard :value="trendsData.summary.total_reports" label="总报告数" color="#409EFF" /></el-col>
        <el-col :span="8"><SummaryCard :value="trendsData.summary.avg_pass_rate + '%'" label="平均通过率" color="#67C23A" /></el-col>
        <el-col :span="8"><SummaryCard :value="trendsData.summary.total_tests" label="总测试数" color="#E6A23C" /></el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <LineChart :data="passRateData" title="通过率趋势" color="#67C23A" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <BarChart :data="durationData" title="耗时趋势" color="#409EFF" />
          </el-card>
        </el-col>
      </el-row>

      <el-card class="history-card">
        <template #header><span>历史报告</span></template>
        <el-table :data="trendsData.trends" stripe>
          <el-table-column prop="date" label="日期" />
          <el-table-column prop="total" label="总步骤" />
          <el-table-column prop="passed" label="通过" />
          <el-table-column prop="failed" label="失败" />
          <el-table-column prop="pass_rate" label="通过率">
            <template #default="{ row }">
              <span :style="{ color: row.pass_rate >= 80 ? '#67C23A' : '#F56C6C' }">{{ row.pass_rate }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="avg_duration" label="耗时(s)" />
        </el-table>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getReportTrends } from '../api/report'
import type { TrendsResponse } from '../types/report'
import SummaryCard from '../components/report/SummaryCard.vue'
import LineChart from '../components/charts/LineChart.vue'
import BarChart from '../components/charts/BarChart.vue'

const loading = ref(false)
const projectId = ref<number | null>(null)
const days = ref(30)
const trendsData = ref<TrendsResponse | null>(null)
const projects = ref<{ id: number; name: string }[]>([])

const passRateData = computed(() =>
  trendsData.value?.trends.map(t => ({ date: t.date, value: t.pass_rate })) || []
)

const durationData = computed(() =>
  trendsData.value?.trends.map(t => ({ date: t.date, value: t.avg_duration })) || []
)

async function fetchTrends() {
  loading.value = true
  try {
    trendsData.value = await getReportTrends(projectId.value || undefined, days.value)
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchTrends() })
watch([projectId, days], () => { fetchTrends() })
</script>

<style scoped>
.project-trends { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
.summary-row { margin-bottom: 20px; }
.history-card { margin-top: 20px; }
</style>
```

### Step 7.4: 提交

- [ ] **提交前端趋势页**

```bash
cd D:\毕设git\ai-ui-test-platform; git add frontend/src/
git commit -m "feat: add ProjectTrends page with charts and history table"
```

---

## Task 8: 最终验证和清理

### Step 8.1: 运行后端全部测试

- [ ] **运行后端全部测试**

```bash
cd D:\毕设git\ai-ui-test-platform; pytest backend/tests/ -v --tb=short
```

Expected: All tests pass

### Step 8.2: 验证前端构建

- [ ] **验证前端构建**

```bash
cd D:\毕设git\ai-ui-test-platform\frontend; npm run build
```

Expected: Build succeeds

### Step 8.3: 最终提交

- [ ] **最终提交**

```bash
cd D:\毕设git\ai-ui-test-platform; git add -A
git commit -m "feat: complete test report generation and visualization module"
```

### Step 8.4: 推送到远程

- [ ] **推送到远程**

```bash
cd D:\毕设git\ai-ui-test-platform; git push origin main
```

---

## 成功指标

| 指标 | 验证方式 |
|------|----------|
| 数据库模型扩展 | test_report_models.py |
| 报告生成服务 | test_report_generator.py |
| 导出服务 | test_report_export.py |
| API 接口 | test_report_api.py |
| 前端构建 | npm run build |
| 报告详情页 | /reports/:id |
| 趋势页 | /reports/trends |
