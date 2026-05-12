"""
配置文件 - 系统配置管理
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础目录
BASE_DIR = Path(__file__).parent.parent

# API配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
API_PREFIX = os.getenv("API_PREFIX", "/api")

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + str(BASE_DIR / "backend" / "data" / "ai_ui_test_platform.db")
)

# CORS配置
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:8080,http://localhost:8081,http://localhost:8000,http://localhost:8001,http://127.0.0.1:8000,http://127.0.0.1:8001"
).split(",")

# 浏览器配置
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "True").lower() == "true"
PLAYWRIGHT_SLOW_MO = int(os.getenv("PLAYWRIGHT_SLOW_MO", "0"))
PLAYWRIGHT_VIEWPORT = {
    "width": int(os.getenv("PLAYWRIGHT_VIEWPORT_WIDTH", "1920")),
    "height": int(os.getenv("PLAYWRIGHT_VIEWPORT_HEIGHT", "1080"))
}

# OpenCV配置
OPENCV_MATCH_THRESHOLD = float(os.getenv("OPENCV_MATCH_THRESHOLD", "0.8"))
OPENCV_SCALE_RANGE = (0.8, 1.2)
OPENCV_SCALE_STEPS = 5

# 目录配置
SCREENSHOT_DIR = BASE_DIR / "backend" / "screenshots"
VISUAL_TEMPLATES_DIR = BASE_DIR / "backend" / "visual_templates"
DATA_DIR = BASE_DIR / "backend" / "data"

# 创建目录
SCREENSHOT_DIR.mkdir(exist_ok=True)
VISUAL_TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 测试配置
EXECUTION_TEST_TIMEOUT = 300

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
