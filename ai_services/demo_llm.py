"""
LLM测试用例生成演示 - DeepSeek API (安全版本)
AI与行为驱动的UI自动化测试平台 - 第三个技术支柱
作者：GH-Z202235810103
GitHub: https://github.com/GH-Z202235810103/ai-ui-test-platform
"""

import os
import requests
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

class DeepSeekTestGenerator:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("❌ 未找到DEEPSEEK_API_KEY环境变量")
        
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.results_dir = Path("llm_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # 创建带重试机制的session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        print("✅ API配置加载成功 (已启用重试机制)")
    
    def test_api_connection(self):
        """测试API连接"""
        print("🔗 测试DeepSeek API连接...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "请回复'连接成功'"}],
            "max_tokens": 10
        }
        
        try:
            response = self.session.post(self.base_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                print("✅ API连接测试成功！")
                return True
            else:
                print(f"❌ API连接失败: HTTP {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            print("❌ API连接超时，但网络是通的，继续尝试...")
            return True  # 超时但继续尝试
        except Exception as e:
            print(f"❌ API连接异常: {e}")
            return False
    
    def generate_test_case(self, test_description, max_tokens=800):  # 减少token数加快响应
        """生成测试用例 - 优化版本"""
        print(f"🧠 正在生成测试用例: {test_description}")
        
        system_prompt = """你是一个专业的UI自动化测试工程师。请根据用户描述生成详细的测试用例。

要求：
1. 生成结构化的测试用例
2. 测试步骤要具体可执行
3. 输出格式为纯JSON：
{
    "test_case_name": "名称",
    "test_objective": "目标", 
    "test_steps": ["步骤1", "步骤2"],
    "expected_results": ["结果1", "结果2"],
    "priority": "High/Medium/Low"
}

请用中文回复，输出纯JSON。"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_description}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            print("⏳ 调用DeepSeek API (最多等待60秒)...")
            start_time = time.time()
            
            # 使用带重试的session，延长超时时间
            response = self.session.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            ai_content = result["choices"][0]["message"]["content"]
            
            execution_time = time.time() - start_time
            print(f"✅ AI响应接收成功 (耗时: {execution_time:.2f}s)")
            
            return ai_content
            
        except requests.exceptions.Timeout:
            print("❌ API调用超时，请检查网络连接或稍后重试")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API调用失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 处理响应时出错: {e}")
            return None

    # 其余方法保持不变...
    def parse_test_case(self, ai_response):
        """解析测试用例"""
        try:
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].strip()
            else:
                json_str = ai_response.strip()
            
            return json.loads(json_str)
        except:
            try:
                return json.loads(ai_response)
            except:
                print("❌ 无法解析AI响应")
                return None

    def demo_llm_generation(self):
        """演示LLM测试用例生成 - 简化版本"""
        print("=" * 60)
        print("🧠 DeepSeek LLM测试用例生成演示")
        print("=" * 60)
        
        if not self.test_api_connection():
            print("❌ API连接失败，请检查网络和API密钥")
            return
        
        # 直接使用百度测试，跳过选择
        test_desc = "测试百度搜索功能，包括正常搜索和边界情况"
        print(f"📝 测试描述: {test_desc}")
        print("-" * 40)
        
        ai_response = self.generate_test_case(test_desc)
        if not ai_response:
            print("❌ 测试用例生成失败，但API连接正常")
            print("💡 建议：稍后重试或检查网络稳定性")
            return
        
        test_case = self.parse_test_case(ai_response)
        if test_case:
            print("\n✅ 测试用例生成成功！")
            print(f"📝 测试名称: {test_case.get('test_case_name', 'N/A')}")
            print(f"🎯 测试步骤: {len(test_case.get('test_steps', []))}个")
            
            # 保存结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(self.results_dir / f"test_case_{timestamp}.json", "w", encoding="utf-8") as f:
                json.dump(test_case, f, indent=2, ensure_ascii=False)
            
            print(f"📁 测试用例已保存: llm_results/test_case_{timestamp}.json")
            print("\n🎉 LLM集成成功！三大技术支柱完成！")
        else:
            print("❌ 测试用例解析失败")

def main():
    try:
        generator = DeepSeekTestGenerator()
        generator.demo_llm_generation()
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")

if __name__ == "__main__":
    main()