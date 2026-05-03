"""
监控API端点
"""
from fastapi import APIRouter
from core.monitoring import SystemMonitor

router = APIRouter()

@router.get("/health")
async def health_check():
    """健康检查"""
    return SystemMonitor.get_health_status()

@router.get("/status")
async def system_status():
    """系统状态"""
    return SystemMonitor.get_full_status()

@router.get("/system")
async def system_info():
    """系统信息"""
    return SystemMonitor.get_system_info()

@router.get("/cpu")
async def cpu_info():
    """CPU信息"""
    return SystemMonitor.get_cpu_info()

@router.get("/memory")
async def memory_info():
    """内存信息"""
    return SystemMonitor.get_memory_info()

@router.get("/disk")
async def disk_info():
    """磁盘信息"""
    return SystemMonitor.get_disk_info()

@router.get("/network")
async def network_info():
    """网络信息"""
    return SystemMonitor.get_network_info()

@router.get("/process")
async def process_info():
    """进程信息"""
    return SystemMonitor.get_process_info()
