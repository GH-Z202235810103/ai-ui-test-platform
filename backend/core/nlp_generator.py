"""
自然语言用例生成模块 - 基于LLM (DeepSeek)
"""
import json
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_services.demo_llm import LLMTestCaseGenerator

class NLPTestCaseGenerator:
    """自然语言测试用例生成器"""
    
    def __init__(self):
        self.llm_generator = None
        self._init_llm()
        
        self.prompt_templates = {
            "ui_test": """
你是一个专业的UI自动化测试工程师。请根据以下测试需求，生成结构化的测试用例。

测试需求：{description}

项目信息：
- 项目名称：{project_name}
- 基础URL：{base_url}

请生成一个包含以下结构的测试用例JSON：
{{
    "name": "测试用例名称（简洁明确）",
    "description": "测试用例详细描述",
    "steps": [
        "步骤1",
        "步骤2"
    ],
    "expected_results": [
        "预期结果1"
    ]
}}

重要要求：
1. 步骤描述必须极其简洁，每个步骤不超过10个字
2. 如果用户需求本身很简洁（如"搜索B站"），直接将其作为唯一步骤，不要拆分
3. 只有用户需求复杂时才拆分为多个步骤
4. 步骤格式示例："搜索B站"、"登录系统"、"提交表单"
5. 不要添加"打开网页"、"验证结果"等冗余步骤
6. 步骤数量控制在1-3个

示例：
输入："搜索B站"
输出：
{{
    "name": "搜索B站",
    "description": "在百度搜索B站",
    "steps": ["搜索B站"],
    "expected_results": ["搜索结果正确显示"]
}}

输入："登录系统并查看个人中心"
输出：
{{
    "name": "登录并查看个人中心",
    "description": "登录系统后查看个人中心页面",
    "steps": ["登录系统", "查看个人中心"],
    "expected_results": ["登录成功", "个人中心正常显示"]
}}
""",
            
            "search_test": """
你是一个专业的UI自动化测试工程师。请生成搜索功能的测试用例。

测试需求：{description}

请生成JSON格式的测试用例：
{{
    "name": "测试用例名称",
    "description": "描述",
    "steps": ["步骤"],
    "expected_results": ["预期结果"]
}}

要求：
1. 步骤极其简洁，不超过10个字
2. 如果需求是"搜索xxx"，直接输出一个步骤："搜索xxx"
3. 不要添加"打开网页"、"点击搜索"等冗余步骤
""",

            "login_test": """
你是一个专业的UI自动化测试工程师。请生成登录功能的测试用例。

测试需求：{description}

请生成JSON格式的测试用例：
{{
    "name": "测试用例名称",
    "description": "描述",
    "steps": ["步骤"],
    "expected_results": ["预期结果"]
}}

要求：
1. 步骤极其简洁，不超过10个字
2. 如果需求是"登录系统"，直接输出一个步骤："登录系统"
3. 只有复杂需求才拆分步骤
""",

            "form_test": """
你是一个专业的UI自动化测试工程师。请生成表单填写功能的测试用例。

测试需求：{description}

请生成JSON格式的测试用例：
{{
    "name": "测试用例名称",
    "description": "描述",
    "steps": ["步骤"],
    "expected_results": ["预期结果"]
}}

要求：
1. 步骤极其简洁，不超过10个字
2. 如果需求简单，直接作为唯一步骤
3. 不要添加冗余的"打开页面"、"验证结果"步骤
"""
        }
    
    def _init_llm(self):
        """初始化LLM生成器"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if api_key:
                self.llm_generator = LLMTestCaseGenerator(
                    api_url="https://api.deepseek.com/v1/chat/completions",
                    api_key=api_key,
                    model="deepseek-chat"
                )
                print("[NLP生成器] DeepSeek LLM已初始化")
            else:
                print("[NLP生成器] 未找到DEEPSEEK_API_KEY，将使用规则引擎")
        except Exception as e:
            print(f"[NLP生成器] LLM初始化失败: {e}，将使用规则引擎")
    
    def generate_test_case(
        self, 
        description: str,
        project_name: str = "默认项目",
        base_url: str = "https://www.example.com",
        template_type: str = None
    ) -> Dict:
        """
        生成测试用例
        
        Args:
            description: 测试需求描述
            project_name: 项目名称
            base_url: 基础URL
            template_type: 提示模板类型（自动识别）
        
        Returns:
            生成的测试用例字典
        """
        if template_type is None:
            template_type = self._detect_test_type(description)
        
        template = self.prompt_templates.get(template_type, self.prompt_templates["ui_test"])
        prompt = template.format(
            description=description,
            project_name=project_name,
            base_url=base_url
        )
        
        if self.llm_generator:
            try:
                print(f"[NLP生成器] 使用DeepSeek生成测试用例（类型：{template_type}）...")
                llm_result = self.llm_generator.generate_test_case(prompt)
                
                if llm_result:
                    if "steps" not in llm_result:
                        llm_result["steps"] = ["执行测试操作", "验证结果"]
                    if "name" not in llm_result:
                        llm_result["name"] = f"AI生成测试 - {description[:20]}"
                    if "description" not in llm_result:
                        llm_result["description"] = description
                    
                    llm_result["steps"] = self._normalize_steps(llm_result.get("steps", []))
                    llm_result["created_at"] = datetime.now().isoformat()
                    print(f"[NLP生成器] DeepSeek生成成功: {llm_result.get('name')}")
                    return llm_result
                else:
                    print("[NLP生成器] DeepSeek返回空结果，降级到规则引擎")
            except Exception as e:
                print(f"[NLP生成器] DeepSeek调用失败: {e}，降级到规则引擎")
        
        print("[NLP生成器] 使用规则引擎生成测试用例")
        test_case = self._generate_with_rules(description, base_url)
        return test_case
    
    def _detect_test_type(self, description: str) -> str:
        """根据描述自动识别测试类型"""
        desc_lower = description.lower()
        
        if any(kw in desc_lower for kw in ["搜索", "search", "查询", "检索"]):
            return "search_test"
        elif any(kw in desc_lower for kw in ["登录", "login", "注册", "register", "signin", "signup"]):
            return "login_test"
        elif any(kw in desc_lower for kw in ["表单", "form", "填写", "提交", "注册"]):
            return "form_test"
        else:
            return "ui_test"
    
    def _normalize_steps(self, steps: List) -> List[str]:
        """规范化步骤描述，过滤冗余步骤"""
        redundant_keywords = [
            "打开网页", "打开页面", "打开网站", "打开浏览器",
            "验证结果", "验证成功", "检查结果", "确认结果",
            "等待加载", "等待页面", "等待显示"
        ]
        
        normalized = []
        for step in steps:
            if isinstance(step, dict):
                action = step.get("action", "")
                target = step.get("target", "")
                value = step.get("value", "")
                if value:
                    step_text = f"{action}{target}，输入{value}"
                elif target:
                    step_text = f"{action}{target}"
                else:
                    step_text = action
            else:
                step_text = str(step)
            
            step_text = re.sub(r'[步骤\d：:]+', '', step_text)
            step_text = step_text.strip()
            
            if any(kw in step_text for kw in redundant_keywords):
                continue
            
            if step_text:
                normalized.append(step_text)
        
        return normalized
    
    def _generate_with_rules(self, description: str, base_url: str) -> Dict:
        """
        使用规则引擎生成测试用例（降级方案）
        
        Args:
            description: 测试需求描述
            base_url: 基础URL
        
        Returns:
            生成的测试用例字典
        """
        keywords = self._extract_keywords(description)
        name = self._generate_test_name(description, keywords)
        steps = self._generate_test_steps(description, keywords, base_url)
        
        # 生成预期结果
        expected_results = self._generate_expected_results(description, keywords)
        
        test_case = {
            "name": name,
            "description": description,
            "priority": "medium",
            "steps": steps,
            "expected_results": expected_results,
            "created_at": datetime.now().isoformat()
        }
        
        return test_case
    
    def _extract_keywords(self, description: str) -> Dict[str, str]:
        """
        从描述中提取关键词
        
        Args:
            description: 测试需求描述
        
        Returns:
            关键词字典
        """
        keywords = {}
        
        # 提取URL
        url_pattern = r'https?://[^\s]+'
        url_match = re.search(url_pattern, description)
        if url_match:
            keywords["url"] = url_match.group()
        
        # 提取测试对象
        if "搜索" in description:
            keywords["action"] = "搜索"
            keywords["element_type"] = "search_box"
        elif "登录" in description:
            keywords["action"] = "登录"
            keywords["element_type"] = "login_form"
        elif "注册" in description:
            keywords["action"] = "注册"
            keywords["element_type"] = "register_form"
        elif "购物车" in description:
            keywords["action"] = "购物车"
            keywords["element_type"] = "cart"
        elif "订单" in description:
            keywords["action"] = "订单"
            keywords["element_type"] = "order"
        else:
            keywords["action"] = "操作"
            keywords["element_type"] = "element"
        
        # 提取测试值
        value_pattern = r'[\'"]([^\'"]+)[\'"]'
        value_matches = re.findall(value_pattern, description)
        if value_matches:
            keywords["test_values"] = value_matches
        
        return keywords
    
    def _generate_test_name(self, description: str, keywords: Dict) -> str:
        """
        生成测试用例名称
        
        Args:
            description: 测试需求描述
            keywords: 关键词字典
        
        Returns:
            测试用例名称
        """
        action = keywords.get("action", "功能")
        
        # 简化描述
        simplified_desc = description[:50] + "..." if len(description) > 50 else description
        
        name = f"{action}功能测试 - {simplified_desc}"
        
        return name
    
    def _generate_test_steps(self, description: str, keywords: Dict, base_url: str) -> List[str]:
        """生成测试步骤 - 简洁版"""
        action = keywords.get("action", "操作")
        test_values = keywords.get("test_values", [])
        
        if action == "搜索":
            if test_values:
                return [f"搜索{test_values[0]}"]
            return ["搜索"]
        
        elif action == "登录":
            return ["登录系统"]
        
        elif action == "注册":
            return ["注册账号"]
        
        elif action == "购物车":
            return ["添加购物车"]
        
        elif action == "订单":
            return ["提交订单"]
        
        else:
            if test_values:
                return [f"{action}{test_values[0]}"]
            return [action]
    
    def _generate_expected_results(self, description: str, keywords: Dict) -> List[str]:
        """生成预期结果"""
        results = []
        action = keywords.get("action", "操作")
        
        results.append(f"{action}操作成功完成")
        if action == "搜索":
            results.append("搜索结果页面正确显示")
            results.append("搜索结果与关键词相关")
            results.append("搜索结果按预期排序")
        
        elif action == "登录":
            results.append("成功登录到系统")
            results.append("用户信息正确显示")
            results.append("跳转到登录后的首页")
        
        elif action == "注册":
            results.append("注册信息成功保存")
            results.append("用户账号创建成功")
            results.append("收到注册确认通知")
        
        else:
            results.append("页面响应正确")
            results.append("数据保存成功")
            results.append("界面显示正常")
        
        return results
    
    def optimize_test_case(self, test_case: Dict, feedback: str) -> Dict:
        """
        根据反馈优化测试用例
        
        Args:
            test_case: 原始测试用例
            feedback: 用户反馈
        
        Returns:
            优化后的测试用例
        """
        optimized = test_case.copy()
        
        # 根据反馈调整测试用例
        if "更多验证" in feedback:
            # 添加更多验证步骤
            additional_steps = [
                "验证页面元素是否正确显示",
                "检查数据一致性",
                "验证响应时间是否在预期范围内"
            ]
            optimized["steps"].extend(additional_steps)
        
        elif "简化步骤" in feedback:
            # 简化测试步骤
            if len(optimized["steps"]) > 6:
                optimized["steps"] = optimized["steps"][:6]
        
        elif "增加边界测试" in feedback:
            # 添加边界测试步骤
            boundary_steps = [
                "测试空值输入",
                "测试超长输入",
                "测试特殊字符输入"
            ]
            optimized["steps"].extend(boundary_steps)
        
        # 更新描述
        optimized["description"] = f"{optimized['description']}（已根据反馈优化）"
        optimized["optimized_at"] = datetime.now().isoformat()
        
        return optimized
    
    def validate_test_case(self, test_case: Dict) -> Dict:
        """
        验证测试用例质量
        
        Args:
            test_case: 测试用例字典
        
        Returns:
            验证结果字典
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 0
        }
        
        # 检查必需字段
        required_fields = ["name", "description", "steps"]
        for field in required_fields:
            if field not in test_case or not test_case[field]:
                validation["errors"].append(f"缺少必需字段：{field}")
                validation["valid"] = False
        
        # 检查步骤数量
        steps = test_case.get("steps", [])
        if len(steps) < 2:
            validation["warnings"].append("测试步骤过少，建议至少2个步骤")
        elif len(steps) > 10:
            validation["warnings"].append("测试步骤过多，建议拆分为多个测试用例")
        
        # 检查步骤描述质量
        for i, step in enumerate(steps):
            if len(step) < 5:
                validation["warnings"].append(f"步骤{i+1}描述过短")
            elif len(step) > 100:
                validation["warnings"].append(f"步骤{i+1}描述过长")
        
        # 计算质量分数
        base_score = 100
        base_score -= len(validation["errors"]) * 20
        base_score -= len(validation["warnings"]) * 5
        validation["score"] = max(0, base_score)
        
        return validation

# 全局生成器实例
_global_generator: Optional[NLPTestCaseGenerator] = None

def get_nlp_generator() -> NLPTestCaseGenerator:
    """获取全局生成器实例"""
    global _global_generator
    
    if _global_generator is None:
        _global_generator = NLPTestCaseGenerator()
    
    return _global_generator

def generate_test_case_from_nlp(
    description: str,
    project_name: str = "默认项目",
    base_url: str = "https://www.example.com"
) -> Dict:
    """
    从自然语言描述生成测试用例
    
    Args:
        description: 测试需求描述
        project_name: 项目名称
        base_url: 基础URL
    
    Returns:
        生成的测试用例字典
    """
    generator = get_nlp_generator()
    return generator.generate_test_case(description, project_name, base_url)