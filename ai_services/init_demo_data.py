import json

def init_demo_data(file_path: str = "test_cases.json"):
    """初始化测试用例数据（匹配演示用例）"""
    test_cases = [
        {
            "case_id": "TC001",
            "case_name": "百度搜索演示",
            "description": "使用Playwright完成百度关键词搜索",
            "steps": ["打开百度首页", "输入Playwright教程", "点击搜索", "验证结果加载"],
            "expected_result": "搜索结果页面正常显示"
        },
        {
            "case_id": "TC002",
            "case_name": "淘宝演示",
            "description": "使用Playwright完成淘宝商品搜索",
            "steps": ["打开淘宝首页", "输入笔记本电脑", "按回车搜索", "验证商品列表加载"],
            "expected_result": "商品列表页面正常显示"
        },
        {
            "case_id": "TC003",
            "case_name": "B站视频搜索演示",
            "description": "使用Playwright完成B站视频搜索",
            "steps": ["打开B站首页", "输入Playwright自动化测试", "点击搜索", "验证视频列表加载"],
            "expected_result": "视频列表页面正常显示"
        },
        {
            "case_id": "TC004",
            "case_name": "京东商品搜索演示",
            "description": "使用Playwright完成京东商品搜索",
            "steps": ["打开京东首页", "输入手机", "点击搜索", "验证商品列表加载"],
            "expected_result": "商品列表页面正常显示"
        }
    ]
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, ensure_ascii=False, indent=4)
        print(f"✅ 测试用例数据已初始化至: {file_path}")
    except Exception as e:
        print(f"❌ 初始化测试数据失败: {str(e)}")

if __name__ == "__main__":
    init_demo_data()