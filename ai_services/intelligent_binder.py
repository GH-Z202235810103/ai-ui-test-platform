"""
intelligent_binder.py - AI测试意图与操作绑定器
改进版：将自然语言描述的测试步骤，自动映射到真正可执行的Playwright操作
作者：GH-Z202235810103
GitHub: https://github.com/GH-Z202235810103/ai-ui-test-platform
"""

import json
import re
from typing import Dict, List, Optional

class IntelligentTestBinder:
    def __init__(self):
        # 扩展的动作模板
        self.action_templates = {
            "打开": self._bind_navigate_action,
            "访问": self._bind_navigate_action,
            "导航": self._bind_navigate_action,
            "输入": self._bind_input_action,
            "填写": self._bind_input_action,
            "搜索": self._bind_search_action,
            "点击": self._bind_click_action,
            "选择": self._bind_click_action,
            "验证": self._bind_verify_action,
            "检查": self._bind_verify_action,
            "断言": self._bind_verify_action,
            "等待": self._bind_wait_action,
            "截图": self._bind_screenshot_action
        }
        
        # 网站知识库 - 包含常用网站的元素选择器
        self.website_knowledge = {
            "百度": {
                "url": "https://www.baidu.com",
                "search_box": "input#kw",
                "search_button": "input#su",
                "search_box_alt": ["input[name='wd']", "input[class*='search']"],
                "logo": "#lg img"
            },
            "淘宝": {
                "url": "https://www.taobao.com",
                "search_box": "input#q",
                "search_button": "button.btn-search",
                "search_box_alt": ["input[name='q']"],
                "logo": ".site-logo"
            },
            "京东": {
                "url": "https://www.jd.com",
                "search_box": "input#key",
                "search_button": "button.button",
                "search_box_alt": ["input[name='key']"],
                "logo": ".logo"
            },
            "bilibili": {
                "url": "https://www.bilibili.com",
                "search_box": "input.nav-search-keyword",
                "search_button": "div.nav-search-btn",
                "search_box_alt": ["input[placeholder='搜索']"],
                "logo": ".header-logo"
            },
            "知乎": {
                "url": "https://www.zhihu.com",
                "search_box": "input.SearchBar-input",
                "search_button": "button.SearchBar-searchButton",
                "search_box_alt": ["input[placeholder='搜索知乎']"]
            }
        }
        
        # 元素模式匹配
        self.element_patterns = {
            "搜索框": ["input[type='search']", "input[name*='search']", "input[placeholder*='搜索']"],
            "按钮": ["button", "input[type='button']", "input[type='submit']", "a.btn"],
            "输入框": ["input[type='text']", "input[type='email']", "input[type='password']", "textarea"],
            "链接": ["a", "a[href]"],
            "图片": ["img", "img[src]"],
            "下拉框": ["select", "div[role='combobox']"]
        }
        
        # 验证类型映射
        self.verification_patterns = {
            "显示": "is_visible",
            "存在": "is_visible", 
            "包含": "text_content_contains",
            "等于": "text_content_equals",
            "可点击": "is_enabled",
            "选中": "is_checked"
        }
    
    def bind_test_case(self, llm_generated_case: Dict) -> Dict:
        """将LLM生成的测试用例绑定为可执行操作"""
        bound_steps = []
        test_name = llm_generated_case.get("test_case_name", "AI生成测试用例")
        
        for step in llm_generated_case.get("test_steps", []):
            action_type = self._detect_action_type(step)
            
            if action_type in self.action_templates:
                bound_step = self.action_templates[action_type](step)
                if bound_step:
                    bound_steps.append(bound_step)
            else:
                # 无法识别时创建占位步骤
                bound_steps.append({
                    "step_type": "manual",
                    "original_description": step,
                    "executable_code": f"# TODO: 需要手动实现: {step}",
                    "status": "pending",
                    "message": "无法自动绑定，需要人工处理"
                })
        
        # 计算自动化程度
        auto_count = len([s for s in bound_steps if s.get("status") == "bound"])
        total_count = len(bound_steps)
        
        return {
            "test_name": test_name,
            "bound_steps": bound_steps,
            "automation_level": f"{auto_count}/{total_count}",
            "fully_bound": auto_count == total_count
        }
    
    def _detect_action_type(self, step_description: str) -> Optional[str]:
        """检测步骤中的动作类型"""
        step_lower = step_description.lower()
        
        for action in self.action_templates.keys():
            if action in step_lower:
                return action
        
        # 尝试英文关键词
        english_keywords = {
            "open": "打开",
            "navigate": "导航",
            "type": "输入",
            "enter": "输入",
            "click": "点击",
            "search": "搜索",
            "verify": "验证",
            "check": "检查",
            "assert": "断言",
            "wait": "等待"
        }
        
        for eng_keyword, chn_action in english_keywords.items():
            if eng_keyword in step_lower:
                return chn_action
        
        return None
    
    def _bind_navigate_action(self, step: str) -> Dict:
        """绑定导航动作 - 生成完整的goto代码"""
        target_site = None
        
        # 识别目标网站
        for site in self.website_knowledge.keys():
            if site in step:
                target_site = site
                break
        
        if target_site:
            url = self.website_knowledge[target_site]["url"]
            return {
                "step_type": "navigation",
                "original_description": step,
                "executable_code": f"await page.goto('{url}')\nawait page.wait_for_load_state('networkidle')",
                "python_code": f"page.goto('{url}')\npage.wait_for_load_state('networkidle')",
                "target_url": url,
                "wait_time": 2,
                "status": "bound",
                "confidence": "high"
            }
        else:
            # 提取URL或关键词
            url_match = re.search(r'(https?://[^\s]+)', step)
            if url_match:
                url = url_match.group(1)
                return {
                    "step_type": "navigation",
                    "original_description": step,
                    "executable_code": f"await page.goto('{url}')",
                    "python_code": f"page.goto('{url}')",
                    "target_url": url,
                    "status": "bound",
                    "confidence": "medium"
                }
        
        return None
    
    def _bind_input_action(self, step: str) -> Dict:
        """绑定输入动作 - 智能识别输入内容和目标元素"""
        # 提取输入内容
        content_patterns = [
            r'输入["\']?([^"\',，。]+?)["\']?(?:到|在)?',
            r'输入[：:]?\s*([^\s，。]+)',
            r'type[\s:]+["\']?([^"\']+)["\']?'
        ]
        
        content = None
        for pattern in content_patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                break
        
        if not content:
            content = "测试数据"
        
        # 识别目标元素
        element_info = self._identify_target_element(step)
        
        if element_info:
            selector = element_info["selector"]
            return {
                "step_type": "input",
                "original_description": step,
                "executable_code": f"await page.fill('{selector}', '{content}')",
                "python_code": f"page.fill('{selector}', '{content}')",
                "content": content,
                "selector": selector,
                "element_type": element_info["type"],
                "status": "bound",
                "confidence": element_info["confidence"]
            }
        else:
            # 无法识别元素，返回需要选择器
            return {
                "step_type": "input",
                "original_description": step,
                "executable_code": f"# 需要指定选择器\n# page.fill('selector', '{content}')",
                "python_code": f"# page.fill('{{selector}}', '{content}')",
                "content": content,
                "status": "partial",
                "message": "需要指定目标元素的选择器",
                "suggested_selectors": self.element_patterns["输入框"]
            }
    
    def _bind_search_action(self, step: str) -> Dict:
        """绑定搜索动作 - 特别处理搜索场景"""
        # 提取搜索关键词
        keyword = None
        keyword_patterns = [
            r'搜索["\']?([^"\',，。]+?)["\']?',
            r'搜索[：:]?\s*([^\s，。]+)',
            r'search[\s:]+["\']?([^"\']+)["\']?'
        ]
        
        for pattern in keyword_patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                keyword = match.group(1).strip()
                break
        
        if not keyword:
            keyword = "测试"
        
        # 识别目标网站
        target_site = None
        for site in self.website_knowledge.keys():
            if site in step:
                target_site = site
                break
        
        if target_site:
            site_info = self.website_knowledge[target_site]
            search_box = site_info.get("search_box")
            search_button = site_info.get("search_button")
            
            if search_box:
                code_lines = [
                    f"# 在{target_site}搜索'{keyword}'",
                    f"await page.fill('{search_box}', '{keyword}')",
                ]
                
                if search_button:
                    code_lines.append(f"await page.click('{search_button}')")
                else:
                    code_lines.append("await page.keyboard.press('Enter')")
                
                return {
                    "step_type": "search",
                    "original_description": step,
                    "executable_code": "\n".join(code_lines),
                    "python_code": f"page.fill('{search_box}', '{keyword}')\npage.keyboard.press('Enter')",
                    "keyword": keyword,
                    "website": target_site,
                    "search_box": search_box,
                    "search_button": search_button,
                    "status": "bound",
                    "confidence": "high"
                }
        
        # 通用搜索处理
        return {
            "step_type": "search",
            "original_description": step,
            "executable_code": f"# 通用搜索实现\nawait page.fill('input[type=\"search\"]', '{keyword}')\nawait page.keyboard.press('Enter')",
            "python_code": f"page.fill('input[type=\"search\"]', '{keyword}')\npage.keyboard.press('Enter')",
            "keyword": keyword,
            "status": "bound",
            "confidence": "medium"
        }
    
    def _bind_click_action(self, step: str) -> Dict:
        """绑定点击动作 - 智能识别点击目标"""
        # 提取点击目标
        target_patterns = [
            r'点击["\']?([^"\',，。]+?)["\']?',
            r'点击[：:]?\s*([^\s，。]+)',
            r'click[\s:]+["\']?([^"\']+)["\']?',
            r'选择["\']?([^"\',，。]+?)["\']?'
        ]
        
        target_text = None
        for pattern in target_patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                target_text = match.group(1).strip()
                break
        
        # 识别目标元素类型
        element_info = self._identify_target_element(step, target_text)
        
        if element_info:
            selector = element_info["selector"]
            return {
                "step_type": "click",
                "original_description": step,
                "executable_code": f"await page.click('{selector}')",
                "python_code": f"page.click('{selector}')",
                "target_text": target_text,
                "selector": selector,
                "element_type": element_info["type"],
                "status": "bound",
                "confidence": element_info["confidence"]
            }
        elif target_text:
            # 使用文本选择器
            return {
                "step_type": "click",
                "original_description": step,
                "executable_code": f"await page.click('text={target_text}')",
                "python_code": f"page.click('text={target_text}')",
                "target_text": target_text,
                "selector": f"text={target_text}",
                "status": "bound",
                "confidence": "medium",
                "note": "使用文本选择器，可能不够精确"
            }
        else:
            return {
                "step_type": "click",
                "original_description": step,
                "executable_code": "# 需要指定点击目标",
                "python_code": "# page.click('selector')",
                "status": "partial",
                "message": "无法识别点击目标",
                "suggested_selectors": self.element_patterns["按钮"]
            }
    
    def _bind_verify_action(self, step: str) -> Dict:
        """绑定验证动作 - 生成断言代码"""
        # 识别验证类型
        verification_type = None
        for v_type in self.verification_patterns.keys():
            if v_type in step:
                verification_type = v_type
                break
        
        if not verification_type:
            verification_type = "显示"  # 默认验证显示
        
        verify_method = self.verification_patterns.get(verification_type, "is_visible")
        
        # 提取验证目标
        target_match = re.search(r'(验证|检查|断言)[^，。]*?["\']?([^"\',，。]+?)["\']?(?:是否|是否|的状态)?', step)
        target_text = target_match.group(2) if target_match else "目标元素"
        
        # 根据验证类型生成代码
        if verify_method == "is_visible":
            code = f"assert await page.is_visible('text={target_text}')"
            py_code = f"assert page.is_visible('text={target_text}')"
        elif verify_method == "text_content_contains":
            # 需要提取包含的文本
            contains_match = re.search(r'包含["\']?([^"\',，。]+?)["\']?', step)
            expected_text = contains_match.group(1) if contains_match else "期望文本"
            code = f"assert '{expected_text}' in await page.text_content('body')"
            py_code = f"assert '{expected_text}' in page.text_content('body')"
        else:
            code = f"# 验证: {step}\n# 需要具体实现"
            py_code = f"# 验证: {step}"
        
        return {
            "step_type": "verification",
            "original_description": step,
            "executable_code": code,
            "python_code": py_code,
            "verification_type": verification_type,
            "verify_method": verify_method,
            "target": target_text,
            "status": "bound",
            "confidence": "medium"
        }
    
    def _bind_wait_action(self, step: str) -> Dict:
        """绑定等待动作"""
        # 提取等待时间
        time_match = re.search(r'(\d+)(?:秒|秒钟|s|秒种)', step)
        wait_time = int(time_match.group(1)) if time_match else 2
        
        return {
            "step_type": "wait",
            "original_description": step,
            "executable_code": f"await page.wait_for_timeout({wait_time * 1000})",
            "python_code": f"page.wait_for_timeout({wait_time * 1000})",
            "wait_time_seconds": wait_time,
            "status": "bound",
            "confidence": "high"
        }
    
    def _bind_screenshot_action(self, step: str) -> Dict:
        """绑定截图动作"""
        # 提取截图名称
        name_match = re.search(r'截图["\']?([^"\',，。]+?)["\']?', step)
        screenshot_name = name_match.group(1) if name_match else "screenshot"
        
        # 清理文件名
        screenshot_name = re.sub(r'[^\w\-]', '_', screenshot_name)
        
        return {
            "step_type": "screenshot",
            "original_description": step,
            "executable_code": f"await page.screenshot({{ path: '{screenshot_name}.png' }})",
            "python_code": f"page.screenshot(path='{screenshot_name}.png')",
            "filename": f"{screenshot_name}.png",
            "status": "bound",
            "confidence": "high"
        }
    
    def _identify_target_element(self, step: str, target_text: str = None) -> Dict:
        """智能识别目标元素"""
        step_lower = step.lower()
        
        # 检查是否是特定网站元素
        for site, info in self.website_knowledge.items():
            if site in step:
                # 检查是否是搜索框
                if any(keyword in step_lower for keyword in ["搜索框", "search box", "输入框"]):
                    selector = info.get("search_box") or info.get("search_box_alt", [""])[0]
                    if selector:
                        return {
                            "selector": selector,
                            "type": "search_box",
                            "confidence": "high"
                        }
                # 检查是否是搜索按钮
                elif any(keyword in step_lower for keyword in ["搜索按钮", "search button", "百度一下"]):
                    selector = info.get("search_button")
                    if selector:
                        return {
                            "selector": selector,
                            "type": "search_button", 
                            "confidence": "high"
                        }
        
        # 检查通用元素类型
        for element_type, patterns in self.element_patterns.items():
            type_keywords = {
                "搜索框": ["搜索框", "search box", "输入框", "文本框"],
                "按钮": ["按钮", "button", "btn", "submit"],
                "输入框": ["输入框", "输入", "文本框", "text field"],
                "链接": ["链接", "link", "a标签", "超链接"],
                "图片": ["图片", "image", "img", "图标"],
                "下拉框": ["下拉框", "下拉菜单", "select", "dropdown"]
            }
            
            if element_type in type_keywords:
                for keyword in type_keywords[element_type]:
                    if keyword in step_lower:
                        return {
                            "selector": patterns[0] if patterns else f"[data-type='{element_type}']",
                            "type": element_type,
                            "confidence": "medium"
                        }
        
        # 如果提供了目标文本，尝试使用文本选择器
        if target_text:
            return {
                "selector": f"text={target_text}",
                "type": "text_element",
                "confidence": "low"
            }
        
        return None
    
    def generate_executable_script(self, bound_case: Dict) -> str:
        """根据绑定结果生成完整的可执行Python脚本"""
        test_name = bound_case.get("test_name", "GeneratedTest")
        bound_steps = bound_case.get("bound_steps", [])
        
        script_lines = [
            '"""',
            f'AI生成的自动化测试脚本: {test_name}',
            '由智能绑定器自动生成',
            '"""',
            '',
            'from playwright.sync_api import sync_playwright',
            'import time',
            '',
            'def run_test():',
            '    """执行生成的测试用例"""',
            '    with sync_playwright() as p:',
            '        browser = p.chromium.launch(headless=True)',
            '        page = browser.new_page()',
            '',
            '        try:',
            '            print(f"🚀 开始执行测试: {test_name}")',
        ]
        
        for i, step in enumerate(bound_steps, 1):
            step_type = step.get("step_type", "unknown")
            original_desc = step.get("original_description", f"步骤{i}")
            python_code = step.get("python_code", "")
            
            if python_code and step.get("status") == "bound":
                # 添加注释和代码
                script_lines.append(f'            # 步骤{i}: {original_desc}')
                for code_line in python_code.split('\n'):
                    script_lines.append(f'            {code_line}')
                script_lines.append('')  # 空行
            else:
                script_lines.append(f'            # TODO: 步骤{i}: {original_desc}')
                script_lines.append(f'            # {step.get("message", "需要手动实现")}')
                script_lines.append('')
        
        script_lines.extend([
            '            print("✅ 测试执行完成")',
            '            return True',
            '',
            '        except Exception as e:',
            '            print(f"❌ 测试执行失败: {e}")',
            '            import traceback',
            '            traceback.print_exc()',
            '            return False',
            '',
            '        finally:',
            '            browser.close()',
            '',
            'if __name__ == "__main__":',
            '    success = run_test()',
            '    exit(0 if success else 1)'
        ])
        
        return '\n'.join(script_lines)


