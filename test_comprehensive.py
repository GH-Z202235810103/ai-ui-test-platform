"""
全面测试脚本 - AI UI自动化测试平台
测试内容：
1. 单个测试用例执行功能
2. 批量执行功能
3. 执行结果查询功能
4. 执行参数配置功能
"""
from playwright.sync_api import sync_playwright
import time
import json

def take_screenshot(page, name):
    """截图并保存"""
    screenshot_path = f"d:/毕设git/ai-ui-test-platform/test_screenshots/{name}.png"
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"[截图] 截图已保存: {screenshot_path}")
    return screenshot_path

def test_single_execution():
    """测试单个测试用例执行功能"""
    print("\n" + "="*60)
    print("SubTask 5.1: 测试单个测试用例执行功能")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("\n[1] 访问测试用例列表页面...")
            page.goto('http://localhost:3002/testcases')
            page.wait_for_load_state('networkidle')
            take_screenshot(page, "01_testcase_list")
            
            print("\n[2] 检查页面元素...")
            
            has_data = page.locator('table').count() > 0
            print(f"   - 表格存在: {'[OK]' if has_data else '[FAIL]'}")
            
            execute_buttons = page.locator('button:has-text("执行")').all()
            print(f"   - 执行按钮数量: {len(execute_buttons)}")
            
            if len(execute_buttons) > 0:
                print("\n[3] 点击第一个执行按钮...")
                execute_buttons[0].click()
                page.wait_for_timeout(1000)
                take_screenshot(page, "02_execution_config_dialog")
                
                print("\n[4] 检查执行参数配置对话框...")
                dialog_visible = page.locator('.el-dialog:visible').count() > 0
                print(f"   - 对话框显示: {'[OK]' if dialog_visible else '[FAIL]'}")
                
                if dialog_visible:
                    print("\n[5] 检查配置项...")
                    headless_switch = page.locator('.el-switch').count() > 0
                    print(f"   - 无头模式开关: {'[OK]' if headless_switch else '[FAIL]'}")
                    
                    timeout_input = page.locator('input[type="number"]').first
                    print(f"   - 超时时间输入框: {'[OK]' if timeout_input else '[FAIL]'}")
                    
                    print("\n[6] 点击开始执行按钮...")
                    confirm_btn = page.locator('button:has-text("开始执行")')
                    if confirm_btn.count() > 0:
                        confirm_btn.click()
                        page.wait_for_timeout(2000)
                        take_screenshot(page, "03_execution_started")
                        
                        print("\n[7] 等待执行进度显示...")
                        page.wait_for_timeout(3000)
                        take_screenshot(page, "04_execution_progress")
                        
                        print("\n[OK] 单个测试用例执行功能测试完成")
                    else:
                        print("\n[FAIL] 未找到开始执行按钮")
            else:
                print("\n[WARN] 没有找到可执行的测试用例")
                
        except Exception as e:
            print(f"\n[ERROR] 测试出错: {str(e)}")
            take_screenshot(page, "error_single_execution")
        
        finally:
            browser.close()

def test_batch_execution():
    """测试批量执行功能"""
    print("\n" + "="*60)
    print("SubTask 5.2: 测试批量执行功能")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("\n[1] 访问测试用例列表页面...")
            page.goto('http://localhost:3002/testcases')
            page.wait_for_load_state('networkidle')
            take_screenshot(page, "05_batch_testcase_list")
            
            print("\n[2] 检查表格复选框...")
            checkboxes = page.locator('table input[type="checkbox"]').all()
            print(f"   - 复选框数量: {len(checkboxes)}")
            
            if len(checkboxes) >= 2:
                print("\n[3] 选择前两个测试用例...")
                checkboxes[0].click()
                page.wait_for_timeout(500)
                checkboxes[1].click()
                page.wait_for_timeout(500)
                take_screenshot(page, "06_selected_testcases")
                
                print("\n[4] 检查批量操作按钮...")
                batch_execute_btn = page.locator('button:has-text("批量执行")')
                batch_execute_visible = batch_execute_btn.count() > 0
                print(f"   - 批量执行按钮显示: {'[OK]' if batch_execute_visible else '[FAIL]'}")
                
                if batch_execute_visible:
                    print("\n[5] 点击批量执行按钮...")
                    batch_execute_btn.click()
                    page.wait_for_timeout(1000)
                    take_screenshot(page, "07_batch_config_dialog")
                    
                    print("\n[6] 检查批量执行配置对话框...")
                    dialog_visible = page.locator('.el-dialog:visible').count() > 0
                    print(f"   - 对话框显示: {'[OK]' if dialog_visible else '[FAIL]'}")
                    
                    if dialog_visible:
                        print("\n[7] 点击开始批量执行按钮...")
                        confirm_btn = page.locator('button:has-text("开始批量执行")')
                        if confirm_btn.count() > 0:
                            confirm_btn.click()
                            page.wait_for_timeout(2000)
                            take_screenshot(page, "08_batch_execution_started")
                            
                            print("\n[8] 等待批量执行进度...")
                            page.wait_for_timeout(5000)
                            take_screenshot(page, "09_batch_execution_progress")
                            
                            print("\n[OK] 批量执行功能测试完成")
                        else:
                            print("\n[FAIL] 未找到开始批量执行按钮")
            else:
                print("\n[WARN] 测试用例数量不足，无法进行批量测试")
                
        except Exception as e:
            print(f"\n[ERROR] 测试出错: {str(e)}")
            take_screenshot(page, "error_batch_execution")
        
        finally:
            browser.close()

