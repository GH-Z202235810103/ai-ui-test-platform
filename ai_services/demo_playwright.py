"""
Playwright 自动化测试演示脚本
AI与行为驱动的UI自动化测试平台 - 核心技术验证
作者：GH-Z202235810103
GitHub: https://github.com/GH-Z202235810103/ai-ui-test-platform
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

class PlaywrightDemo:
    """Playwright演示用例 - 重构后增强健壮性和复用性"""
    def __init__(self):
        self.test_results = []  # 存储所有测试结果
        self.screenshot_dir = "./screenshots"  # 截图保存目录
        # 确保截图目录存在
        import os
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def _init_browser(self, p) -> tuple:
        """公共浏览器初始化方法 - 抽离重复逻辑"""
        try:
            browser = p.chromium.launch(headless=False)  # 调试时设为False，生产设为True
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            return browser, context, page
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {str(e)}")
            raise

    def _save_screenshot(self, page, case_name: str) -> str:
        """公共截图保存方法"""
        screenshot_path = f"{self.screenshot_dir}/{case_name}_{int(time.time())}.png"
        try:
            page.screenshot(path=screenshot_path, full_page=True)
            return screenshot_path
        except Exception as e:
            print(f"⚠️ 截图保存失败: {str(e)}")
            return ""

    def _record_result(self, case_name: str, status: str, error_msg: str = "", screenshot: str = ""):
        """公共测试结果记录方法"""
        self.test_results.append({
            "case_name": case_name,
            "status": status,  # success/failed
            "error_msg": error_msg,
            "screenshot": screenshot,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def run_baidu_search_demo(self, p):
        """百度搜索演示 - 修复异常处理和等待逻辑"""
        case_name = "百度搜索演示"
        browser = context = page = None
        try:
            # 初始化浏览器
            browser, context, page = self._init_browser(p)
            
            # 访问百度
            page.goto("https://www.baidu.com", timeout=10000)
            
            # 条件等待：搜索框出现（替代固定等待）
            search_box = page.wait_for_selector("#kw", timeout=10000)
            search_box.fill("Playwright教程")
            
            # 点击搜索按钮（条件等待按钮可点击）
            search_btn = page.wait_for_selector("#su", state="enabled", timeout=5000)
            search_btn.click()
            
            # 等待搜索结果加载
            page.wait_for_selector("#content_left", timeout=10000)
            
            # 保存截图
            screenshot = self._save_screenshot(page, case_name)
            
            # 记录成功结果
            self._record_result(case_name, "success", screenshot=screenshot)
            print(f"✅ {case_name} 执行成功")

        except Exception as e:
            error_msg = str(e)
            self._record_result(case_name, "failed", error_msg, self._save_screenshot(page, case_name) if page else "")
            print(f"❌ {case_name} 执行失败: {error_msg}")
        finally:
            # 安全关闭浏览器（逐层关闭，避免资源泄漏）
            if page:
                page.close()
            if context:
                context.close()
            if browser:
                browser.close()

    def run_taobao_demo(self, p):
        """淘宝演示 - 优化等待和选择器"""
        case_name = "淘宝演示"
        browser = context = page = None
        try:
            # 初始化浏览器（建议在_init_browser中添加超时和日志）
            browser, context, page = self._init_browser(p)
            page.goto("https://www.taobao.com", timeout=15000)
            page.wait_for_load_state("networkidle", timeout=15000)
            
            # 搜索框选择逻辑优化：添加日志，明确尝试的选择器
            search_selectors = ["#q", "input[placeholder='搜索淘宝']", "input[name='q']"]
            search_box = None
            for idx, selector in enumerate(search_selectors, 1):
                try:
                    search_box = page.wait_for_selector(selector, timeout=3000)
                    if search_box:
                        print(f"✅ 找到搜索框，使用选择器: {selector}")
                        break
                except Exception as e:
                    print(f"⚠️ 选择器 {selector} 未找到（第{idx}次尝试）: {str(e)}")
                    continue
            
            if not search_box:
                raise Exception("未找到淘宝搜索框，所有选择器尝试失败")
            
            # 搜索操作优化：添加输入后等待
            search_box.fill("笔记本电脑")
            page.wait_for_timeout(500)  # 短暂等待输入生效
            page.keyboard.press("Enter")
            
            # 修复选择器（原选择器缺少.连接类名）
            page.wait_for_selector(".item.J_MouserOnverReq", timeout=10000)
            
            # 截图和结果记录
            screenshot = self._save_screenshot(page, case_name)
            self._record_result(case_name, "success", screenshot=screenshot)
            print(f"✅ {case_name} 执行成功")

        except Exception as e:
            error_msg = str(e)
            # 避免page为None时调用_save_screenshot
            screenshot = self._save_screenshot(page, case_name) if page else "无截图（页面未初始化）"
            self._record_result(case_name, "failed", error_msg, screenshot)
            print(f"❌ {case_name} 执行失败: {error_msg}")
        finally:
            # 关闭资源的安全处理（先判断再关闭）
            if page:
                try:
                    page.close()
                except Exception as e:
                    print(f"⚠️ 关闭页面失败: {str(e)}")
            if context:
                try:
                    context.close()
                except Exception as e:
                    print(f"⚠️ 关闭上下文失败: {str(e)}")
            if browser:
                try:
                    browser.close()
                except Exception as e:
                    print(f"⚠️ 关闭浏览器失败: {str(e)}")

    def run_bilibili_demo(self, p):
        """B站演示 - 补全代码，优化选择器"""
        case_name = "B站视频搜索演示"
        browser = context = page = None
        try:
            browser, context, page = self._init_browser(p)
            page.goto("https://www.bilibili.com", timeout=10000)
            
            # 关闭弹窗（如有）
            try:
                close_btn = page.wait_for_selector(".bili-modal__close", timeout=3000)
                close_btn.click()
            except:
                pass
            
            # 条件等待搜索框
            search_box = page.wait_for_selector('input[placeholder="搜索"]', timeout=10000)
            search_box.fill("Playwright自动化测试")
            
            # 点击搜索按钮（兼容多个选择器）
            search_btns = ['.nav-search-btn', 'button[type="submit"]', '.search-button']
            for btn_selector in search_btns:
                try:
                    search_btn = page.wait_for_selector(btn_selector, state="enabled", timeout=3000)
                    search_btn.click()
                    break
                except:
                    continue
            
            # 等待搜索结果加载
            page.wait_for_selector(".video-list-item", timeout=10000)
            
            screenshot = self._save_screenshot(page, case_name)
            self._record_result(case_name, "success", screenshot=screenshot)
            print(f"✅ {case_name} 执行成功")

        except Exception as e:
            error_msg = str(e)
            self._record_result(case_name, "failed", error_msg, self._save_screenshot(page, case_name) if page else "")
            print(f"❌ {case_name} 执行失败: {error_msg}")
        finally:
            if page:
                page.close()
            if context:
                context.close()
            if browser:
                browser.close()

    def run_jd_demo(self, p):
        """京东商品搜索演示 - 补充缺失的实现"""
        case_name = "京东商品搜索演示"
        browser = context = page = None
        try:
            browser, context, page = self._init_browser(p)
            page.goto("https://www.jd.com", timeout=10000)
            
            search_box = page.wait_for_selector("#key", timeout=10000)
            search_box.fill("手机")
            page.wait_for_selector(".button", timeout=5000).click()
            
            # 等待商品列表加载
            page.wait_for_selector(".gl-item", timeout=10000)
            
            screenshot = self._save_screenshot(page, case_name)
            self._record_result(case_name, "success", screenshot=screenshot)
            print(f"✅ {case_name} 执行成功")

        except Exception as e:
            error_msg = str(e)
            self._record_result(case_name, "failed", error_msg, self._save_screenshot(page, case_name) if page else "")
            print(f"❌ {case_name} 执行失败: {error_msg}")
        finally:
            if page:
                page.close()
            if context:
                context.close()
            if browser:
                browser.close()

    def save_test_report(self, file_path: str = "test_session_report.json"):
        """保存测试报告到JSON文件"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=4)
            print(f"📄 测试报告已保存至: {file_path}")
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")

# 主执行逻辑
if __name__ == "__main__":
    demo = PlaywrightDemo()
    
    with sync_playwright() as p:
        # 执行所有演示用例
        demo.run_baidu_search_demo(p)
        demo.run_taobao_demo(p)
        demo.run_bilibili_demo(p)
        demo.run_jd_demo(p)
    
    # 保存测试报告
    demo.save_test_report()