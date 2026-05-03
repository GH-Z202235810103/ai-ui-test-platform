"""
智能录制回放模块 - 基于Playwright（修复版）
"""
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.visual_locator import get_visual_locator

# 延迟导入 Playwright，避免在模块加载时触发错误
playwright = None
Browser = None
Page = None
BrowserContext = None
async_playwright = None

class RecordingSession:
    """录制会话"""
    def __init__(self, session_id: str, url: str, headless: bool = False):
        self.session_id = session_id
        self.url = url
        self.headless = headless
        self.actions: List[Dict] = []
        self.playwright_instance = None
        self.browser: Optional = None
        self.context: Optional = None
        self.page: Optional = None
        self.is_recording = False
    
    async def start(self):
        """开始录制（同步版本，不推荐使用）"""
        return await self.start_async()
    
    async def start_async(self):
        """异步开始录制"""
        try:
            print(f"[录制] 开始异步启动录制会话: {self.session_id}")
            print(f"[录制] 目标URL: {self.url}")
            print(f"[录制] 无头模式: {self.headless}")
            # 动态导入 Playwright
            print(f"[录制] 开始导入 Playwright")
            global playwright, Browser, Page, BrowserContext, async_playwright
            try:
                from playwright.async_api import async_playwright as _async_playwright
                from playwright.async_api import Browser as _Browser
                from playwright.async_api import Page as _Page
                from playwright.async_api import BrowserContext as _BrowserContext
                print(f"[录制] Playwright 导入成功")
            except Exception as e:
                print(f"[录制] Playwright 导入失败: {e}")
                raise
            
            async_playwright = _async_playwright
            Browser = _Browser
            Page = _Page
            BrowserContext = _BrowserContext
            
            print(f"[录制] 开始启动 Playwright 实例")
            self.playwright_instance = await async_playwright().start()
            print(f"[录制] Playwright 实例已启动")
            
            print(f"[录制] 开始启动浏览器")
            self.browser = await self.playwright_instance.chromium.launch(
                headless=self.headless,
                slow_mo=100,
                args=[
                    f"--window-size=1920,1080",
                    f"--window-position=0,0",
                    "--start-maximized",           # 启动时最大化
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--always-on-top",              # 保持窗口置顶
                    "--disable-extensions",
                    "--disable-popup-blocking",
                    "--no-sandbox",                 # 某些系统需要
                    "--disable-gpu",                 # 可选，减少干扰
                ]
            )
            print(f"[录制] 浏览器已启动 (无头模式: {self.headless})")
            
            print(f"[录制] 开始创建浏览器上下文")
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            print(f"[录制] 浏览器上下文已创建")
            
            print(f"[录制] 开始创建新页面")
            self.page = await self.context.new_page()
            print(f"[录制] 页面已创建")
            
            # 导航到目标URL
            print(f"[录制] 开始导航到: {self.url}")
            await self.page.goto(self.url, wait_until="networkidle")
            print(f"[录制] 已导航到: {self.url}")
            
            # 只有在非无头模式下才执行窗口操作
            if not self.headless:
                try:
                    screen_size = await self.page.evaluate('''
                        () => {
                            return {
                                width: window.screen.width,
                                height: window.screen.height
                            }
                        }
                    ''')
                    
                    await self.page.evaluate(f'''
                        () => {{
                            window.moveTo(0, 0);
                            window.resizeTo({screen_size['width']}, {screen_size['height']});
                            window.focus();
                        }}
                    ''')
                    
                    await self.page.bring_to_front()
                    await self.page.evaluate("window.focus();")
                    await asyncio.sleep(0.5)
                    print(f"[录制] 窗口已调整大小: {screen_size['width']}x{screen_size['height']}")
                except Exception as e:
                    print(f"[录制] 窗口操作失败: {e}")

            # 设置录制脚本
            await self._setup_recording_script()
            
            # 等待录制脚本就绪（监听器绑定完成）
            try:
                await self.page.wait_for_function("() => window.__recording_ready === true", timeout=10000)
                print("[录制] 录制脚本已就绪")
            except Exception as e:
                print(f"[录制] 等待录制脚本就绪失败: {e}")
                # 继续执行，不阻塞录制启动

            # 启动轮询
            asyncio.create_task(self._poll_actions())
            
            self.is_recording = True
            
            print(f"[录制] 会话 {self.session_id} 已成功启动")
        except Exception as e:
            print(f"[录制] 启动失败: {e}")
            # 清理资源
            await self.stop()
    
    async def _setup_recording_script(self):
        """设置录制脚本：使用全局事件监听捕获所有用户操作"""
        try:
            print("[录制] 开始注入全局录制脚本")

            # 定义暴露给 JavaScript 的回调函数
            async def on_action(action_type, selector, value=None, text_content=None, tag_name=None, element_name=None):
                print(f"[录制] Python收到操作: {action_type} {selector} {value}")
                action = {
                    "type": action_type,
                    "selector": selector,
                    "timestamp": datetime.now().isoformat(),
                    "text_content": text_content,
                    "tagName": tag_name,
                    "element_name": element_name
                }
                if value is not None:
                    action["text"] = value
                self.actions.append(action)
                print(f"[录制] 已记录操作: {action}")
                
                if action_type == 'click' and self.is_recording:
                    try:
                        # 检查页面是否仍然有效
                        if not self.page or self.page.is_closed():
                            print("[录制] 页面已关闭，跳过保存视觉模板")
                            return

                        element = await self.page.query_selector(selector)
                        if element:
                            # 检查元素是否可见
                            is_visible = await element.is_visible()
                            if not is_visible:
                                print(f"[录制] 元素不可见，跳过保存视觉模板: {selector}")
                                return

                            screenshot = await element.screenshot(timeout=5000)
                            import cv2
                            import numpy as np
                            nparr = np.frombuffer(screenshot, np.uint8)
                            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            if img is not None:
                                locator = get_visual_locator()
                                template_name = selector.replace('#', '').replace('.', '_').replace('[', '_').replace(']', '').replace('=', '_')[:30]
                                locator.save_template(img, template_name, "button")
                                print(f"[录制] 自动保存视觉模板: {template_name}")
                    except Exception as e:
                        # 仅在录制进行中时报告错误
                        if self.is_recording:
                            print(f"[录制] 保存视觉模板失败: {e}")

            # 尝试暴露函数给JavaScript
            try:
                await self.page.expose_function("py_on_action", on_action)
                print("[录制] 成功暴露py_on_action函数")
            except Exception as e:
                print(f"[录制] 暴露函数失败: {e}")
                # 继续执行，不阻塞录制启动

            # 注入 JavaScript 脚本
            try:
                await self.page.evaluate("""
                    () => {
                        console.log('[录制] 开始注入全局事件监听器');
                        // 初始化就绪标志
                        window.__recording_ready = false;

                        // 生成元素的精确选择器
                        function getSelector(el) {
                            if (!el) return '';

                            // 1. 优先使用 id（最精确）
                            if (el.id) {
                                return '#' + CSS.escape(el.id);
                            }

                            // 2. 尝试使用 name 属性
                            if (el.name) {
                                const tag = el.tagName.toLowerCase();
                                return tag + '[name="' + CSS.escape(el.name) + '"]';
                            }

                            // 3. 尝试使用 data 属性（常见的测试属性）
                            for (const attr of el.attributes) {
                                if (attr.name.startsWith('data-') && attr.name !== 'data-v-') {
                                    return el.tagName.toLowerCase() + '[' + attr.name + '="' + CSS.escape(attr.value) + '"]';
                                }
                            }

                            // 4. 使用 aria-label 或 title
                            if (el.getAttribute('aria-label')) {
                                return el.tagName.toLowerCase() + '[aria-label="' + CSS.escape(el.getAttribute('aria-label')) + '"]';
                            }
                            if (el.title) {
                                return el.tagName.toLowerCase() + '[title="' + CSS.escape(el.title) + '"]';
                            }

                            // 5. 对于表单元素，使用 type + placeholder
                            if (el.tagName === 'INPUT' || el.tagName === 'BUTTON') {
                                if (el.type) {
                                    let selector = el.tagName.toLowerCase() + '[type="' + el.type + '"]';
                                    if (el.placeholder) {
                                        selector += '[placeholder="' + CSS.escape(el.placeholder) + '"]';
                                    }
                                    return selector;
                                }
                            }

                            // 6. 使用类名，但添加标签前缀增加精确度
                            if (el.className && typeof el.className === 'string') {
                                const classes = el.className.split(/\\s+/).filter(c => c && !c.startsWith('_'));
                                if (classes.length > 0) {
                                    // 取前几个有意义的类名
                                    const meaningfulClasses = classes.slice(0, 2);
                                    return el.tagName.toLowerCase() + '.' + meaningfulClasses.map(c => CSS.escape(c)).join('.');
                                }
                            }

                            // 7. 使用文本内容（对于按钮和链接）
                            const text = (el.innerText || el.textContent || '').trim();
                            if (text && text.length < 20 && el.tagName !== 'BODY' && el.tagName !== 'HTML') {
                                if (el.tagName === 'BUTTON' || el.tagName === 'A') {
                                    return el.tagName.toLowerCase() + ':has-text("' + CSS.escape(text.substring(0, 30)) + '")';
                                }
                            }

                            // 8. 计算在父元素中的位置作为最后手段
                            const tag = el.tagName.toLowerCase();
                            if (el.parentElement) {
                                const siblings = Array.from(el.parentElement.children).filter(c => c.tagName === el.tagName);
                                if (siblings.length > 1) {
                                    const index = siblings.indexOf(el) + 1;
                                    return tag + ':nth-of-type(' + index + ')';
                                }
                            }

                            return tag;
                        }

                        // 全局点击监听
                        document.addEventListener('click', function(e) {
                            const target = e.target;
                            const selector = getSelector(target);
                            if (selector) {
                                const textContent = target.innerText || target.textContent || target.value || '';
                                const tagName = target.tagName.toLowerCase();
                                const name = target.name || target.title || target.alt || '';
                                if (window.py_on_action) {
                                    window.py_on_action('click', selector, null, textContent.trim().substring(0, 50), tagName, name);
                                }
                            }
                        }, true);

                        // 全局输入监听
                        document.addEventListener('input', function(e) {
                            console.log('[录制] input事件触发，目标:', e.target.tagName, e.target);
                            const target = e.target;
                            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
                                const selector = getSelector(target);
                                const value = target.value || target.innerText;
                                const tagName = target.tagName.toLowerCase();
                                const name = target.name || target.placeholder || '';
                                if (selector && window.py_on_action) {
                                    console.log('[录制] input事件有效，selector:', selector, 'value:', value);
                                    window.py_on_action('type', selector, value, null, tagName, name);
                                } else {
                                    console.log('[录制] input事件无法生成选择器或py_on_action不存在');
                                }
                            }
                        }, true);

                        // 全局按键监听（捕获回车）
                        document.addEventListener('keydown', function(e) {
                            if (e.key === 'Enter') {
                                const target = e.target;
                                const selector = getSelector(target);
                                if (selector && window.py_on_action) {
                                    const tagName = target.tagName.toLowerCase();
                                    window.py_on_action('press_enter', selector, null, null, tagName, null);
                                }
                            }
                        }, true);

                        // 所有监听器绑定完成，设置就绪标志
                        window.__recording_ready = true;
                        console.log('[录制] 监听器已就绪');
                    }
                """)
                print("[录制] 全局录制脚本注入成功")
            except Exception as e:
                print(f"[录制] 注入脚本失败: {e}")
                # 继续执行，不阻塞录制启动

            print("[录制] 全局录制脚本设置完成")

        except Exception as e:
            print(f"[录制] 设置录制脚本失败: {e}")
            # 不抛出异常，允许录制继续
    
    async def _poll_actions(self):
        """轮询检查录制状态，保持会话活跃"""
        while self.is_recording:
            try:
                if self.page is None or self.page.is_closed():
                    print("[录制] 页面已关闭，停止轮询")
                    break

                # 检查页面是否仍然响应
                try:
                    _ = await self.page.evaluate("() => document.readyState")
                except Exception as e:
                    print(f"[录制] 页面无响应: {e}")
                    break

                await asyncio.sleep(1)
            except Exception as e:
                if "closed" in str(e).lower():
                    print("[录制] 页面已关闭，停止轮询")
                    break
                print(f"[录制] 轮询检查失败: {e}")
                await asyncio.sleep(1)
    
    async def stop(self):
        """停止录制"""
        try:
            self.is_recording = False

            # 逐级关闭资源（从内到外）
            try:
                if self.page and not self.page.is_closed():
                    await self.page.close()
                if self.context:
                    await self.context.close()
                if self.browser:
                    await self.browser.close()
                if self.playwright_instance:
                    await self.playwright_instance.stop()
            except Exception as close_error:
                print(f"[录制] 关闭资源失败: {close_error}")

            print(f"[录制] 会话 {self.session_id} 已停止")
            print(f"[录制] 实际录制的动作数量: {len(self.actions)}")
            print(f"[录制] 录制的动作: {self.actions}")

            return self.actions
        except Exception as e:
            print(f"[录制] 停止失败: {e}")
            return self.actions
    
    async def add_action(self, action: Dict):
        """添加动作"""
        self.actions.append(action)

