"""
系统监控和健康检查模块
"""
import psutil
import os
import time
from datetime import datetime
from typing import Dict, Any

class SystemMonitor:
    """系统监控类"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "os": os.name,
            "platform": psutil.os.name(),
            "version": psutil.os.version(),
            "machine": os.uname().machine,
            "hostname": os.uname().nodename
        }
    
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """获取CPU信息"""
        return {
            "count": psutil.cpu_count(logical=True),
            "physical_count": psutil.cpu_count(logical=False),
            "usage_percent": psutil.cpu_percent(interval=1),
            "stats": psutil.cpu_stats()._asdict()
        }
    
    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """获取内存信息"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent
        }
    
    @staticmethod
    def get_disk_info() -> Dict[str, Any]:
        """获取磁盘信息"""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """获取网络信息"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    
    @staticmethod
    def get_process_info() -> Dict[str, Any]:
        """获取进程信息"""
        process = psutil.Process(os.getpid())
        return {
            "pid": process.pid,
            "name": process.name(),
            "status": process.status(),
            "cpu_percent": process.cpu_percent(interval=1),
            "memory_percent": process.memory_percent(),
            "memory_info": process.memory_info()._asdict(),
            "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
        }
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """获取健康状态"""
        try:
            # 检查CPU使用率
            cpu_usage = psutil.cpu_percent(interval=0.1)
            cpu_healthy = cpu_usage < 90
            
            # 检查内存使用率
            memory = psutil.virtual_memory()
            memory_healthy = memory.percent < 90
            
            # 检查磁盘使用率
            disk = psutil.disk_usage('/')
            disk_healthy = disk.percent < 90
            
            # 检查系统负载
            load_healthy = True
            if hasattr(psutil, 'getloadavg'):
                load = psutil.getloadavg()
                cpu_count = psutil.cpu_count(logical=True)
                load_healthy = all(l < cpu_count for l in load)
            
            # 综合健康状态
            overall_healthy = all([cpu_healthy, memory_healthy, disk_healthy, load_healthy])
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "cpu": {
                        "status": "healthy" if cpu_healthy else "unhealthy",
                        "usage_percent": cpu_usage
                    },
                    "memory": {
                        "status": "healthy" if memory_healthy else "unhealthy",
                        "usage_percent": memory.percent
                    },
                    "disk": {
                        "status": "healthy" if disk_healthy else "unhealthy",
                        "usage_percent": disk.percent
                    },
                    "load": {
                        "status": "healthy" if load_healthy else "unhealthy"
                    }
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    @staticmethod
    def get_full_status() -> Dict[str, Any]:
        """获取完整状态"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": SystemMonitor.get_system_info(),
            "cpu": SystemMonitor.get_cpu_info(),
            "memory": SystemMonitor.get_memory_info(),
            "disk": SystemMonitor.get_disk_info(),
            "network": SystemMonitor.get_network_info(),
            "process": SystemMonitor.get_process_info(),
            "health": SystemMonitor.get_health_status()
        }