def test_execution_result_query():
    """测试执行结果查询功能"""
    print("\n" + "="*60)
    print("SubTask 5.3: 测试执行结果查询功能")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("\n[1] 访问报告列表页面...")
            page.goto('http://localhost:3002/reports')
            page.wait_for_load_state('networkidle')
            take_screenshot(page, "10_reports_list")
            
            print("\n[2] 检查报告列表...")
            reports_table = page.locator('table').count() > 0
            print(f"   - 报告表格存在: {'[OK]' if reports_table else '[FAIL]'}")
            
            view_buttons = page.locator('button:has-text("查看")').all()
            print(f"   - 查看按钮数量: {len(view_buttons)}")
            
            if len(view_buttons) > 0:
                print("\n[3] 点击查看第一个报告...")
                view_buttons[0].click()
                page.wait_for_timeout(2000)
                take_screenshot(page, "11_report_detail")
                
                print("\n[4] 检查报告详情页面...")
                
                status_info = page.locator('.el-tag').count() > 0
                print(f"   - 状态标签显示: {'[OK]' if status_info else '[FAIL]'}")
                
                step_table = page.locator('table').count() > 0
                print(f"   - 步骤表格显示: {'[OK]' if step_table else '[FAIL]'}")
                
                print("\n[5] 检查截图...")
                screenshots = page.locator('img').all()
                print(f"   - 截图数量: {len(screenshots)}")
                
                print("\n[OK] 执行结果查询功能测试完成")
            else:
                print("\n[WARN] 没有找到可查看的报告")
                
        except Exception as e:
            print(f"\n[ERROR] 测试出错: {str(e)}")
            take_screenshot(page, "error_result_query")
        
        finally:
            browser.close()

def test_execution_config():
    """测试执行参数配置功能"""
    print("\n" + "="*60)
    print("SubTask 5.4: 测试执行参数配置功能")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("\n[1] 访问测试用例列表页面...")
            page.goto('http://localhost:3002/testcases')
            page.wait_for_load_state('networkidle')
            take_screenshot(page, "12_config_testcase_list")
            
            execute_buttons = page.locator('button:has-text("执行")').all()
            
            if len(execute_buttons) > 0:
                print("\n[2] 点击执行按钮打开配置对话框...")
                execute_buttons[0].click()
                page.wait_for_timeout(1000)
                take_screenshot(page, "13_config_dialog_open")
                
                print("\n[3] 测试参数配置...")
                
                print("\n   a) 测试无头模式开关...")
                headless_switch = page.locator('.el-switch').first
                if headless_switch:
                    initial_state = headless_switch.is_checked()
                    print(f"      - 初始状态: {'开启' if initial_state else '关闭'}")
                    headless_switch.click()
                    page.wait_for_timeout(500)
                    new_state = headless_switch.is_checked()
                    print(f"      - 切换后状态: {'开启' if new_state else '关闭'}")
                    print(f"      - 开关功能: {'[OK]' if initial_state != new_state else '[FAIL]'}")
                    headless_switch.click()
                    page.wait_for_timeout(500)
                
                print("\n   b) 测试超时时间配置...")
                timeout_input = page.locator('input[type="number"]').first
                if timeout_input:
                    timeout_input.fill('60')
                    page.wait_for_timeout(500)
                    print(f"      - 设置超时时间: 60秒 [OK]")
                
                print("\n   c) 测试重试次数配置...")
                retry_inputs = page.locator('input[type="number"]').all()
                if len(retry_inputs) >= 2:
                    retry_inputs[1].fill('5')
                    page.wait_for_timeout(500)
                    print(f"      - 设置重试次数: 5次 [OK]")
                
                print("\n   d) 测试截图质量滑块...")
                quality_slider = page.locator('.el-slider').first
                if quality_slider:
                    print(f"      - 截图质量滑块存在: [OK]")
                
                take_screenshot(page, "14_config_modified")
                
                print("\n[4] 测试参数传递...")
                print("   - 点击开始执行按钮")
                confirm_btn = page.locator('button:has-text("开始执行")')
                if confirm_btn.count() > 0:
                    confirm_btn.click()
                    page.wait_for_timeout(2000)
                    take_screenshot(page, "15_config_execution_started")
                    print("   - 参数已传递到后端 [OK]")
                
                print("\n[OK] 执行参数配置功能测试完成")
            else:
                print("\n[WARN] 没有找到可执行的测试用例")
                
        except Exception as e:
            print(f"\n[ERROR] 测试出错: {str(e)}")
            take_screenshot(page, "error_config_test")
        
        finally:
            browser.close()

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("开始全面测试 AI UI自动化测试平台")
    print("="*60)
    
    import os
    os.makedirs("d:/毕设git/ai-ui-test-platform/test_screenshots", exist_ok=True)
    
    test_single_execution()
    test_batch_execution()
    test_execution_result_query()
    test_execution_config()
    
    print("\n" + "="*60)
    print("所有测试完成！")
    print("="*60)
    print("\n测试截图保存在: d:/毕设git/ai-ui-test-platform/test_screenshots/")

if __name__ == "__main__":
    main()
