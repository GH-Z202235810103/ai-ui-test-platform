"""
API接口 
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os

from database import (
    get_db, init_database, Project, TestCase, TestTask, TestReport, 
    VisualElement, Recording
)
from sqlalchemy.orm import Session

router = APIRouter()

def serialize_model(obj):
    """序列化SQLAlchemy模型"""
    if obj is None:
        return None
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, datetime):
            result[column.name] = value.isoformat()
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
