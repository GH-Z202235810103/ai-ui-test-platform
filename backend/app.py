"""
FastAPI主应用 - AI UI自动化测试平台
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

# 设置标准输出和标准错误为 UTF-8 编码，解决 Windows 系统上的编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    API_HOST,
    API_PORT,
    API_PREFIX,
    CORS_ORIGINS,
    BASE_DIR,
    LOG_LEVEL,
    LOG_FORMAT
)
import logging

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 AI UI自动化测试平台启动中...")
    
    try:
        from database import init_database
        init_database()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.warning(f"⚠️ 数据库连接失败，将使用文件存储: {e}")
    
    logger.info("✅ 系统初始化完成")
    
    yield
    
    logger.info("👋 AI UI自动化测试平台已关闭")

app = FastAPI(
    title="AI UI自动化测试平台",
    description="基于AI与行为驱动的UI自动化测试平台",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api import api_router
app.include_router(api_router, prefix=API_PREFIX)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "ai-ui-test-platform",
        "version": "1.0.0"
    }

@app.api_route("/@vite/client", methods=["GET", "POST", "PUT", "DELETE"])
async def vite_client():
    """处理Trae IDE预览的Vite请求"""
    return {"status": "ok"}

screenshots_dir = BASE_DIR / "backend" / "screenshots"
screenshots_dir.mkdir(parents=True, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")
logger.info(f"✅ 截图目录已挂载: {screenshots_dir}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🌐 服务器启动: http://{API_HOST}:{API_PORT}")
    logger.info(f"📚 API文档: http://{API_HOST}:{API_PORT}/docs")
    
    uvicorn.run(
        "app:app",
        host=API_HOST,
        port=API_PORT,
        log_level="info",
        access_log=True,
        reload=True
    )
    