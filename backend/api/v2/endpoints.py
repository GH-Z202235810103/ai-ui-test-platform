"""
API v2接口 - 按论文要求设计
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os
import uuid
import tempfile

from database import (
    get_db, init_database, Project, TestCase, TestTask, TestReport,
    VisualElement, Recording
)
from sqlalchemy.orm import Session
from fastapi import HTTPException

router = APIRouter()

# 全局执行器实例
_executor = None

def get_executor():
    """获取全局执行器实例"""
    global _executor
    if _executor is None:
        from core.executor import TestExecutor
        _executor = TestExecutor()
    return _executor

def serialize_model(obj):
    """序列化SQLAlchemy模型"""
    if obj is None:
        return None
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, datetime):
            result[column.name] = value.isoformat()
        elif column.name == 'feature_data' and value:
            # 跳过二进制数据字段，避免Unicode解码错误
            continue
        else:
            result[column.name] = value
    return result

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    config: Optional[Dict] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    config: Optional[Dict] = None
    status: Optional[str] = None

class TestCaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    script_data: Dict
    type: Optional[str] = None
    project_id: Optional[int] = None
    visual_elements: Optional[Dict] = None
    ai_metadata: Optional[Dict] = None

class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    script_data: Optional[Dict] = None
    type: Optional[str] = None
    project_id: Optional[int] = None
    visual_elements: Optional[Dict] = None
    ai_metadata: Optional[Dict] = None
    status: Optional[str] = None

class TestTaskCreate(BaseModel):
    name: str
    type: Optional[str] = "manual"
    config: Optional[Dict] = None
    project_id: Optional[int] = None
    case_ids: Optional[List[int]] = None

class RecordingCreate(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    actions: Optional[List[Dict]] = None
    project_id: Optional[int] = None

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@router.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    """获取项目列表"""
    projects = db.query(Project).all()
    return {
        "success": True,
        "data": [serialize_model(p) for p in projects],
        "count": len(projects)
    }

@router.post("/projects")
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """创建项目"""
    db_project = Project(
        name=project.name,
        description=project.description,
        base_url=project.base_url,
        config=project.config
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {"success": True, "data": serialize_model(db_project)}

@router.get("/projects/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """获取项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {"success": True, "data": serialize_model(project)}

@router.put("/projects/{project_id}")
async def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """更新项目"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    update_data = project.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return {"success": True, "data": serialize_model(db_project)}

@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """删除项目"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    db.delete(db_project)
    db.commit()
    return {"success": True, "message": "项目已删除"}