# 全局录制会话存储
recording_sessions = {}
# 全局任务存储，防止任务被垃圾回收
recording_tasks = {}

async def start_recording(url: str, headless: bool = False) -> str:
    """开始录制"""
    try:
        session_id = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"[录制] 开始创建录制会话: {session_id}")

        # 创建会话对象
        session = RecordingSession(session_id, url, headless)
        recording_sessions[session_id] = session

        # 异步启动录制，保存任务引用防止被垃圾回收
        import asyncio
        task = asyncio.create_task(session.start_async())
        recording_tasks[session_id] = task

        # 添加任务完成回调，清理任务引用
        def on_task_done(t):
            if session_id in recording_tasks:
                del recording_tasks[session_id]
                print(f"[录制] 任务引用已清理: {session_id}")

        task.add_done_callback(on_task_done)

        print(f"[录制] 会话已创建并异步启动: {session_id}")
        return session_id
    except Exception as e:
        print(f"[错误] 开始录制失败: {e}")
        raise

async def stop_recording(recording_id: str) -> List[Dict]:
    """停止录制"""
    try:
        print(f"[停止录制] 尝试停止录制会话: {recording_id}")
        session = recording_sessions.get(recording_id)
        if session:
            print(f"[停止录制] 找到会话: {recording_id}")
            actions = await session.stop()
            print(f"[停止录制] 从会话获取的动作数量: {len(actions)}")
            del recording_sessions[recording_id]

            # 清理任务引用
            if recording_id in recording_tasks:
                task = recording_tasks[recording_id]
                if not task.done():
                    task.cancel()
                    print(f"[停止录制] 已取消未完成的任务: {recording_id}")
                del recording_tasks[recording_id]
                print(f"[停止录制] 已清理任务引用: {recording_id}")

            return actions
        else:
            print(f"[停止录制] 未找到会话: {recording_id}")
            return []
    except Exception as e:
        print(f"[错误] 停止录制失败: {e}")
        return []

