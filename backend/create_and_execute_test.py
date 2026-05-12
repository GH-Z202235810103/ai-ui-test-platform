"""创建并执行测试用例"""
import sys
from pathlib import Path

# 设置标准输出和标准错误为 UTF-8 编码，解决 Windows 系统上的编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from database import init_database, db_manager, TestCase
from core.executor_optimized import execute_testcase_sync

# 初始化数据库
init_database()

# 创建会话
db = db_manager.get_session()

try:
    # 创建一个简单的测试用例
    testcase = TestCase(
        name="百度搜索测试",
        description="测试百度搜索功能",
        script_data={
            "steps": [
                {"description": "打开百度首页"},
                {"description": "输入关键词'Python'"},
                {"description": "点击搜索按钮"}
            ],
            "url": "https://www.baidu.com"
        },
        type="ui",
        status="draft"
    )
    
    db.add(testcase)
    db.commit()
    db.refresh(testcase)
    
    print(f'✓ 创建测试用例成功，ID: {testcase.id}')
    
    # 执行测试用例
    testcase_dict = {
        "id": testcase.id,
        "name": testcase.name,
        "description": testcase.description,
        "steps": testcase.get_steps(),
        "url": testcase.script_data.get("url")
    }
    
    print(f'\n开始执行测试用例: {testcase.name}')
    print('=' * 50)
    
    result = execute_testcase_sync(
        testcase=testcase_dict,
        headless=True,
        save_to_db=True,
        log_level='normal',
        timeout=30,
        retry_count=3
    )
    
    print('\n' + '=' * 50)
    print(f'执行状态: {result["status"]}')
    print(f'执行时长: {result["duration"]}')
    print(f'报告ID: {result.get("report_id")}')
    
    if result["error"]:
        print(f'错误信息: {result["error"]}')
    
    # 检查数据库中的报告
    from database import TestReport
    reports = db.query(TestReport).all()
    print(f'\n数据库中的测试报告总数: {len(reports)}')
    
    if reports:
        print('\n最近的测试报告:')
        for r in reports[:5]:
            print(f'  ID: {r.id}, 状态: {r.status}, 时间: {r.generated_at}, 步骤数: {r.total_count}')
    
finally:
    db.close()
