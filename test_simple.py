"""
简化测试脚本 - AI UI自动化测试平台
"""
from playwright.sync_api import sync_playwright
import os
import time

def main():
    print("\n" + "="*60)
    print("开始测试 AI UI自动化测试平台")
    print("="*60)
    
    os.makedirs("d:/毕设git/ai-ui-test-platform/test_screenshots", exist_ok=True)
    
    with sync_playwright() as p:
        print("\n[1] 启动浏览器...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("\n[2] 访问测试用例列表页面...")
            page.goto('http://localhost:3002/testcases', timeout=30000)
            page.wait_for_load_state('networkidle', timeout=30000)
            
            print("\n[3] 截图保存...")
            screenshot_path = "d:/毕设git/ai-ui-test-platform/test_screenshots/testcase_list.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"   - 截图已保存: {screenshot_path}")
            
            print("\n[4] 检查页面元素...")
            
            table_count = page.locator('table').count()
            print(f"   - 表格数量: {table_count}")
            
            if table_count > 0:
                print("\n[5] 检查执行按钮...")
                execute_buttons = page.locator('button:has-text("执行")').all()
                print(f"   - 执行按钮数量: {len(execute_buttons)}")
                
                if len(execute_buttons) > 0:
                    print("\n[6] 点击第一个执行按钮...")
                    execute_buttons[0].click()
                    time.sleep(2)
                    
                    print("\n[7] 截图保存配置对话框...")
                    screenshot_path = "d:/毕设git/ai-ui-test-platform/test_screenshots/config_dialog.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    print(f"   - 截图已保存: {screenshot_path}")
                    
                    print("\n[8] 检查配置对话框...")
                    dialog_count = page.locator('.el-dialog:visible').count()
                    print(f"   - 对话框数量: {dialog_count}")
                    
                    if dialog_count > 0:
                        print("\n[9] 检查配置项...")
                        switch_count = page.locator('.el-switch').count()
                        print(f"   - 开关数量: {switch_count}")
                        
                        input_count = page.locator('input[type="number"]').count()
                        print(f"   - 数字输入框数量: {input_count}")
                        
                        print("\n[10] 点击开始执行按钮...")
                        confirm_btn = page.locator('button:has-text("开始执行")')
                        if confirm_btn.count() > 0:
                            confirm_btn.click()
                            time.sleep(3)
                            
                            print("\n[11] 截图保存执行进度...")
                            screenshot_path = "d:/毕设git/ai-ui-test-platform/test_screenshots/execution_progress.png"
                            page.screenshot(path=screenshot_path, full_page=True)
                            print(f"   - 截图已保存: {screenshot_path}")
                            
                            print("\n[OK] 单个测试用例执行功能测试完成")
                        else:
                            print("\n[FAIL] 未找到开始执行按钮")
                    else:
                        print("\n[FAIL] 配置对话框未显示")
                else:
                    print("\n[WARN] 没有找到执行按钮")
            else:
                print("\n[FAIL] 表格未找到")
                
        except Exception as e:
            print(f"\n[ERROR] 测试出错: {str(e)}")
            import traceback
            traceback.print_exc()
            
            screenshot_path = "d:/毕设git/ai-ui-test-platform/test_screenshots/error.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"   - 错误截图已保存: {screenshot_path}")
        
        finally:
            print("\n[12] 关闭浏览器...")
            browser.close()
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n测试截图保存在: d:/毕设git/ai-ui-test-platform/test_screenshots/")

if __name__ == "__main__":
    main()