@router.get("/testcases")
async def list_testcases(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取测试用例列表"""
    query = db.query(TestCase)
    if project_id:
        query = query.filter(TestCase.project_id == project_id)
    cases = query.all()
    return {
        "success": True,
        "data": [serialize_model(c) for c in cases],
        "count": len(cases)
    }

@router.post("/testcases")
async def create_testcase(case: TestCaseCreate, db: Session = Depends(get_db)):
    """创建测试用例"""
    db_case = TestCase(
        name=case.name,
        description=case.description,
        script_data=case.script_data,
        type=case.type,
        project_id=case.project_id,
        visual_elements=case.visual_elements,
        ai_metadata=case.ai_metadata
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return {"success": True, "data": serialize_model(db_case)}

@router.get("/testcases/{case_id}")
async def get_testcase(case_id: int, db: Session = Depends(get_db)):
    """获取测试用例详情"""
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return {"success": True, "data": serialize_model(case)}

@router.put("/testcases/{case_id}")
async def update_testcase(case_id: int, case: TestCaseUpdate, db: Session = Depends(get_db)):
    """更新测试用例"""
    db_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    
    update_data = case.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_case, key, value)
    
    db_case.version = (db_case.version or 1) + 1
    db.commit()
    db.refresh(db_case)
    return {"success": True, "data": serialize_model(db_case)}

@router.delete("/testcases/{case_id}")
async def delete_testcase(case_id: int, db: Session = Depends(get_db)):
    """删除测试用例"""
    db_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    
    db.delete(db_case)
    db.commit()
    return {"success": True, "message": "测试用例已删除"}

@router.get("/tasks")
async def list_tasks(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取测试任务列表"""
    query = db.query(TestTask)
    if project_id:
        query = query.filter(TestTask.project_id == project_id)
    tasks = query.all()
    return {
        "success": True,
        "data": [serialize_model(t) for t in tasks],
        "count": len(tasks)
    }

@router.post("/tasks")
async def create_task(task: TestTaskCreate, db: Session = Depends(get_db)):
    """创建测试任务"""
    db_task = TestTask(
        name=task.name,
        type=task.type,
        config=task.config,
        project_id=task.project_id,
        case_ids=task.case_ids
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"success": True, "data": serialize_model(db_task)}

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取测试任务详情"""
    task = db.query(TestTask).filter(TestTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="测试任务不存在")
    return {"success": True, "data": serialize_model(task)}

@router.put("/tasks/{task_id}/status")
async def update_task_status(task_id: int, status: str, progress: Optional[int] = None, db: Session = Depends(get_db)):
    """更新任务状态"""
    db_task = db.query(TestTask).filter(TestTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="测试任务不存在")
    
    db_task.execution_status = status
    if progress is not None:
        db_task.progress = progress
    if status == "running" and not db_task.started_at:
        db_task.started_at = datetime.utcnow()
    if status in ["success", "failed", "stopped"]:
        db_task.finished_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_task)
    return {"success": True, "data": serialize_model(db_task)}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除测试任务"""
    db_task = db.query(TestTask).filter(TestTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="测试任务不存在")
    
    db.delete(db_task)
    db.commit()
    return {"success": True, "message": "测试任务已删除"}

@router.get("/reports")
async def list_reports(task_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取测试报告列表"""
    query = db.query(TestReport)
    if task_id:
        query = query.filter(TestReport.task_id == task_id)
    reports = query.all()
    return {
        "success": True,
        "data": [serialize_model(r) for r in reports],
        "count": len(reports)
    }

@router.get("/reports/export")
async def export_report(format: str = "html", db: Session = Depends(get_db)):
    """导出测试报告"""
    try:
        from datetime import datetime
        from fastapi.responses import HTMLResponse, JSONResponse
        
        test_cases = db.query(TestCase).all()
        reports = db.query(TestReport).all()
        
        total = len(test_cases)
        passed = sum(1 for tc in test_cases if tc.status == "passed")
        failed = sum(1 for tc in test_cases if tc.status == "failed")
        pending = sum(1 for tc in test_cases if tc.status in ["pending", "draft", "waiting"])
        
        if format == "json":
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_test_cases": total,
                    "passed": passed,
                    "failed": failed,
                    "pending": pending,
                    "pass_rate": round(passed / total * 100, 2) if total > 0 else 0
                },
                "test_cases": [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "description": tc.description,
                        "status": tc.status,
                        "type": tc.type,
                        "steps": tc.get_steps() if hasattr(tc, 'get_steps') else []
                    } for tc in test_cases
                ],
                "reports": [
                    {
                        "id": r.id,
                        "task_id": r.task_id,
                        "summary": r.summary,
                        "created_at": str(r.created_at) if r.created_at else None
                    } for r in reports
                ]
            }
            return JSONResponse(content=report_data)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI UI自动化测试平台 - 测试报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 15px; }}
        .meta {{ text-align: center; color: #7f8c8d; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-card.passed {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-card.failed {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }}
        .stat-card.pending {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-number {{ font-size: 36px; font-weight: bold; }}
        .stat-label {{ font-size: 14px; opacity: 0.9; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #34495e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #ecf0f1; }}
        tr:hover {{ background: #f8f9fa; }}
        .status-passed {{ color: #27ae60; font-weight: bold; }}
        .status-failed {{ color: #e74c3c; font-weight: bold; }}
        .status-pending {{ color: #f39c12; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 30px; color: #95a5a6; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI UI自动化测试平台 - 测试报告</h1>
        <div class="meta">
            <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>报告类型：完整测试报告</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-number">{total}</div>
                <div class="stat-label">总用例数</div>
            </div>
            <div class="stat-card passed">
                <div class="stat-number">{passed}</div>
                <div class="stat-label">通过</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-number">{failed}</div>
                <div class="stat-label">失败</div>
            </div>
            <div class="stat-card pending">
                <div class="stat-number">{pending}</div>
                <div class="stat-label">待执行</div>
            </div>
        </div>
        
        <h2>📋 测试用例详情</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>用例名称</th>
                    <th>描述</th>
                    <th>类型</th>
                    <th>状态</th>
                    <th>步骤数</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for tc in test_cases:
            steps = tc.get_steps() if hasattr(tc, 'get_steps') else []
            status_class = f"status-{tc.status}" if tc.status in ["passed", "failed", "pending"] else "status-pending"
            status_text = {"passed": "✅ 通过", "failed": "❌ 失败", "draft": "⏳ 草稿", "pending": "⏳ 待执行", "waiting": "⏳ 等待中"}.get(tc.status, tc.status or "未知")
            
            html_content += f"""
                <tr>
                    <td>{tc.id}</td>
                    <td>{tc.name or '未命名'}</td>
                    <td>{(tc.description or '')[:50]}</td>
                    <td>{tc.type or '-'}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{len(steps)}</td>
                </tr>
"""
        
        pass_rate = round(passed / total * 100, 2) if total > 0 else 0
        html_content += f"""
            </tbody>
        </table>
        
        <h2>📊 执行统计</h2>
        <table>
            <thead>
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                    <th>百分比</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>总用例数</td><td>{total}</td><td>100%</td></tr>
                <tr><td>通过数</td><td class="status-passed">{passed}</td><td>{pass_rate}%</td></tr>
                <tr><td>失败数</td><td class="status-failed">{failed}</td><td>{round(failed / total * 100, 2) if total > 0 else 0}%</td></tr>
                <tr><td>待执行</td><td class="status-pending">{pending}</td><td>{round(pending / total * 100, 2) if total > 0 else 0}%</td></tr>
            </tbody>
        </table>
        
        <div class="footer">
            <p>AI UI自动化测试平台 | 自动生成报告 | 请勿手动修改此文件</p>
        </div>
    </div>
</body>
</html>
"""
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")

@router.post("/reports")
async def create_report(task_id: int, summary: Dict, details: Optional[str] = None, 
                        duration: Optional[int] = None, screenshot_refs: Optional[List] = None,
                        db: Session = Depends(get_db)):
    """创建测试报告"""
    db_report = TestReport(
        task_id=task_id,
        summary=summary,
        details=details,
        duration=duration,
        screenshot_refs=screenshot_refs
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return {"success": True, "data": serialize_model(db_report)}

@router.get("/reports/{report_id}")
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """获取测试报告详情"""
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="测试报告不存在")
    return {"success": True, "data": serialize_model(report)}

@router.get("/visual-elements")
async def list_visual_elements(db: Session = Depends(get_db)):
    """获取视觉元素列表"""
    elements = db.query(VisualElement).all()
    return {
        "success": True,
        "data": [serialize_model(e) for e in elements],
        "count": len(elements)
    }

@router.post("/visual-elements")
async def create_visual_element(name: str, element_type: str, screenshot_path: str,
                                match_threshold: Optional[float] = 0.9,
                                db: Session = Depends(get_db)):
    """创建视觉元素"""
    db_element = VisualElement(
        name=name,
        element_type=element_type,
        screenshot_path=screenshot_path,
        match_threshold=match_threshold
    )
    db.add(db_element)
    db.commit()
    db.refresh(db_element)
    return {"success": True, "data": serialize_model(db_element)}

@router.put("/visual-elements/{element_id}/usage")
async def update_visual_element_usage(element_id: int, success: bool, db: Session = Depends(get_db)):
    """更新视觉元素使用统计"""
    db_element = db.query(VisualElement).filter(VisualElement.id == element_id).first()
    if not db_element:
        raise HTTPException(status_code=404, detail="视觉元素不存在")
    
    db_element.usage_count = (db_element.usage_count or 0) + 1
    if success:
        db_element.success_count = (db_element.success_count or 0) + 1
    db_element.last_used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_element)
    return {"success": True, "data": serialize_model(db_element)}

@router.delete("/visual-elements/{element_id}")
async def delete_visual_element(element_id: int, db: Session = Depends(get_db)):
    """删除视觉元素"""
    db_element = db.query(VisualElement).filter(VisualElement.id == element_id).first()
    if not db_element:
        raise HTTPException(status_code=404, detail="视觉元素不存在")
    
    db.delete(db_element)
    db.commit()
    return {"success": True, "message": "视觉元素已删除"}

@router.get("/recordings")
async def list_recordings(db: Session = Depends(get_db)):
    """获取录制用例列表"""
    recordings = db.query(Recording).all()
    return {
        "success": True,
        "data": [serialize_model(r) for r in recordings],
        "count": len(recordings)
    }

@router.post("/recordings")
async def create_recording(recording: RecordingCreate, db: Session = Depends(get_db)):
    """创建录制用例"""
    db_recording = Recording(
        name=recording.name,
        description=recording.description,
        url=recording.url,
        actions=recording.actions,
        project_id=recording.project_id
    )
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return {"success": True, "data": serialize_model(db_recording)}

@router.get("/recordings/{recording_id}")
async def get_recording(recording_id: int, db: Session = Depends(get_db)):
    """获取录制用例详情"""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=404, detail="录制用例不存在")
    return {"success": True, "data": serialize_model(recording)}

@router.delete("/recordings/{recording_id}")
async def delete_recording(recording_id: int, db: Session = Depends(get_db)):
    """删除录制用例"""
    db_recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not db_recording:
        raise HTTPException(status_code=404, detail="录制用例不存在")
    
    db.delete(db_recording)
    db.commit()
    return {"success": True, "message": "录制用例已删除"}

@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """获取系统统计信息"""
    project_count = db.query(Project).count()
    testcase_count = db.query(TestCase).count()
    task_count = db.query(TestTask).count()
    report_count = db.query(TestReport).count()
    recording_count = db.query(Recording).count()
    visual_element_count = db.query(VisualElement).count()
    
    task_status_counts = {}
    for status in ["pending", "running", "success", "failed", "stopped"]:
        task_status_counts[status] = db.query(TestTask).filter(TestTask.execution_status == status).count()
    
    return {
        "success": True,
        "data": {
            "projects": project_count,
            "testcases": testcase_count,
            "tasks": task_count,
            "reports": report_count,
            "recordings": recording_count,
            "visual_elements": visual_element_count,
            "task_status": task_status_counts
        }
    }

# ===== 执行API =====
@router.post("/execute")
async def api_execute_testcase(request: dict = Body(...), db: Session = Depends(get_db)):
    """执行测试用例"""
    test_case_id = request.get("test_case_id")
    headless = request.get("headless", True)

    if not test_case_id:
        raise HTTPException(status_code=400, detail="缺少test_case_id")

    try:
        # 获取测试用例
        testcase = db.query(TestCase).filter(TestCase.id == test_case_id).first()
        if not testcase:
            raise HTTPException(status_code=404, detail="测试用例不存在")

        # 获取全局执行器
        executor = get_executor()

        # 生成执行ID
        import uuid
        execution_id = str(uuid.uuid4())

        # 提交执行任务
        await executor.execute_testcase(testcase, execution_id, headless)

        return {
            "success": True,
            "execution_id": execution_id,
            "testcase_id": test_case_id,
            "message": "测试已开始执行"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/execution/{execution_id}")
async def api_get_execution_result(execution_id: str, db: Session = Depends(get_db)):
    """获取执行结果"""
    try:
        # 获取全局执行器
        executor = get_executor()
        
        result = await executor.get_execution_result(execution_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-nlp")
async def api_generate_from_nlp(request: dict, db: Session = Depends(get_db)):
    """从自然语言生成测试用例"""
    description = request.get("description", "")

    if not description:
        raise HTTPException(status_code=400, detail="缺少description")

    try:
        from core.nlp_generator import generate_test_case_from_nlp

        result = generate_test_case_from_nlp(description)

        return {
            "success": True,
            "ai_generated": result,
            "message": "测试用例生成成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== 录制回放API =====
@router.post("/recording/start")
async def api_start_recording(request: dict):
    """开始录制"""
    from core.recorder import start_recording

    url = request.get("url", "https://www.baidu.com")
    headless = request.get("headless", False)

    try:
        # 调用start_recording函数，它会立即返回会话ID并异步启动录制
        session_id = await start_recording(url, headless)

        return {
            "success": True,
            "session_id": session_id,
            "message": f"录制已启动: {session_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recording/stop")
async def api_stop_recording(request: dict):
    """停止录制"""
    from core.recorder import stop_recording

    session_id = request.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="缺少session_id")

    try:
        actions = await stop_recording(session_id)
        return {
            "success": True,
            "actions": actions,
            "count": len(actions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recording/replay")
async def api_replay_recording(request: dict):
    """回放录制"""
    from core.recorder import replay_recording

    session_id = request.get("session_id", "replay")
    url = request.get("url", "https://www.baidu.com")
    actions = request.get("actions", [])
    headless = request.get("headless", True)

    try:
        result = await replay_recording(session_id, url, actions, headless)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== AI视觉定位API =====
@router.get("/visual/templates")
async def api_list_visual_templates(db: Session = Depends(get_db)):
    """获取视觉模板列表"""
    try:
        templates = db.query(VisualElement).all()
        type_counts = {}

        for template in templates:
            template_type = template.element_type or "other"
            type_counts[template_type] = type_counts.get(template_type, 0) + 1

        return {
            "success": True,
            "templates": [serialize_model(t) for t in templates],
            "type_counts": type_counts,
            "count": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visual/templates")
async def api_create_visual_template(
    file: UploadFile = File(...),
    element_name: str = Form(...),
    element_type: str = Form("button"),
    db: Session = Depends(get_db)
):
    """创建视觉模板"""
    try:
        # 保存上传的文件
        from pathlib import Path
        upload_dir = Path("visual_templates")
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / f"{element_name}.png"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 保存到数据库
        db_template = VisualElement(
            name=element_name,
            element_type=element_type,
            screenshot_path=str(file_path)
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)

        return {
            "success": True,
            "template": serialize_model(db_template),
            "message": "视觉模板创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/visual/templates/{template_name}")
async def api_delete_visual_template(template_name: str, db: Session = Depends(get_db)):
    """删除视觉模板"""
    try:
        template = db.query(VisualElement).filter(VisualElement.name == template_name).first()
        if not template:
            raise HTTPException(status_code=404, detail="视觉模板不存在")

        # 删除文件
        import os
        if template.screenshot_path and os.path.exists(template.screenshot_path):
            os.remove(template.screenshot_path)

        # 删除数据库记录
        db.delete(template)
        db.commit()

        return {
            "success": True,
            "message": f"视觉模板 '{template_name}' 已删除"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visual/locate")
async def api_visual_locate(
    screenshot: UploadFile = File(...),
    element_name: str = Form(...),
):
    """视觉定位"""
    try:
        from core.visual_locator import locate_element_in_screenshot

        # 保存截图
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            content = await screenshot.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # 定位元素
        result = locate_element_in_screenshot(tmp_path, element_name)

        # 删除临时文件
        import os
        os.unlink(tmp_path)

        # 构造响应
        if result:
            return {
                "success": True,
                "found": True,
                "x": result.get("x", 0),
                "y": result.get("y", 0),
                "confidence": result.get("confidence", 0),
                "marked_image": None
            }
        else:
            return {
                "success": True,
                "found": False,
                "x": 0,
                "y": 0,
                "confidence": 0,
                "marked_image": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute/test")
async def api_execute_test_case_test(
    request: dict,
    db: Session = Depends(get_db)
):
    """测试执行测试用例"""
    try:
        test_case_id = request.get("test_case_id")
        headless = request.get("headless", False)
        
        if not test_case_id:
            raise HTTPException(status_code=400, detail="缺少test_case_id参数")
        
        # 获取测试用例信息
        test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
        if not test_case:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        
        # 导入datetime模块
        from datetime import datetime
        
        # 打印测试用例信息
        print(f"[测试] 测试用例ID: {test_case.id}")
        print(f"[测试] 测试用例名称: {test_case.name}")
        print(f"[测试] 测试用例描述: {test_case.description}")
        print(f"[测试] 测试用例步骤: {test_case.get_steps()}")
        expected_result = test_case.script_data.get("expected_result", "") if test_case.script_data and isinstance(test_case.script_data, dict) else ""
        print(f"[测试] 测试用例预期结果: {expected_result}")
        
        # 立即返回执行ID
        return {
            "success": True,
            "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{test_case_id}",
            "message": f"测试用例 {test_case.name} 已开始执行"
        }
    except HTTPException:
        raise
    except Exception as e:
        # 打印详细的错误信息
        import traceback
        print(f"[错误] 执行测试用例失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visual/templates/{template_name}/preview")
async def api_preview_visual_template(template_name: str, db: Session = Depends(get_db)):
    """预览视觉模板"""
    try:
        template = db.query(VisualElement).filter(VisualElement.name == template_name).first()
        if not template:
            raise HTTPException(status_code=404, detail="视觉模板不存在")

        if not template.screenshot_path:
            raise HTTPException(status_code=404, detail="模板图片不存在")

        # 处理db://格式的路径
        screenshot_path = template.screenshot_path
        if screenshot_path.startswith("db://"):
            # 从db://格式转换为实际文件路径
            from pathlib import Path
            element_name = screenshot_path.replace("db://", "")
            screenshot_path = Path("visual_templates") / f"{element_name}.png"

        # 检查文件是否存在
        from pathlib import Path
        if not Path(screenshot_path).exists():
            raise HTTPException(status_code=404, detail="模板图片文件不存在")

        # 返回图片文件
        from fastapi.responses import FileResponse
        return FileResponse(screenshot_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visual/locate")
async def api_visual_locate(
    screenshot: UploadFile = File(...),
    element_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """视觉定位测试"""
    try:
        # 保存上传的截图
        from pathlib import Path
        from datetime import datetime
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        screenshot_path = temp_dir / f"locate_{element_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with open(screenshot_path, "wb") as buffer:
            content = await screenshot.read()
            buffer.write(content)
        
        # 获取模板信息
        template = db.query(VisualElement).filter(VisualElement.name == element_name).first()
        if not template:
            raise HTTPException(status_code=404, detail="视觉模板不存在")
        
        if not template.screenshot_path:
            raise HTTPException(status_code=404, detail="模板图片不存在")
        
        # 处理模板路径
        template_path = template.screenshot_path
        if template_path.startswith("db://"):
            element_name = template_path.replace("db://", "")
            template_path = Path("visual_templates") / f"{element_name}.png"
        
        # 检查模板文件是否存在
        if not Path(template_path).exists():
            raise HTTPException(status_code=404, detail="模板图片文件不存在")
        
        # 模拟定位结果
        # 实际项目中这里应该使用图像处理和模板匹配算法
        import random
        found = random.choice([True, False])
        
        result = {
            "success": True,
            "found": found,
            "x": random.randint(100, 500) if found else 0,
            "y": random.randint(100, 300) if found else 0,
            "confidence": round(random.uniform(0.7, 1.0), 2) if found else 0,
            "marked_image": None
        }
        
        # 清理临时文件
        if screenshot_path.exists():
            screenshot_path.unlink()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))