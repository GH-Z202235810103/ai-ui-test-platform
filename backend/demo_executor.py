"""
执行引擎演示脚本

演示如何使用优化后的执行引擎执行测试用例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.executor_optimized import execute_testcase_sync, OptimizedTestExecutor


def demo_basic_usage():
    """演示基本用法"""
    print("=" * 60)
    print("演示 1: 基本用法 - 同步执行测试用例")
    print("=" * 60)
    
    testcase = {
        "id": 1,
        "name": "百度搜索测试",
        "description": "测试百度搜索功能",
        "url": "https://www.baidu.com",
        "steps": [
            "打开百度首页",
            "在搜索框中输入：测试关键词",
            "点击搜索按钮",
            "等待2秒"
        ]
    }
    
    print(f"\n测试用例: {testcase['name']}")
    print(f"步骤数量: {len(testcase['steps'])}")
    print("\n开始执行...")
    
    result = execute_testcase_sync(
        testcase=testcase,
        headless=True,
        save_to_db=False,
        log_level='normal'
    )
    
    print(f"\n执行结果:")
    print(f"  状态: {result['status']}")
    print(f"  持续时间: {result['duration']}")
    print(f"  步骤数: {len(result['steps'])}")
    print(f"  截图数: {len(result['screenshots'])}")
    
    if result['error']:
        print(f"  错误: {result['error']}")
    
    print(f"\n执行日志 (前5条):")
    for log in result['execution_log'][:5]:
        print(f"  {log}")


def demo_executor_class():
    """演示使用执行器类"""
    print("\n" + "=" * 60)
    print("演示 2: 使用执行器类")
    print("=" * 60)
    
    testcase = {
        "id": 2,
        "name": "多步骤测试",
        "url": "https://www.baidu.com",
        "steps": [
            "打开百度首页",
            "在搜索框中输入：Python自动化测试",
            "点击搜索按钮",
            "等待1秒",
            "验证页面包含：Python"
        ]
    }
    
    print(f"\n测试用例: {testcase['name']}")
    
    executor = OptimizedTestExecutor(headless=True, log_level='verbose')
    
    print("\n开始执行...")
    result = executor.execute_testcase(
        testcase=testcase,
        save_to_db=False
    )
    
    print(f"\n执行结果:")
    print(f"  执行ID: {result.execution_id}")
    print(f"  状态: {result.status}")
    print(f"  持续时间: {result.duration}")
    
    print(f"\n步骤执行详情:")
    for step in result.steps:
        status = "✓" if step.get('success') else "✗"
        print(f"  {status} 步骤 {step.get('step_index')}: {step.get('step_desc')}")
        if step.get('error'):
            print(f"      错误: {step.get('error')}")


def demo_error_handling():
    """演示错误处理"""
    print("\n" + "=" * 60)
    print("演示 3: 错误处理")
    print("=" * 60)
    
    testcase = {
        "id": 3,
        "name": "错误测试用例",
        "url": "https://www.baidu.com",
        "steps": [
            "打开百度首页",
            "执行不存在的操作",
            "验证页面包含：不存在的文本12345"
        ]
    }
    
    print(f"\n测试用例: {testcase['name']}")
    print("\n开始执行...")
    
    result = execute_testcase_sync(
        testcase=testcase,
        headless=True,
        save_to_db=False,
        log_level='normal'
    )
    
    print(f"\n执行结果:")
    print(f"  状态: {result['status']}")
    
    if result['error']:
        print(f"  错误信息: {result['error']}")
    
    print(f"\n步骤执行情况:")
    for step in result['steps']:
        status = "✓" if step.get('success') else "✗"
        print(f"  {status} 步骤 {step.get('step_index')}: {step.get('step_desc')}")


def demo_database_persistence():
    """演示数据库持久化"""
    print("\n" + "=" * 60)
    print("演示 4: 数据库持久化")
    print("=" * 60)
    
    testcase = {
        "id": 4,
        "name": "数据库持久化测试",
        "url": "https://www.baidu.com",
        "steps": [
            "打开百度首页",
            "等待1秒"
        ]
    }
    
    print(f"\n测试用例: {testcase['name']}")
    print("\n开始执行并保存到数据库...")
    
    result = execute_testcase_sync(
        testcase=testcase,
        headless=True,
        save_to_db=True,
        log_level='normal'
    )
    
    print(f"\n执行结果:")
    print(f"  状态: {result['status']}")
    print(f"  已保存到数据库: 是")
    
    print(f"\n提示: 可以通过以下SQL查询数据库中的执行记录:")
    print(f"  SELECT * FROM test_reports WHERE summary LIKE '%{testcase['name']}%';")
    print(f"  SELECT * FROM report_steps WHERE step_name LIKE '%{testcase['name']}%';")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("优化后的执行引擎演示")
    print("=" * 60)
    
    print("\n本演示将展示优化后的执行引擎的主要功能:")
    print("1. 基本用法 - 同步执行测试用例")
    print("2. 使用执行器类")
    print("3. 错误处理")
    print("4. 数据库持久化")
    
    print("\n注意: 本演示需要启动浏览器，可能需要较长时间。")
    print("如果不需要启动浏览器，可以跳过此演示。")
    
    try:
        input("\n按 Enter 键继续，或 Ctrl+C 退出...")
    except KeyboardInterrupt:
        print("\n\n演示已取消。")
        return
    
    try:
        demo_basic_usage()
        demo_executor_class()
        demo_error_handling()
        demo_database_persistence()
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        
        print("\n主要改进:")
        print("✓ 集成了 ExecutionLogger 进行结构化日志记录")
        print("✓ 集成了 RetryStrategy 进行智能重试")
        print("✓ 集成了 SmartWait 进行智能等待")
        print("✓ 集成了 StepParser 进行步骤解析")
        print("✓ 添加了数据库持久化功能")
        print("✓ 改进了错误处理和异常捕获")
        print("✓ 支持多浏览器（Edge、Chrome、Firefox）")
        print("✓ 提供了同步和异步执行接口")
        
        print("\n详细文档: backend/docs/executor_optimization_report.md")
        
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
