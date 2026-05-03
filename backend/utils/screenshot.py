"""
截图工具模块
"""
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np

def screenshot_to_base64(image_path: str) -> str:
    """
    将截图转换为base64编码
    
    Args:
        image_path: 截图路径
    
    Returns:
        base64编码的字符串
    """
    try:
        # 使用PIL读取图片
        with Image.open(image_path) as img:
            # 将图片转换为BytesIO对象
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            # 转换为base64编码
            base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{base64_str}"
    except Exception as e:
        print(f"[错误] 截图转换为base64失败: {e}")
        return ""

def cv2_to_base64(image: np.ndarray) -> str:
    """
    将cv2图像转换为base64编码
    
    Args:
        image: cv2图像数组
    
    Returns:
        base64编码的字符串
    """
    try:
        # 将cv2图像转换为BytesIO对象
        is_success, buffer = cv2.imencode('.png', image)
        if not is_success:
            return ""
        # 转换为base64编码
        base64_str = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{base64_str}"
    except Exception as e:
        print(f"[错误] cv2图像转换为base64失败: {e}")
        return ""

def base64_to_cv2(base64_str: str) -> np.ndarray:
    """
    将base64编码转换为cv2图像
    
    Args:
        base64_str: base64编码的字符串
    
    Returns:
        cv2图像数组
    """
    try:
        # 移除data:image/png;base64,前缀
        if base64_str.startswith('data:image'):
            base64_str = base64_str.split(',')[1]
        # 解码base64字符串
        image_data = base64.b64decode(base64_str)
        # 将数据转换为numpy数组
        nparr = np.frombuffer(image_data, np.uint8)
        # 解码为cv2图像
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"[错误] base64转换为cv2图像失败: {e}")
        return None
