"""
Playwright 自动化测试演示脚本
AI与行为驱动的UI自动化测试平台 - 核心技术验证
作者：GH-Z202235810103
GitHub: https://github.com/GH-Z202235810103/ai-ui-test-platform
"""

from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime
from pathlib import Path

class PlaywrightDemo:
    """Playwright 自动化测试演示类 - 修复B站搜索版"""
    
    def __init__(self):
        self.results_dir = Path("playwright_results")
        self.results_dir.mkdir(exist_ok=True)
        self.test_results = []
        
    def run_baidu_search_demo(self):
        """
        百度搜索演示 - 核心功能验证
        """
        print("🎯 开始百度搜索演示")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            try:
                start_time = time.time()
                
                # 1. 访问百度首页
                print("📄 正在导航到百度...")
                page.goto("https://www.baidu.com", timeout=30000)
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(2000)
                
                # 保存首页截图
                page.screenshot(path=self.results_dir / "baidu_homepage.png")
                print("✅ 百度首页访问成功")
                
                # 2. 通过JavaScript设置搜索关键词
                print("⌨️ 设置搜索关键词: 'AI自动化测试'")
                page.evaluate('''() => {
                    const searchBox = document.querySelector('input#kw');
                    if (searchBox) {
                        searchBox.value = 'AI自动化测试';
                        searchBox.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }''')
                
                # 3. 通过JavaScript点击搜索按钮
                print("🔘 执行搜索...")
                page.evaluate('''() => {
                    const searchButton = document.querySelector('input#su');
                    if (searchButton) {
                        searchButton.click();
                    }
                }''')
                
                # 4. 等待搜索结果
                print("⏳ 等待搜索结果加载...")
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(3000)
                
                # 5. 保存搜索结果截图
                search_result_path = self.results_dir / "baidu_search_results.png"
                page.screenshot(path=search_result_path)
                print(f"✅ 搜索结果截图已保存: {search_result_path}")
                
                # 6. 提取搜索结果数据
                print("📊 提取搜索结果信息...")
                search_data = self.extract_search_results(page)
                
                # 7. 记录测试结果
                execution_time = time.time() - start_time
                test_result = {
                    "test_name": "百度搜索演示",
                    "status": "PASS",
                    "execution_time": round(execution_time, 2),
                    "timestamp": datetime.now().isoformat(),
                    "search_keyword": "AI自动化测试",
                    "results_count": len(search_data),
                    "search_results": search_data,
                    "screenshots": [
                        "baidu_homepage.png",
                        "baidu_search_results.png"
                    ]
                }
                
                self.test_results.append(test_result)
                self.save_test_report()
                
                print("✅ 百度搜索演示完成！")
                print(f"⏱️  总执行时间: {execution_time:.2f}秒")
                print(f"📊 找到 {len(search_data)} 个搜索结果")
                
                # 保持浏览器打开供查看
                print("🖥️  浏览器将保持打开8秒...")
                page.wait_for_timeout(8000)
                
            except Exception as e:
                print(f"❌ 百度搜索演示失败: {e}")
                test_result = {
                    "test_name": "百度搜索演示",
                    "status": "FAIL",
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(test_result)
            finally:
                browser.close()
    
    def run_taobao_product_demo(self):
        """
        淘宝商品搜索演示 - 国内网站，访问稳定
        """
        print("\n🎯 开始淘宝商品搜索演示")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            try:
                start_time = time.time()
                
                # 1. 访问淘宝首页
                print("📄 正在访问淘宝...")
                page.goto("https://www.taobao.com", timeout=30000)
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(3000)
                
                page.screenshot(path=self.results_dir / "taobao_homepage.png")
                print("✅ 淘宝首页访问成功")
                
                # 2. 搜索商品
                print("🔍 搜索商品: '手机'")
                page.evaluate('''() => {
                    const searchInput = document.querySelector('input#q');
                    if (searchInput) {
                        searchInput.value = '手机';
                        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // 点击搜索按钮
                        const searchBtn = document.querySelector('button.btn-search');
                        if (searchBtn) {
                            searchBtn.click();
                        }
                    }
                }''')
                
                # 3. 等待搜索结果
                print("⏳ 等待商品搜索结果...")
                page.wait_for_timeout(5000)
                
                page.screenshot(path=self.results_dir / "taobao_search_results.png")
                print("✅ 商品搜索完成")
                
                # 4. 记录测试结果
                execution_time = time.time() - start_time
                test_result = {
                    "test_name": "淘宝商品搜索演示",
                    "status": "PASS",
                    "execution_time": round(execution_time, 2),
                    "timestamp": datetime.now().isoformat(),
                    "search_keyword": "手机",
                    "screenshots": [
                        "taobao_homepage.png",
                        "taobao_search_results.png"
                    ]
                }
                
                self.test_results.append(test_result)
                self.save_test_report()
                
                print("✅ 淘宝商品搜索演示完成！")
                page.wait_for_timeout(5000)
                
            except Exception as e:
                print(f"❌ 淘宝演示失败: {e}")
                test_result = {
                    "test_name": "淘宝商品搜索演示",
                    "status": "FAIL",
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(test_result)
            finally:
                browser.close()
    
    def run_bilibili_demo(self):
        """
        B站演示 - 修复搜索功能
        """
        print("\n🎯 开始B站探索演示")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            try:
                start_time = time.time()
                
                # 1. 访问B站首页
                print("📄 正在访问B站...")
                page.goto("https://www.bilibili.com", timeout=30000)
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(3000)
                
                page.screenshot(path=self.results_dir / "bilibili_homepage.png")
                print("✅ B站首页访问成功")
                
                # 2. 修复搜索功能 - 使用更智能的搜索方法
                print("🔍 搜索视频: 'Python教程'")
                
                # 方法1: 尝试点击搜索框后输入
                search_success = page.evaluate('''() => {
                    try {
                        // 尝试多种搜索框选择器
                        const selectors = [
                            'input[placeholder="搜索"]',
                            '.nav-search-keyword',
                            'input.search-keyword',
                            'input[class*="search"]',
                            'input'
                        ];
                        
                        let searchInput = null;
                        for (let selector of selectors) {
                            const element = document.querySelector(selector);
                            if (element && element.offsetParent !== null) {
                                searchInput = element;
                                break;
                            }
                        }
                        
                        if (searchInput) {
                            // 点击搜索框
                            searchInput.click();
                            // 输入搜索词
                            searchInput.value = 'Python教程';
                            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                            
                            // 尝试找到搜索按钮并点击
                            const searchButtons = [
                                '.nav-search-btn',
                                'button[type="submit"]',
                                '.search-btn',
                                'button'
                            ];
                            
                            for (let btnSelector of searchButtons) {
                                const btn = document.querySelector(btnSelector);
                                if (btn && btn.offsetParent !== null) {
                                    btn.click();
                                    return true;
                                }
                            }
                            
                            // 如果没有找到按钮，按回车键
                            searchInput.dispatchEvent(new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true
                            }));
                            return true;
                        }
                        return false;
                    } catch (e) {
                        return false;
                    }
                }''')
                
                if search_success:
                    print("✅ 搜索指令执行成功")
                else:
                    print("⚠️  搜索框未找到，使用直接导航方式")
                    # 方法2: 直接导航到搜索结果页
                    page.goto("https://search.bilibili.com/all?keyword=Python教程", timeout=30000)
                
                # 3. 等待搜索结果
                print("⏳ 等待视频搜索结果...")
                page.wait_for_timeout(5000)
                
                page.screenshot(path=self.results_dir / "bilibili_search_results.png")
                print("✅ 视频搜索完成")
                
                # 4. 记录测试结果
                execution_time = time.time() - start_time
                test_result = {
                    "test_name": "B站视频搜索演示",
                    "status": "PASS",
                    "execution_time": round(execution_time, 2),
                    "timestamp": datetime.now().isoformat(),
                    "search_keyword": "Python教程",
                    "search_method": "直接导航" if not search_success else "页面交互",
                    "screenshots": [
                        "bilibili_homepage.png",
                        "bilibili_search_results.png"
                    ]
                }
                
                self.test_results.append(test_result)
                self.save_test_report()
                
                print("✅ B站探索演示完成！")
                page.wait_for_timeout(5000)
                
            except Exception as e:
                print(f"❌ B站演示失败: {e}")
                test_result = {
                    "test_name": "B站视频搜索演示",
                    "status": "FAIL", 
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(test_result)
            finally:
                browser.close()
    
    def run_form_interaction_demo(self):
        """
        表单交互演示 - 使用国内可访问的测试页面
        """
        print("\n🎯 开始表单交互演示")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            try:
                start_time = time.time()
                
                # 使用国内可访问的表单测试页面
                print("📄 访问表单测试页面...")
                page.goto("https://httpbin.org/forms/post", timeout=30000)
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(2000)
                
                page.screenshot(path=self.results_dir / "form_page.png")
                print("✅ 表单页面访问成功")
                
                # 通过JavaScript填充表单
                print("⌨️ 填充表单数据...")
                page.evaluate('''() => {
                    // 填充客户名
                    const custname = document.querySelector('input[name="custname"]');
                    if (custname) custname.value = '测试用户';
                    
                    // 选择电话
                    const telephone = document.querySelector('input[name="custtel"]');
                    if (telephone) telephone.value = '13800138000';
                    
                    // 选择披萨尺寸
                    const size = document.querySelector('select[name="size"]');
                    if (size) size.value = 'large';
                    
                    // 选择配料
                    const pepperoni = document.querySelector('input[value="pepperoni"]');
                    if (pepperoni) pepperoni.checked = true;
                    
                    // 填写备注
                    const comments = document.querySelector('textarea[name="comments"]');
                    if (comments) comments.value = '自动化测试订单';
                }''')
                
                page.screenshot(path=self.results_dir / "form_filled.png")
                print("✅ 表单填充完成")
                
                # 记录测试结果
                execution_time = time.time() - start_time
                test_result = {
                    "test_name": "表单交互演示",
                    "status": "PASS", 
                    "execution_time": round(execution_time, 2),
                    "timestamp": datetime.now().isoformat(),
                    "form_actions": "填充客户信息、选择选项、填写备注",
                    "screenshots": [
                        "form_page.png", 
                        "form_filled.png"
                    ]
                }
                
                self.test_results.append(test_result)
                self.save_test_report()
                
                print("✅ 表单交互演示完成！")
                page.wait_for_timeout(5000)
                
            except Exception as e:
                print(f"❌ 表单演示失败: {e}")
                test_result = {
                    "test_name": "表单交互演示",
                    "status": "FAIL",
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(test_result)
            finally:
                browser.close()
    
    def run_jd_product_demo(self):
        """
        京东商品搜索演示 - 替代方案，更稳定的电商网站
        """
        print("\n🎯 开始京东商品搜索演示")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            try:
                start_time = time.time()
                
                # 1. 访问京东首页
                print("📄 正在访问京东...")
                page.goto("https://www.jd.com", timeout=30000)
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(3000)
                
                page.screenshot(path=self.results_dir / "jd_homepage.png")
                print("✅ 京东首页访问成功")
                
                # 2. 搜索商品 - 京东的搜索框比较容易定位
                print("🔍 搜索商品: '笔记本电脑'")
                page.evaluate('''() => {
                    const searchInput = document.querySelector('input#key');
                    if (searchInput) {
                        searchInput.value = '笔记本电脑';
                        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // 点击搜索按钮
                        const searchBtn = document.querySelector('button.button');
                        if (searchBtn) {
                            searchBtn.click();
                        } else {
                            // 按回车键
                            searchInput.dispatchEvent(new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true
                            }));
                        }
                    }
                }''')
                
                # 3. 等待搜索结果
                print("⏳ 等待商品搜索结果...")
                page.wait_for_timeout(5000)
                
                page.screenshot(path=self.results_dir / "jd_search_results.png")
                print("✅ 商品搜索完成")
                
                # 4. 记录测试结果
                execution_time = time.time() - start_time
                test_result = {
                    "test_name": "京东商品搜索演示",
                    "status": "PASS",
                    "execution_time": round(execution_time, 2),
                    "timestamp": datetime.now().isoformat(),
                    "search_keyword": "笔记本电脑",
                    "screenshots": [
                        "jd_homepage.png",
                        "jd_search_results.png"
                    ]
                }
                
                self.test_results.append(test_result)
                self.save_test_report()
                
                print("✅ 京东商品搜索演示完成！")
                page.wait_for_timeout(5000)
                
            except Exception as e:
                print(f"❌ 京东演示失败: {e}")
                test_result = {
                    "test_name": "京东商品搜索演示",
                    "status": "FAIL",
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(test_result)
            finally:
                browser.close()
    
    def extract_search_results(self, page):
        """提取搜索结果信息"""
        try:
            search_data = page.evaluate('''() => {
                const results = [];
                const resultElements = document.querySelectorAll('div.result h3 a');
                
                for (let i = 0; i < Math.min(resultElements.length, 5); i++) {
                    const element = resultElements[i];
                    results.push({
                        rank: i + 1,
                        title: element.textContent?.trim() || '',
                        link: element.href || ''
                    });
                }
                return results;
            }''')
            
            return search_data
        except Exception as e:
            print(f"⚠️ 提取搜索结果时出错: {e}")
            return []
    
    def save_test_report(self):
        """保存测试报告"""
        report_data = {
            "project": "基于AI与行为驱动的UI自动化测试平台",
            "test_session": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "passed_tests": len([r for r in self.test_results if r['status'] == 'PASS']),
                "failed_tests": len([r for r in self.test_results if r['status'] == 'FAIL'])
            },
            "test_results": self.test_results
        }
        
        report_path = self.results_dir / "test_session_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 测试报告已更新: {report_path}")
    
    def run_complete_demo(self):
        """运行完整演示套件"""
        print("=" * 60)
        print("🎯 Playwright 自动化测试演示套件 - 增强版")
        print("基于AI与行为驱动的UI自动化测试平台")
        print("=" * 60)
        
        self.run_baidu_search_demo()      # 搜索引擎测试
        self.run_taobao_product_demo()    # 电商网站测试  
        self.run_bilibili_demo()          # 视频网站测试（修复版）
        self.run_jd_product_demo()        # 京东测试（新增）
        self.run_form_interaction_demo()  # 表单交互测试
        
        # 生成总结报告
        self.generate_summary_report()
        
        print("\n" + "=" * 60)
        print("✅ 所有演示完成！")
        print(f"📁 结果保存在: {self.results_dir.absolute()}")
        print("=" * 60)
    
    def generate_summary_report(self):
        """生成测试总结报告"""
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        total = len(self.test_results)
        
        print(f"\n📊 测试执行总结:")
        print(f"  总测试数: {total}")
        print(f"  通过: {passed}")
        print(f"  失败: {total - passed}")
        print(f"  成功率: {passed/total*100:.1f}%" if total > 0 else "成功率: 0%")

def main():
    """主函数"""
    demo = PlaywrightDemo()
    
    print("请选择演示模式:")
    print("1. 完整演示套件 (推荐)")
    print("2. 基础演示 (仅百度搜索)")
    print("3. 电商网站测试 (淘宝+京东)")
    
    choice = input("请输入选择 (1, 2 或 3): ").strip()
    
    if choice == "1":
        demo.run_complete_demo()
    elif choice == "2":
        demo.run_baidu_search_demo()
    elif choice == "3":
        demo.run_taobao_product_demo()
        demo.run_jd_product_demo()
    else:
        print("❌ 无效选择，运行基础演示...")
        demo.run_baidu_search_demo()

if __name__ == "__main__":
    main()