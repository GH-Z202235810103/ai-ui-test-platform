"""
AI视觉定位模块 - 基于OpenCV
"""
import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict
import os
from pathlib import Path
import json

class VisualLocator:
    """视觉定位器"""
    
    ELEMENT_TYPE_THRESHOLDS = {
        "button": 0.8,
        "input": 0.75,
        "link": 0.7,
        "icon": 0.7,
        "text": 0.65,
        "image": 0.75,
        "checkbox": 0.8,
        "dropdown": 0.75,
        "tab": 0.75,
        "menu": 0.7,
        "other": 0.7
    }
    
    def __init__(self, template_dir: str, match_threshold: float = 0.8):
        self.template_dir = Path(template_dir)
        self.match_threshold = match_threshold
        self.scale_range = (0.8, 1.2)
        self.scale_steps = 5
        self.templates = {}
        
        self._load_templates()
    
    def _load_templates(self):
        """加载所有视觉模板"""
        import urllib.parse
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for template_file in self.template_dir.glob("*.png"):
            safe_name = template_file.stem
            element_name = urllib.parse.unquote(safe_name)
            try:
                with open(str(template_file), 'rb') as f:
                    file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
                template = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if template is not None:
                    element_type = self._get_element_type(safe_name)
                    threshold = self._get_element_threshold(safe_name, element_type)
                    self.templates[element_name] = {
                        "template": template,
                        "path": str(template_file),
                        "threshold": threshold,
                        "element_type": element_type
                    }
                    print(f"[视觉定位] 加载模板: {element_name} (类型: {element_type}, 阈值: {threshold})")
            except Exception as e:
                print(f"[视觉定位] 加载模板失败 {element_name}: {e}")
    
    def _get_element_type(self, safe_name: str) -> str:
        """获取元素的类型"""
        type_file = self.template_dir / f"{safe_name}_type.json"
        if type_file.exists():
            with open(type_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("element_type", "other")
        return "other"
    
    def _get_element_threshold(self, safe_name: str, element_type: str) -> float:
        """获取元素的匹配阈值"""
        threshold_file = self.template_dir / f"{safe_name}_threshold.json"
        if threshold_file.exists():
            with open(threshold_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("threshold", self.match_threshold)
        return self.ELEMENT_TYPE_THRESHOLDS.get(element_type, self.match_threshold)
    
    def _save_element_threshold(self, safe_name: str, threshold: float):
        """保存元素的匹配阈值"""
        threshold_file = self.template_dir / f"{safe_name}_threshold.json"
        with open(threshold_file, 'w', encoding='utf-8') as f:
            json.dump({"threshold": threshold}, f, ensure_ascii=False, indent=2)
    
    def locate_element(
        self, 
        screenshot: np.ndarray, 
        element_name: str,
        scale_range: Tuple[float, float] = None,
        scale_steps: int = None
    ) -> Optional[Dict]:
        """
        定位元素
        
        Args:
            screenshot: 截图数组
            element_name: 元素名称
            scale_range: 缩放范围
            scale_steps: 缩放步数
        
        Returns:
            包含位置和匹配度的字典 {"x": int, "y": int, "confidence": float} 或 None
        """
        if element_name not in self.templates:
            print(f"[视觉定位] 模板不存在: {element_name}")
            return None
        
        template_data = self.templates[element_name]
        template = template_data["template"]
        threshold = template_data["threshold"]
        
        scale_range = scale_range or self.scale_range
        scale_steps = scale_steps or self.scale_steps
        
        best_match = None
        best_max_val = 0
        best_scale = 1.0
        
        scales = np.linspace(scale_range[0], scale_range[1], scale_steps)
        
        for scale in scales:
            # 缩放模板
            if scale != 1.0:
                scaled_template = cv2.resize(
                    template, 
                    None, 
                    fx=scale, 
                    fy=scale, 
                    interpolation=cv2.INTER_CUBIC
                )
            else:
                scaled_template = template
            
            # 模板匹配
            result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 检查是否是最佳匹配
            if max_val > best_max_val and max_val >= threshold:
                best_max_val = max_val
                best_match = max_loc
                best_scale = scale
        
        if best_match is not None:
            template_h, template_w = template.shape[:2]
            center_x = int(best_match[0] + template_w * best_scale / 2)
            center_y = int(best_match[1] + template_h * best_scale / 2)
            
            confidence = round(best_max_val, 3)
            print(f"[视觉定位] 找到元素: {element_name}, 匹配度: {confidence}, 缩放: {best_scale:.2f}")
            
            if best_max_val > threshold:
                import urllib.parse
                new_threshold = (threshold + best_max_val) / 2
                safe_name = urllib.parse.quote(element_name, safe='')
                self._save_element_threshold(safe_name, new_threshold)
            
            return {
                "x": center_x,
                "y": center_y,
                "confidence": confidence
            }
        
        print(f"[视觉定位] 未找到元素: {element_name}, 最高匹配度: {best_max_val:.3f}")
        return None
    
    def save_template(
        self, 
        screenshot: np.ndarray, 
        element_name: str,
        element_type: str = "button"
    ) -> bool:
        """
        保存视觉模板
        
        Args:
            screenshot: 截图数组
            element_name: 元素名称
            element_type: 元素类型
        
        Returns:
            是否保存成功
        """
        try:
            if not self.template_dir.exists():
                self.template_dir.mkdir(parents=True, exist_ok=True)
                print(f"[视觉定位] 创建模板目录: {self.template_dir}")
            
            import urllib.parse
            safe_name = urllib.parse.quote(element_name, safe='')
            template_path = self.template_dir / f"{safe_name}.png"
            print(f"[视觉定位] 尝试保存模板到: {template_path}")
            print(f"[视觉定位] 图片尺寸: {screenshot.shape if screenshot is not None else 'None'}")
            
            is_success, buffer = cv2.imencode(".png", screenshot)
            if is_success:
                with open(str(template_path), "wb") as f:
                    f.write(buffer)
                print(f"[视觉定位] 保存成功")
            else:
                print(f"[视觉定位] 编码失败")
                return False
            
            if template_path.exists():
                threshold = self.ELEMENT_TYPE_THRESHOLDS.get(element_type, self.match_threshold)
                
                type_file = self.template_dir / f"{safe_name}_type.json"
                with open(type_file, 'w', encoding='utf-8') as f:
                    json.dump({"element_type": element_type}, f, ensure_ascii=False, indent=2)
                
                self.templates[element_name] = {
                    "template": screenshot,
                    "path": str(template_path),
                    "threshold": threshold,
                    "element_type": element_type
                }
                print(f"[视觉定位] 保存模板成功: {element_name} (类型: {element_type}, 阈值: {threshold})")
                return True
            else:
                print(f"[视觉定位] 保存模板失败: 文件不存在")
                return False
            
        except Exception as e:
            print(f"[视觉定位] 保存模板异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def batch_locate(
        self, 
        screenshot: np.ndarray, 
        element_names: List[str]
    ) -> dict:
        """
        批量定位元素
        
        Args:
            screenshot: 截图数组
            element_names: 元素名称列表
        
        Returns:
            定位结果字典 {element_name: (x, y) or None}
        """
        results = {}
        
        for element_name in element_names:
            location = self.locate_element(screenshot, element_name)
            results[element_name] = location
        
        return results
    
    def get_template_info(self, element_name: str) -> Optional[dict]:
        """获取模板信息"""
        if element_name in self.templates:
            template_data = self.templates[element_name]
            template = template_data["template"]
            h, w = template.shape[:2]
            
            return {
                "element_name": element_name,
                "width": w,
                "height": h,
                "threshold": template_data["threshold"],
                "element_type": template_data.get("element_type", "other"),
                "path": template_data["path"]
            }
        
        return None
    
    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())
    
    def delete_template(self, element_name: str) -> bool:
        """删除模板"""
        import urllib.parse
        if element_name in self.templates:
            try:
                template_path = self.templates[element_name]["path"]
                if os.path.exists(template_path):
                    os.remove(template_path)
                
                safe_name = urllib.parse.quote(element_name, safe='')
                threshold_file = self.template_dir / f"{safe_name}_threshold.json"
                if threshold_file.exists():
                    os.remove(threshold_file)
                
                del self.templates[element_name]
                print(f"[视觉定位] 删除模板: {element_name}")
                return True
                
            except Exception as e:
                print(f"[视觉定位] 删除模板失败: {e}")
                return False
        
        return False

# 全局视觉定位器实例
_global_locator: Optional[VisualLocator] = None

def get_visual_locator(template_dir: str = None, match_threshold: float = 0.8) -> VisualLocator:
    """获取全局视觉定位器实例"""
    global _global_locator
    
    if _global_locator is None:
        from config import VISUAL_TEMPLATES_DIR, OPENCV_MATCH_THRESHOLD
        template_dir = template_dir or str(VISUAL_TEMPLATES_DIR)
        match_threshold = match_threshold or OPENCV_MATCH_THRESHOLD
        _global_locator = VisualLocator(template_dir, match_threshold)
    
    return _global_locator

def locate_element_in_screenshot(
    screenshot_path: str,
    element_name: str
) -> Optional[Tuple[int, int]]:
    """
    在截图中定位元素
    
    Args:
        screenshot_path: 截图路径
        element_name: 元素名称
    
    Returns:
        元素中心坐标 (x, y) 或 None
    """
    if not os.path.exists(screenshot_path):
        print(f"[视觉定位] 截图不存在: {screenshot_path}")
        return None
    
    try:
        with open(screenshot_path, 'rb') as f:
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        screenshot = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"[视觉定位] 读取截图失败: {e}")
        return None
    
    if screenshot is None:
        print(f"[视觉定位] 无法解析截图: {screenshot_path}")
        return None
    
    locator = get_visual_locator()
    return locator.locate_element(screenshot, element_name)