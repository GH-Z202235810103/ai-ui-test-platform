"""
intelligent_binder.py - AI测试意图与操作绑定器
核心思想：将自然语言描述的测试步骤，自动映射到可执行的屏幕操作
作者：GH-Z202235810103
GitHub: https://github.com/GH-Z202235810103/ai-ui-test-platform
"""

import json
import re

class IntelligentTestBinder:
    def __init__(self):
        self.action_templates = {
            "打开": self._bind_navigate_action,
            "访问": self._bind_navigate_action,
            "输入": self._bind_input_action,
            "搜索": self._bind_search_action,
            "点击": self._bind_click_action,
            "验证": self._bind_verify_action,
            "检查": self._bind_verify_action
        }
    
    def bind_test_case(self, llm_generated_case):
        """将LLM生成的测试用例绑定为可执行操作"""
        bound_steps = []
        
        for step in llm_generated_case.get("test_steps", []):
            action_type = self._detect_action_type(step)
            
            if action_type in self.action_templates:
                bound_step = self.action_templates[action_type](step)
                bound_steps.append(bound_step)
            else:
                bound_steps.append({
                    "原始描述": step,
                    "状态": "待处理",
                    "建议": "需要手动录制或提供更多信息"
                })
        
        return {
            "test_name": llm_generated_case.get("test_case_name"),
            "bound_steps": bound_steps,
            "自动化程度": f"{len([s for s in bound_steps if s.get('状态') != '待处理'])}/{len(bound_steps)}"
        }
    
    def _detect_action_type(self, step_description):
        """检测步骤中的动作类型"""
        for action in self.action_templates.keys():
            if action in step_description:
                return action
        return None
    
    def _bind_navigate_action(self, step):
        """绑定导航动作"""
        if "百度" in step:
            url = "https://www.baidu.com"
        elif "淘宝" in step:
            url = "https://www.taobao.com"
        elif "B站" in step or "bilibili" in step:
            url = "https://www.bilibili.com"
        else:
            url = "待指定"
        
        return {
            "动作类型": "导航",
            "原始描述": step,
            "执行代码": f'page.goto("{url}")',
            "状态": "已绑定",
            "验证方式": "page.wait_for_load_state('networkidle')"
        }
    
    def _bind_input_action(self, step):
        """绑定输入动作"""
        content_match = re.search(r'输入["\']?([^"\',，。]+)["\']?', step)
        content = content_match.group(1) if content_match else "待指定文本"
        
        return {
            "动作类型": "输入",
            "原始描述": step,
            "执行代码": f'page.fill("input selector", "{content}")',
            "状态": "部分绑定",
            "待完善": "需要指定具体的选择器(selector)"
        }
    
    def _bind_search_action(self, step):
        """绑定搜索动作"""
        return {
            "动作类型": "搜索",
            "原始描述": step,
            "执行代码": 'page.fill("input[type=search]", "搜索内容")',
            "状态": "部分绑定",
            "待完善": "需要指定具体的搜索内容和选择器"
        }
    
    def _bind_click_action(self, step):
        """绑定点击动作"""
        return {
            "动作类型": "点击",
            "原始描述": step,
            "执行代码": 'page.click("button selector")',
            "状态": "部分绑定",
            "待完善": "需要指定具体的选择器(selector)",
            "建议": "使用OpenCV录制功能获取元素位置"
        }
    
    def _bind_verify_action(self, step):
        """绑定验证动作"""
        return {
            "动作类型": "验证",
            "原始描述": step,
            "执行代码": 'assert page.is_visible("element selector")',
            "状态": "部分绑定",
            "待完善": "需要指定具体的验证元素和断言条件"
        }

# 使用示例
if __name__ == "__main__":
    binder = IntelligentTestBinder()
    
    llm_case = {
        "test_case_name": "百度搜索测试",
        "test_steps": [
            "打开百度首页",
            "在搜索框输入'自动化测试'",
            "点击'百度一下'按钮",
            "验证搜索结果页面正常显示"
        ]
    }
    
    bound_case = binder.bind_test_case(llm_case)
    print(json.dumps(bound_case, ensure_ascii=False, indent=2))