async def replay_recording(recording_id: str, url: str, actions: List[Dict], headless: bool = True) -> Dict:
    """回放录制"""
    try:
        # 检查是否有操作需要回放
        if not actions or len(actions) == 0:
            print("[回放] 没有可回放的操作")
            return {
                "success": False,
                "message": "没有可回放的操作",
                "actions_executed": 0,
                "actions_total": 0
            }
        
        # 动态导入 Playwright
        global playwright, Browser, Page, BrowserContext, async_playwright
        from playwright.async_api import async_playwright as _async_playwright
        from playwright.async_api import Browser as _Browser
        from playwright.async_api import Page as _Page
        from playwright.async_api import BrowserContext as _BrowserContext
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        
        async_playwright = _async_playwright
        Browser = _Browser
        Page = _Page
        BrowserContext = _BrowserContext
        
        print("[回放] 开始初始化浏览器")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
                slow_mo=100,
                args=[
                    f"--window-size=1920,1080",
                    f"--window-position=0,0",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--always-on-top",
                    "--disable-extensions",
                    "--disable-popup-blocking"
                ]
            )
            
            print("[回放] 浏览器启动成功")
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            
            page = await context.new_page()
            
            # 获取屏幕尺寸并调整窗口到全屏
            screen_size = await page.evaluate('''
                () => {
                    return {
                        width: window.screen.width,
                        height: window.screen.height
                    }
                }
            ''')
            
            await page.evaluate(f'''
                () => {{
                    window.moveTo(0, 0);
                    window.resizeTo({screen_size['width']}, {screen_size['height']});
                    window.focus();
                }}
            ''')
            
            await page.bring_to_front()
            print(f"[回放] 页面创建成功，窗口全屏显示，大小：{screen_size['width']}x{screen_size['height']}")
            
            # 导航到目标URL
            print(f"[回放] 导航到: {url}")
            await page.goto(url, wait_until="networkidle")
            await page.bring_to_front()
            await page.evaluate("window.focus();")
            await asyncio.sleep(0.5)
            print(f"[回放] 页面加载完成: {url}")
            
            await page.evaluate(f'''
                () => {{
                    window.moveTo(0, 0);
                    window.resizeTo({screen_size['width']}, {screen_size['height']});
                }}
            ''')
            
            # 执行录制的动作
            actions_executed = 0
            print(f"[回放] 开始执行录制的动作，共 {len(actions)} 个动作")
            
            try:
                for i, action in enumerate(actions):
                    print(f"[回放] 执行动作 {i+1}/{len(actions)}: {action}")
                    
                    await page.wait_for_load_state("networkidle")                    
                    action_type = action.get('type')
                    selector = action.get('selector')
                    text = action.get('text')
                    
                    if action_type == 'click':
                        print(f"[回放] 点击元素: {selector}")
                        try:
                            await page.click(selector, timeout=5000)
                            print(f"[回放] 点击成功: {selector}")
                        except Exception as e:
                            print(f"[回放] 选择器点击失败，尝试视觉定位: {e}")
                            try:
                                template_name = selector.replace('#', '').replace('.', '_').replace('[', '_').replace(']', '').replace('=', '_')[:30]
                                screenshot = await page.screenshot()
                                import cv2
                                import numpy as np
                                nparr = np.frombuffer(screenshot, np.uint8)
                                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                locator = get_visual_locator()
                                position = locator.locate_element(img, template_name)
                                if position:
                                    print(f"[回放] 视觉定位成功: {template_name} at ({position['x']}, {position['y']}), 匹配度: {position['confidence']}")
                                    await page.mouse.click(position["x"], position["y"])
                                    print(f"[回放] 视觉定位点击成功")
                                else:
                                    print(f"[回放] 视觉定位失败: 未找到模板 {template_name}")
                            except Exception as ve:
                                print(f"[回放] 视觉定位失败: {ve}")
                    
                    elif action_type == 'type':
                        print(f"[回放] 输入文本: {text} 到元素: {selector}")
                        try:
                            await page.fill(selector, text, timeout=5000)
                            print(f"[回放] 输入成功: {text}")
                        except Exception as e:
                            print(f"[回放] 选择器输入失败，尝试视觉定位: {e}")
                            try:
                                template_name = selector.replace('#', '').replace('.', '_').replace('[', '_').replace(']', '').replace('=', '_')[:30]
                                screenshot = await page.screenshot()
                                import cv2
                                import numpy as np
                                nparr = np.frombuffer(screenshot, np.uint8)
                                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                locator = get_visual_locator()
                                position = locator.locate_element(img, template_name)
                                if position:
                                    print(f"[回放] 视觉定位成功: {template_name} at ({position['x']}, {position['y']}), 匹配度: {position['confidence']}")
                                    await page.mouse.click(position["x"], position["y"])
                                    await asyncio.sleep(0.3)
                                    await page.keyboard.type(text)
                                    print(f"[回放] 视觉定位输入成功")
                                else:
                                    print(f"[回放] 视觉定位失败: 未找到模板 {template_name}")
                            except Exception as ve:
                                print(f"[回放] 视觉定位失败: {ve}")
                    
                    elif action_type == 'press_enter':
                        print(f"[回放] 按Enter键: {selector}")
                        try:
                            await page.press(selector, 'Enter', timeout=5000)
                            print(f"[回放] Enter键成功")
                        except Exception as e:
                            print(f"[回放] Enter键失败: {e}")
                    
                    actions_executed += 1
                    print(f"[回放] 动作 {i+1} 执行成功")
                    await asyncio.sleep(2)
                
                print("[回放] 所有操作执行完成")
                await asyncio.sleep(2)  # 等待2秒，让用户观察结果
                # 显示倒计时
                if not headless:
                    try:
                        # 再次确保窗口在前台
                        await page.bring_to_front()
                        # await page.evaluate("window.focus();")
                        # await asyncio.sleep(0.2)
                        # # 如果最后一个操作可能引起导航，等待网络空闲
                        # await page.wait_for_load_state("networkidle")
                        print("[回放] 显示倒计时")
                        await page.evaluate('''
                            () => {
                                const countdown = document.createElement("div");
                                countdown.style.position = "fixed";
                                countdown.style.top = "50%";
                                countdown.style.left = "50%";
                                countdown.style.transform = "translate(-50%, -50%)";
                                countdown.style.fontSize = "120px";
                                countdown.style.fontWeight = "bold";
                                countdown.style.color = "white";
                                countdown.style.backgroundColor = "rgba(0, 0, 0, 0.9)";
                                countdown.style.padding = "60px";
                                countdown.style.borderRadius = "20px";
                                countdown.style.zIndex = "99999";
                                countdown.style.textAlign = "center";
                                countdown.style.boxShadow = "0 0 50px rgba(0, 0, 0, 0.5)";
                                document.body.appendChild(countdown);
                                let seconds = 3;
                                countdown.textContent = seconds;
                                const interval = setInterval(() => {
                                    seconds--;
                                    if (seconds > 0) {
                                        countdown.textContent = seconds;
                                    } else {
                                        clearInterval(interval);
                                        countdown.textContent = "回放完成";
                                        setTimeout(() => {
                                            countdown.remove();
                                        }, 1000);
                                    }
                                }, 1000);
                            }
                        ''')
                        await asyncio.sleep(4)
                    except Exception as e:
                        print(f"[回放] 显示倒计时失败: {e}")
                
            except Exception as e:
                print(f"[回放] 执行操作失败: {e}")
                await browser.close()
                return {
                    "success": False,
                    "message": f"回放失败: {str(e)}",
                    "actions_executed": actions_executed,
                    "actions_total": len(actions)
                }
            
            await asyncio.sleep(1)
            await browser.close()
            print("[回放] 浏览器已关闭")
            
            return {
                "success": True,
                "message": f"回放完成，执行了 {actions_executed} 个操作",
                "actions_executed": actions_executed,
                "actions_total": len(actions)
            }
            
    except Exception as e:
        print(f"[回放] 回放失败: {e}")
        return {
            "success": False,
            "message": f"回放失败: {str(e)}",
            "actions_executed": 0,
            "actions_total": len(actions) if actions else 0
        }