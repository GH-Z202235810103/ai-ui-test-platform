"""
backend/app.py - AI测试平台后端API
基于PPT框架：测试数据管理与报告平台
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="AI UI自动化测试平台",
    description="基于AI与行为驱动的UI自动化测试平台 - 后端API",
    version="1.0.0"
)

# 允许跨域，便于前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class TestCase(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    steps: List[str]
    status: str = "pending"  # pending, running, passed, failed
    created_at: Optional[str] = None

class ExecutionRequest(BaseModel):
    testcase_id: str
    browser: str = "chromium"
    headless: bool = False

# 模拟数据库
test_cases_db = []

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # 可以在static目录放一个favicon.ico文件
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    # 或者返回空响应
    from fastapi.responses import Response
    return Response(status_code=204)

@app.get("/")
async def root():
    return {
        "message": "AI UI自动化测试平台后端API",
        "version": "1.0.0",
        "author": "GH-Z202235810103"
    }

@app.get("/testcases", response_model=List[TestCase])
async def get_testcases():
    """获取所有测试用例 - 测试数据管理"""
    return test_cases_db

@app.post("/testcases", response_model=TestCase)
async def create_testcase(testcase: TestCase):
    """创建测试用例"""
    import uuid
    from datetime import datetime
    
    testcase.id = str(uuid.uuid4())
    testcase.created_at = datetime.now().isoformat()
    test_cases_db.append(testcase.dict())
    return testcase

@app.post("/generate-from-nlp")
async def generate_from_nlp(description: str):
    """自然语言生成测试用例 - 对应PPT模块3"""
    try:
        # 这里会调用你的LLM服务
        return {
            "success": True,
            "description": description,
            "generated_steps": [
                "打开测试页面",
                "输入用户名和密码",
                "点击登录按钮",
                "验证登录成功"
            ],
            "message": "测试用例生成成功（模拟）"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
async def execute_test(request: ExecutionRequest):
    """执行测试用例 - 一键执行功能"""
    return {
        "success": True,
        "testcase_id": request.testcase_id,
        "status": "running",
        "message": "测试开始执行",
        "execution_id": "exec_123456"
    }

@app.get("/report/{execution_id}")
async def get_report(execution_id: str):
    """获取测试报告 - 可视化报告功能"""
    return {
        "execution_id": execution_id,
        "status": "passed",
        "duration": "15.3s",
        "screenshots": ["step1.png", "step2.png"],
        "details": "所有测试步骤执行成功"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)