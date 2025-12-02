"""
main.py - AI UI自动化测试平台主入口
作者：GH-Z202235810103
GitHub: https://github.com/GH-Z202235810103/ai-ui-test-platform
"""

import sys
import os
from pathlib import Path

# 添加ai_services到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_services_path = os.path.join(current_dir, 'ai_services')
if ai_services_path not in sys.path:
    sys.path.append(ai_services_path)

def main():
    print("=" * 60)
    print("🤖 AI UI自动化测试平台")
    print("基于AI与行为驱动的UI自动化测试平台")
    print("=" * 60)
    
    while True:
        print("\n=== 主菜单 ===")
        print("1. 🧠 AI智能生成测试用例 (LLM引擎)")
        print("2. 👁️  视觉辅助录制元素 (OpenCV引擎)")
        print("3. 🎭 执行自动化测试 (Playwright引擎)")
        print("4. 🔗 AI-行为智能绑定演示 (创新功能)")
        print("5. 🚀 完整流程演示 (推荐)")
        print("6. 📊 项目结构与说明")
        print("7. ❌ 退出平台")
        
        choice = input("\n请输入选项 (1-7): ").strip()
        
        if choice == "1":
            run_llm_engine()
        elif choice == "2":
            run_opencv_engine()
        elif choice == "3":
            run_playwright_engine()
        elif choice == "4":
            run_intelligent_binder_demo()  # 新增功能
        elif choice == "5":
            run_full_demo()
        elif choice == "6":
            show_project_info()
        elif choice == "7":
            print("\n感谢使用AI UI自动化测试平台！")
            break
        else:
            print("❌ 无效选项")

def run_llm_engine():
    """运行LLM测试生成引擎"""
    print("\n" + "=" * 40)
    print("🧠 AI测试用例生成引擎")
    print("=" * 40)
    
    try:
        from demo_llm import DeepSeekTestGenerator
        generator = DeepSeekTestGenerator()
        generator.demo_llm_generation()
    except ImportError as e:
        print(f"❌ 导入失败，请检查: {e}")
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def run_opencv_engine():
    """运行OpenCV视觉引擎"""
    print("\n" + "=" * 40)
    print("👁️  视觉辅助录制引擎")
    print("=" * 40)
    
    try:
        from demo_opencv import run_opencv_demo
        run_opencv_demo()
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def run_playwright_engine():
    """运行Playwright自动化引擎"""
    print("\n" + "=" * 40)
    print("🎭 自动化测试执行引擎")
    print("=" * 40)
    
    try:
        from demo_playwright import PlaywrightDemo
        demo = PlaywrightDemo()
        
        print("请选择演示模式:")
        print("1. 百度搜索演示")
        print("2. 完整演示套件 (推荐)")
        print("3. 电商网站测试 (淘宝+京东)")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            demo.run_baidu_search_demo()
        elif choice == "2":
            demo.run_complete_demo()
        elif choice == "3":
            demo.run_taobao_product_demo()
            demo.run_jd_product_demo()
        else:
            print("❌ 无效选择，运行百度搜索演示...")
            demo.run_baidu_search_demo()
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def run_intelligent_binder_demo():
    """运行AI-行为智能绑定演示"""
    print("\n" + "=" * 40)
    print("🔗 AI-行为智能绑定演示")
    print("(论文创新点：自然语言到可执行代码的映射)")
    print("=" * 40)
    
    try:
        from intelligent_binder import IntelligentTestBinder
        
        binder = IntelligentTestBinder()
        
        # 模拟LLM生成的测试用例
        test_case = {
            "test_case_name": "百度搜索完整测试",
            "test_steps": [
                "打开百度首页",
                "在搜索框输入'人工智能'",
                "点击百度一下按钮",
                "验证搜索结果包含相关条目",
                "点击第一条搜索结果"
            ]
        }
        
        print("📝 原始测试步骤:")
        for i, step in enumerate(test_case["test_steps"], 1):
            print(f"  {i}. {step}")
        
        print("\n🔧 智能绑定结果:")
        result = binder.bind_test_case(test_case)
        
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n💡 学术价值:")
        print("  • 展示了自然语言到可执行代码的映射")
        print("  • 为完全自动化测试生成提供了框架")
        print("  • 标记了需要视觉录制补充的部分")
        
    except ImportError:
        print("❌ 找不到 intelligent_binder.py，请确保文件在 ai_services/ 目录")
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def run_full_demo():
    """运行完整演示流程"""
    print("\n" + "=" * 40)
    print("🚀 完整集成演示流程")
    print("=" * 40)
    
    print("🎬 演示剧本：百度搜索自动化测试")
    print("1. AI生成测试用例")
    print("2. 智能绑定为可执行步骤")
    print("3. (可选)视觉录制补充元素定位")
    print("4. 执行自动化测试")
    print("-" * 40)
    
    # 这里可以分步调用各个模块
    choice = input("是否开始完整演示？(y/n): ").strip().lower()
    
    if choice == 'y':
        # 1. 先演示AI绑定
        run_intelligent_binder_demo()
        
        # 2. 询问是否继续其他演示
        cont = input("\n是否继续其他模块演示？(y/n): ").strip().lower()
        if cont == 'y':
            print("\n请从主菜单中选择其他模块继续体验...")
    else:
        print("已返回主菜单")

def show_project_info():
    """显示项目信息"""
    print("\n" + "=" * 40)
    print("📋 项目信息")
    print("=" * 40)
    print("项目：基于AI与行为驱动的UI自动化测试平台")
    print("作者：GH-Z202235810103")
    
    print("\n🏗️  技术架构:")
    print("  1. 🧠 LLM引擎 - DeepSeek智能生成测试用例")
    print("  2. 👁️  OpenCV引擎 - 视觉定位与元素录制")
    print("  3. 🎭 Playwright引擎 - 跨平台自动化执行")
    print("  4. 🔗 智能绑定器 - AI意图到操作的映射")
    
    print("\n📁 项目结构:")
    try:
        root = Path(".")
        for item in sorted(root.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                print(f"  📁 {item.name}/")
                # 显示子目录内容
                subdir = Path(item)
                for subitem in sorted(subdir.iterdir()):
                    if subitem.is_file() and subitem.suffix == '.py':
                        print(f"     📄 {subitem.name}")
        print(f"  📄 main.py (本文件)")
    except:
        print("  (无法读取目录结构)")

if __name__ == "__main__":
    main()