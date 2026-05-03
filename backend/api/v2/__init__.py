"""
API v2模块初始化
"""
from fastapi import APIRouter
from .endpoints import router as v2_endpoints_router

# 创建v2版本的路由器
router = APIRouter()

# 包含v2版本的端点路由
router.include_router(v2_endpoints_router, tags=["v2"])