"""
API模块初始化
"""
from fastapi import APIRouter
from .v2 import router as v2_router
from .auth import router as auth_router
from .monitoring import router as monitoring_router

# 创建主路由器
api_router = APIRouter()

# 包含认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# 包含监控路由
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])

# 包含v2版本的路由
api_router.include_router(v2_router, prefix="/v2", tags=["v2"])
