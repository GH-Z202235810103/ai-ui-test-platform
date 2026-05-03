"""
LLM测试用例生成演示 - DeepSeek API (安全版本)
AI与行为驱动的UI自动化测试平台 - 第三个技术支柱
作者：GH-Z202235810103
GitHub: https://github.com/GH-Z202235810103/ai-ui-test-platform
"""

import json
import time
import requests
import os
from pathlib import Path
from typing import Optional, Dict, Any

# 加载环境变量
def load_env():
    """从.env文件加载环境变量"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()

class LLMTestCaseGenerator:
    """LLM测试用例生成器 - 增强容错性和可配置性"""
    def __init__(self, api_url: str, api_key: str, model: str = "deepseek-chat"):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model  # 支持参数化配置模型
        self.session = requests.Session()
        # 设置更健壮的重试策略
        self.session.mount('https://', requests.adapters.HTTPAdapter(
            max_retries=requests.packages.urllib3.util.retry.Retry(
                total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
            )
        ))

    def generate_test_case(self, prompt: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        生成测试用例，增加失败重试和格式校验
        :param prompt: 生成用例的提示词
        :param max_retries: 最大重试次数
        :return: 解析后的测试用例字典，失败返回None
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()  # 触发HTTP错误（4xx/5xx）
                
                # 解析响应（增加多层校验）
                result = response.json()
                if not result.get("choices") or len(result["choices"]) == 0:
                    raise ValueError("LLM返回结果中无有效choices")
                
                content = result["choices"][0].get("message", {}).get("content")
                if not content:
                    raise ValueError("LLM返回内容为空")
                
                # 解析测试用例
                test_case = self.parse_test_case(content)
                if test_case:
                    return test_case
                else:
                    print(f"⚠️ 第{attempt+1}次尝试：LLM返回内容格式异常，重试中...")
                    
            except requests.exceptions.RequestException as e:
                # 网络错误：打印详细信息，增加重试间隔
                print(f"⚠️ 第{attempt+1}次尝试：网络请求失败 - {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = (attempt + 1) * 2  # 指数退避：2s, 4s, 6s...
                    print(f"⏳ 等待{sleep_time}秒后重试...")
                    time.sleep(sleep_time)
            except (KeyError, json.JSONDecodeError, ValueError) as e:
                # 解析错误：快速重试
                print(f"⚠️ 第{attempt+1}次尝试：响应解析失败 - {str(e)}")
                continue
        
        print("❌ 达到最大重试次数，生成测试用例失败")
        return None

    def parse_test_case(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析LLM返回的测试用例，增强容错性
        :param content: LLM返回的原始内容
        :return: 解析后的字典，失败返回None
        """
        try:
            # 兼容多种格式：```json、```JSON、无标记等
            content = content.strip()
            if "```json" in content.lower():
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content and "}" in content:
                # 直接提取JSON部分（兼容无代码块标记的情况）
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                json_str = content[start_idx:end_idx]
            else:
                return None
            
            # 严格解析JSON
            return json.loads(json_str)
        except (IndexError, json.JSONDecodeError):
            return None

# 向后兼容的别名
class DeepSeekTestGenerator(LLMTestCaseGenerator):
    """DeepSeek测试生成器 - 兼容旧代码"""
    def __init__(self):
        # 从环境变量读取API密钥
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key:
            print("⚠️ 警告: 未找到DEEPSEEK_API_KEY环境变量，AI生成功能将使用模拟数据")
        
        # 使用默认配置初始化
        super().__init__(
            api_url="https://api.deepseek.com/v1/chat/completions",
            api_key=api_key,
            model="deepseek-chat"
        )

# 示例使用（从环境变量读取API密钥）
if __name__ == "__main__":
    # 从环境变量读取API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
    
    generator = LLMTestCaseGenerator(
        api_url="https://api.deepseek.com/v1/chat/completions",
        api_key=api_key,
        model="deepseek-chat"
    )
    test_case = generator.generate_test_case("生成一个B站视频搜索的Playwright测试用例")
    print(f"生成的测试用例：{test_case}")