# 使用示例
if __name__ == "__main__":
    binder = IntelligentTestBinder()
    
    # 测试用例1: 百度搜索
    llm_case1 = {
        "test_case_name": "百度搜索自动化测试",
        "test_steps": [
            "打开百度首页",
            "在搜索框输入'人工智能'",
            "点击'百度一下'按钮",
            "验证搜索结果包含'AI'相关内容",
            "等待3秒",
            "截图保存搜索结果"
        ]
    }
    
    print("🧪 测试智能绑定功能:")
    print("=" * 60)
    
    bound_case1 = binder.bind_test_case(llm_case1)
    print("绑定结果:")
    print(json.dumps(bound_case1, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("生成的Python脚本:")
    print("=" * 60)
    
    script1 = binder.generate_executable_script(bound_case1)
    print(script1)
    
    print("\n" + "=" * 60)
    
    # 测试用例2: 淘宝搜索
    llm_case2 = {
        "test_case_name": "淘宝商品搜索测试",
        "test_steps": [
            "访问淘宝网",
            "搜索'手机'",
            "验证商品列表显示正常"
        ]
    }
    
    print("\n测试淘宝用例:")
    bound_case2 = binder.bind_test_case(llm_case2)
    print(f"自动化程度: {bound_case2['automation_level']}")
    
    for step in bound_case2['bound_steps']:
        print(f"  - {step['original_description']}: {step.get('status', 'unknown')}")