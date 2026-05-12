#!/usr/bin/env python
"""
测试后端执行功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, TestCase
import json
import time
from core.executor_optimized import execute_testcase_sync

def test_execution():
    print("=" * 60)
    print("开始测试后端执行功能")
    print("=" * 60)

    # 初始化数据库
    db_manager.init_database()
    session = db_manager.get_session()

    try:
        # 获取第一个测试用例
        testcase = session.query(TestCase).first()
        if not testcase:
            print("❌ 没有找到测试用例")
            return False

        print(f"[INFO] 测试用例 ID: {testcase.id}")
        print(f"[INFO] 测试用例名称: {testcase.name}")
        print(f"[INFO] 测试用例类型: {testcase.type}")
        print(f"[INFO] 测试步骤: {json.dumps(testcase.script_data, ensure_ascii=False, indent=2)}")

        # 执行测试用例
        print("\n[INFO] 开始执行测试用例...")
        start_time = time.time()

        result = execute_testcase_sync(
            testcase=testcase.to_dict() if hasattr(testcase, 'to_dict') else {
                "id": testcase.id,
                "name": testcase.name,
                "description": testcase.description,
                "steps": testcase.script_data.get("steps", []),
                "url": testcase.script_data.get("url", ""),
                "type": testcase.type
            },
            headless=False,  # 显示浏览器窗口
            save_to_db=True,
            timeout=30,
            retry_count=2
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n[SUCCESS] 执行完成!")
        print(f"[INFO] 执行耗时: {duration:.2f}秒")
        print(f"[INFO] 执行状态: {result.get('status', 'unknown')}")
        print(f"[INFO] 执行日志: {len(result.get('execution_log', []))} 条")

        # 显示执行日志
        print("\n[INFO] 执行日志:")
        for i, log in enumerate(result.get('execution_log', [])[:10]):  # 只显示前10条
            print(f"  {i+1}. {log}")

        # 检查是否有截图
        screenshots = result.get('screenshots', [])
        if screenshots:
            print(f"\n[INFO] 截图数量: {len(screenshots)}")
            for i, screenshot in enumerate(screenshots[:3]):  # 只显示前3张
                print(f"  {i+1}. {screenshot}")

        # 检查是否生成了报告
        if result.get('report_id'):
            print(f"\n[INFO] 生成了测试报告 ID: {result['report_id']}")

        return result.get('status') in ['success', 'passed']

    except Exception as e:
        print(f"\n[ERROR] 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()

if __name__ == "__main__":
    success = test_execution()
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] 测试执行成功!")
    else:
        print("[ERROR] 测试执行失败!")
    print("=" * 60)
    sys.exit(0 if success else 1)