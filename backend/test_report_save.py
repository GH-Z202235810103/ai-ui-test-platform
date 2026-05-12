"""测试报告保存功能 - 详细版本"""
import sys
from pathlib import Path

# 设置标准输出和标准错误为 UTF-8 编码，解决 Windows 系统上的编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("开始测试报告保存功能")
print("=" * 60)

try:
    print("\n1. 导入模块...")
    from database import init_database, db_manager, TestCase, TestReport
    from core.executor_optimized import OptimizedTestExecutor
    print("   ✓ 模块导入成功")
    
    print("\n2. 初始化数据库...")
    init_database()
    print("   ✓ 数据库初始化成功")
    
    print("\n3. 创建数据库会话...")
    db = db_manager.get_session()
    print("   ✓ 数据库会话创建成功")
    
    print("\n4. 查询测试用例...")
    testcase = db.query(TestCase).first()
    
    if not testcase:
        print("   ✗ 数据库中没有测试用例")
        sys.exit(1)
    
    print(f"   ✓ 找到测试用例: {testcase.name} (ID: {testcase.id})")
    
    print("\n5. 准备测试用例数据...")
    testcase_dict = {
        "id": testcase.id,
        "name": testcase.name,
        "description": testcase.description,
        "steps": testcase.get_steps() if hasattr(testcase, 'get_steps') else [],
        "url": testcase.script_data.get("url") if hasattr(testcase, 'script_data') and testcase.script_data and testcase.script_data.get("url") else None
    }
    
    print(f"   ✓ 测试步骤数: {len(testcase_dict['steps'])}")
    print(f"   ✓ 测试URL: {testcase_dict['url']}")
    
    print("\n6. 创建执行器...")
    executor = OptimizedTestExecutor(
        headless=True,
        log_level='normal',
        timeout=30,
        retry_count=3
    )
    print("   ✓ 执行器创建成功")
    
    print("\n7. 执行测试用例...")
    print("=" * 60)
    
    result = executor.execute_testcase(
        testcase=testcase_dict,
        save_to_db=True
    )
    
    print("=" * 60)
    print("\n8. 执行结果:")
    print(f"   状态: {result.status}")
    print(f"   时长: {result.duration}")
    print(f"   报告ID: {result.report_id}")
    
    if result.error:
        print(f"   错误: {result.error}")
    
    print("\n9. 检查数据库中的报告...")
    reports = db.query(TestReport).all()
    print(f"   ✓ 测试报告总数: {len(reports)}")
    
    if reports:
        print("\n   最近的测试报告:")
        for r in reports[-5:]:
            print(f"     ID: {r.id}, 状态: {r.status}, 时间: {r.generated_at}, 步骤数: {r.total_count}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 发生错误: {e}")
    import traceback
    print(f"\n错误堆栈:\n{traceback.format_exc()}")
    sys.exit(1)
