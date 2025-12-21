"""
backend/app.py - AI测试平台后端API主文件
更新版：使用模块化API路由
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# 导入API路由
from api.endpoints import router as api_router

app = FastAPI(
    title="AI UI自动化测试平台",
    description="基于AI与行为驱动的UI自动化测试平台 - 后端API",
    version="1.0.0"
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载API路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "🤖 AI UI自动化测试平台后端API",
        "version": "1.0.0",
        "author": "GH-Z202235810103",
        "endpoints": {
            "API文档": "/docs",
            "测试用例管理": "/api/testcases",
            "AI生成测试": "/api/generate-from-nlp",
            "执行测试": "/api/execute-playwright",
            "OpenCV功能": "/api/opencv-demo"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "ai-test-platform"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)