from playwright.sync_api import sync_playwright

def run_playwright_demo():
    """
    一个简单的Playwright演示函数
    目标：打开浏览器，访问百度，执行搜索，并截图。
    """
    # 使用 sync_playwright 管理器启动Playwright
    with sync_playwright() as p:
        # 1. 启动Chromium浏览器
        print("正在启动浏览器...")
        browser = p.chromium.launch(headless=False)
        
        # 2. 创建一个新的浏览器页面
        page = browser.new_page()
        
        # 3. 导航到百度首页
        print("正在导航到百度...")
        page.goto("https://www.baidu.com")
        
        # 【关键修复1】：等待页面完全加载
        print("等待页面完全加载...")
        page.wait_for_load_state('networkidle')  # 等待网络空闲
        page.wait_for_timeout(2000)  # 额外等待2秒
        
        # 【关键修复2】：使用JavaScript直接设置搜索框的值（绕过可见性检查）
        print("通过JavaScript设置搜索关键词...")
        page.evaluate('''() => {
            const searchBox = document.querySelector('input#kw');
            if (searchBox) {
                searchBox.value = '什么是UI自动化测试';
                // 触发输入事件，让百度知道值改变了
                searchBox.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }''')
        
        # 【关键修复3】：使用JavaScript直接点击搜索按钮
        print("通过JavaScript执行搜索...")
        page.evaluate('''() => {
            const searchButton = document.querySelector('input#su');
            if (searchButton) {
                searchButton.click();
            }
        }''')
        
        # 4. 等待搜索结果页面加载
        print("等待搜索结果...")
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)  # 额外等待3秒
        
        # 5. 对搜索结果页面进行截图
        print("正在截图...")
        page.screenshot(path="baidu_search_result.png")
        print("截图已保存为 'baidu_search_result.png'")
        
        # 6. 成功提示
        print("🎉 演示成功完成！浏览器将保持打开15秒供您查看...")
        page.wait_for_timeout(15000)
        browser.close()
        print("浏览器已关闭。")

if __name__ == "__main__":
    run_playwright_demo()