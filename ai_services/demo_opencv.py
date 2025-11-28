import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import time
import os

def find_element_on_screen(template_path, confidence=0.8):
    """
    在屏幕上查找指定元素图像
    template_path: 要查找的元素截图路径
    confidence: 匹配置信度（0-1之间）
    """
    # 1. 读取模板图像（要查找的目标）
    print(f"正在加载模板图像: {template_path}")
    
    # 先检查文件是否存在
    if not os.path.exists(template_path):
        print(f"❌ 文件不存在: {template_path}")
        return None
        
    template = cv2.imread(template_path)
    if template is None:
        print(f"错误：无法读取模板图像 {template_path}")
        return None
    
    # 2. 截取整个屏幕
    print("正在截取屏幕...")
    try:
        screenshot = ImageGrab.grab()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)  # 转换颜色空间
    except Exception as e:
        print(f"❌ 截屏失败: {e}")
        return None
    
    # 3. 使用模板匹配算法
    print("正在进行图像匹配...")
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    
    # 4. 查找最佳匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(f"最高匹配度: {max_val:.3f} (阈值: {confidence})")
    
    # 5. 检查是否找到目标
    if max_val >= confidence:
        # 计算目标中心坐标
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        print(f"✅ 找到目标！坐标: ({center_x}, {center_y}), 置信度: {max_val:.3f}")
        return (center_x, center_y, max_val)  # 返回置信度
    else:
        print(f"❌ 未找到目标，最高置信度 {max_val:.3f} 低于阈值 {confidence}")
        return None

def safe_screenshot(bbox=None):
    """
    安全的屏幕截图函数
    """
    try:
        if bbox:
            return ImageGrab.grab(bbox=bbox)
        else:
            return ImageGrab.grab()
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        return None

def simple_capture_demo():
    """
    简化版截取演示 - 稳定可靠
    """
    print("\n=== 简化版截取演示 ===")
    print("将鼠标移动到目标位置，5秒后自动截取...")
    
    for i in range(5, 0, -1):
        print(f"{i}...", end=' ', flush=True)
        time.sleep(1)
    print("截取！")
    
    current_x, current_y = pyautogui.position()
    print(f"鼠标位置: ({current_x}, {current_y})")
    
    # 截取区域
    box_size = 100
    x1 = max(0, current_x - box_size//2)
    y1 = max(0, current_y - box_size//2)
    x2 = current_x + box_size//2
    y2 = current_y + box_size//2
    
    target_area = safe_screenshot((x1, y1, x2, y2))
    if target_area:
        target_area.save("simple_target.png")
        print(f"✅ 已保存截取区域: simple_target.png")
        
        # 显示截取的图像
        target_cv = np.array(target_area)
        target_cv = cv2.cvtColor(target_cv, cv2.COLOR_RGB2BGR)
        cv2.imshow("Captured Area", target_cv)
        print("按任意键关闭预览...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # 查找目标
        position = find_element_on_screen("simple_target.png", confidence=0.7)
        if position:
            x, y, confidence = position
            print(f"🎯 找到目标，移动到: ({x}, {y})，置信度: {confidence:.3f}")
            pyautogui.moveTo(x, y, duration=1)
            return True
        else:
            print("❌ 未找到目标")
            return False
    else:
        print("❌ 截图失败")
        return False

def test_real_world_scenario():
    """
    测试真实场景：保存一个目标，然后查找它
    """
    print("\n" + "="*50)
    print("🧪 真实场景测试")
    print("="*50)
    
    # 第一步：让用户选择目标区域
    print("\n步骤1: 选择目标区域")
    print("将鼠标移动到你想测试的目标上（如图标、按钮等）")
    print("5秒后自动截取该区域...")
    time.sleep(5)
    
    current_x, current_y = pyautogui.position()
    print(f"鼠标位置: ({current_x}, {current_y})")
    
    # 截取目标区域
    box_size = 100
    x1 = max(0, current_x - box_size//2)
    y1 = max(0, current_y - box_size//2)
    x2 = current_x + box_size//2
    y2 = current_y + box_size//2
    
    target_area = safe_screenshot((x1, y1, x2, y2))
    if target_area:
        target_area.save("real_world_template.png")
        print(f"✅ 模板已保存: real_world_template.png")
        
        # 第二步：查找目标
        print("\n步骤2: 查找目标")
        print("现在移动鼠标到屏幕其他位置，然后按回车键开始查找...")
        input("按回车键继续...")
        
        position = find_element_on_screen("real_world_template.png", confidence=0.7)
        
        if position:
            x, y, confidence = position
            print(f"🎯 成功找到目标！坐标: ({x}, {y})，置信度: {confidence:.3f}")
            
            # 移动到目标位置
            pyautogui.moveTo(x, y, duration=1)
            print("✅ 已移动到目标位置")
            
            # 进行点击操作（可选）
            response = input("是否要在该位置进行点击？(y/n): ")
            if response.lower() == 'y':
                pyautogui.click()
                print("✅ 已执行点击操作")
            return True
        else:
            print("❌ 未找到目标")
            return False
    else:
        print("❌ 截图失败，无法创建模板")
        return False

def run_opencv_demo():
    """
    OpenCV视觉定位演示 - 稳定版
    """
    print("=== OpenCV 视觉定位演示开始 ===")
    
    while True:
        print("\n请选择演示模式:")
        print("1. 基础演示（自动截取测试）")
        print("2. 真实场景测试（推荐）")
        print("3. 简化演示（最高成功率）")
        print("4. 退出")
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == '1':
            print("\n=== 基础演示开始 ===")
            print("请将鼠标悬停在你想识别的目标上，5秒后截取该区域...")
            time.sleep(5)
            
            current_x, current_y = pyautogui.position()
            print(f"鼠标当前位置: ({current_x}, {current_y})")
            
            box_size = 100
            x1 = max(0, current_x - box_size//2)
            y1 = max(0, current_y - box_size//2)
            x2 = current_x + box_size//2
            y2 = current_y + box_size//2
            
            target_area = safe_screenshot((x1, y1, x2, y2))
            if target_area:
                target_area.save("example_target.png")
                print(f"已截取区域: ({x1}, {y1}) 到 ({x2}, {y2})")
                
                position = find_element_on_screen("example_target.png", confidence=0.7)
                if position:
                    x, y, confidence = position
                    print(f"🎯 移动到目标位置: ({x}, {y})，置信度: {confidence:.3f}")
                    pyautogui.moveTo(x, y, duration=1)
                    print("✅ 视觉定位演示成功！")
                else:
                    print("未找到目标")
            else:
                print("❌ 截图失败")
                
        elif choice == '2':
            test_real_world_scenario()
            
        elif choice == '3':
            simple_capture_demo()
            
        elif choice == '4':
            print("👋 演示结束，再见！")
            break
            
        else:
            print("❌ 无效选择，请重新输入")

# === 这里是程序的入口 ===
if __name__ == "__main__":
    try:
        run_opencv_demo()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")
    finally:
        cv2.destroyAllWindows()