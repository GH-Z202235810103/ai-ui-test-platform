"""截图工具"""
from datetime import datetime
from pathlib import Path
from playwright.sync import Page
from backend.config import Config

def save_step_screenshot(page: Page, case_id: str, step_index: int) -> str:
    """
    保存步骤截图
    :param page: Playwright页面对象
    :param case_id: 测试用例ID
    :param step_index: 步骤索引（从0开始）
    :return: 截图相对路径
    """
    # 生成唯一文件名：用例ID_步骤索引_时间戳.png
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{case_id}_step_{step_index}_{timestamp}.png"
    save_path = Config.SCREENSHOT_DIR / filename
    
    # 保存截图
    page.screenshot(path=str(save_path), full_page=True)
    
    # 返回相对路径（便于前端访问）
    return f"screenshots/{filename}"