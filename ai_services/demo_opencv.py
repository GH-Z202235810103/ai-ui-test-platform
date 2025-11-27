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
    screenshot = ImageGrab.grab()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)  # 转换颜色空间
    
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
        return (center_x, center_y)
    else:
        print(f"❌ 未找到目标，最高置信度 {max_val:.3f} 低于阈值 {confidence}")
        return None

def real_time_mouse_capture():
    """
    实时截取鼠标位置区域的演示
    """
    print("=== 实时鼠标位置截取演示 ===")
    print("说明：")
    print("1. 将鼠标移动到你想截取的目标上")
    print("2. 程序会实时显示鼠标位置的区域")
    print("3. 按 's' 键保存当前区域作为模板")
    print("4. 按 'q' 键退出实时模式")
    print("5. 按 'f' 键开始查找保存的模板")
    
    capture_size = 150  # 截取区域大小
    template_saved = False
    template_path = "real_time_template.png"
    
    # 创建OpenCV窗口
    cv2.namedWindow("Real-time Mouse Area", cv2.WINDOW_NORMAL)
    
    print("\n开始实时监控...")
    
    while True:
        # 获取当前鼠标位置
        current_x, current_y = pyautogui.position()
        
        # 计算截取区域（确保不超出屏幕边界）
        screen_width, screen_height = pyautogui.size()
        x1 = max(0, current_x - capture_size//2)
        y1 = max(0, current_y - capture_size//2)
        x2 = min(screen_width, current_x + capture_size//2)
        y2 = min(screen_height, current_y + capture_size//2)
        
        # 截取鼠标位置区域
        mouse_area = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        mouse_area_cv = np.array(mouse_area)
        mouse_area_cv = cv2.cvtColor(mouse_area_cv, cv2.COLOR_RGB2BGR)
        
        # 在图像上添加信息
        cv2.putText(mouse_area_cv, f"Mouse: ({current_x}, {current_y})", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(mouse_area_cv, f"Area: {x1},{y1} to {x2},{y2}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(mouse_area_cv, "Press 's' to save, 'q' to quit, 'f' to find", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 显示图像
        cv2.imshow("Real-time Mouse Area", mouse_area_cv)
        
        # 检测按键
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):  # 退出
            break
        elif key == ord('s'):  # 保存模板
            cv2.imwrite(template_path, mouse_area_cv)
            template_saved = True
            print(f"✅ 模板已保存: {template_path}")
            print(f"📏 模板尺寸: {mouse_area_cv.shape[1]}x{mouse_area_cv.shape[0]}")
        elif key == ord('f'):  # 查找模板
            if template_saved:
                print("🔍 开始查找保存的模板...")
                position = find_element_on_screen(template_path, confidence=0.7)
                if position:
                    x, y = position
                    print(f"🎯 移动到找到的位置: ({x}, {y})")
                    pyautogui.moveTo(x, y, duration=1)
                else:
                    print("❌ 未找到模板目标")
            else:
                print("❌ 请先按 's' 保存模板")
    
    cv2.destroyAllWindows()
    return template_saved

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
    print("在实时窗口中按 's' 保存为目标模板")
    
    template_saved = real_time_mouse_capture()
    
    if not template_saved:
        print("❌ 未保存模板，跳过测试")
        return
    
    # 第二步：查找目标
    print("\n步骤2: 查找目标")
    print("现在移动鼠标到屏幕其他位置，然后按任意键开始查找...")
    input("按回车键继续...")
    
    position = find_element_on_screen("real_time_template.png", confidence=0.7)
    
    if position:
        x, y = position
        print(f"🎯 成功找到目标！坐标: ({x}, {y})")
        
        # 移动到目标位置
        pyautogui.moveTo(x, y, duration=1)
        print("✅ 已移动到目标位置")
        
        # 进行点击操作（可选）
        response = input("是否要在该位置进行点击？(y/n): ")
        if response.lower() == 'y':
            pyautogui.click()
            print("✅ 已执行点击操作")
    else:
        print("❌ 未找到目标，可能的原因：")
        print("   - 屏幕内容发生了变化")
        print("   - 目标被其他窗口遮挡")
        print("   - 匹配置信度阈值过高")

def run_opencv_demo():
    """
    OpenCV视觉定位演示 - 完整版
    """
    print("=== OpenCV 视觉定位演示开始 ===")
    
    while True:
        print("\n请选择演示模式:")
        print("1. 基础演示（截取固定区域）")
        print("2. 实时鼠标区域截取")
        print("3. 真实场景测试")
        print("4. 退出")
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == '1':
            print("\n=== 基础演示开始 ===")
            print("请将鼠标悬停在你想识别的目标上，5秒后截取该区域...")
            time.sleep(5)
            
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            print(f"鼠标当前位置: ({current_x}, {current_y})")
            
            # 以鼠标位置为中心截取一个区域
            box_size = 100
            x1 = max(0, current_x - box_size//2)
            y1 = max(0, current_y - box_size//2)
            x2 = current_x + box_size//2
            y2 = current_y + box_size//2
            
            # 截取目标区域
            target_area = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            target_area.save("example_target.png")
            print(f"已截取区域: ({x1}, {y1}) 到 ({x2}, {y2})")
            print("示例区域已保存为 'example_target.png'")
            
            # 查找目标
            position = find_element_on_screen("example_target.png", confidence=0.7)
            
            if position:
                x, y = position
                print(f"🎯 移动到目标位置: ({x}, {y})")
                pyautogui.moveTo(x, y, duration=1)
                print("✅ 视觉定位演示成功！")
            else:
                print("未找到目标，可能截图区域特征不够明显")
                
        elif choice == '2':
            real_time_mouse_capture()
            
        elif choice == '3':
            test_real_world_scenario()
            
        elif choice == '4':
            print("👋 演示结束，再见！")
            break
            
        else:
            print("❌ 无效选择，请重新输入")

# === 这里是程序的入口 ===
if __name__ == "__main__":
    run_opencv_demo()