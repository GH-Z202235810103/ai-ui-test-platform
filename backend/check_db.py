"""检查数据库状态"""
import sys
from pathlib import Path

# 设置标准输出和标准错误为 UTF-8 编码，解决 Windows 系统上的编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from database import init_database, db_manager, TestReport, TestCase

# 初始化数据库
init_database()

# 创建会话
db = db_manager.get_session()

try:
    # 查询测试用例
    testcases = db.query(TestCase).all()
    print(f'测试用例总数: {len(testcases)}')
    
    if testcases:
        print('\n测试用例列表:')
        for tc in testcases[:10]:
            print(f'  ID: {tc.id}, 名称: {tc.name}, 状态: {tc.status}')
    
    # 查询测试报告
    reports = db.query(TestReport).all()
    print(f'\n测试报告总数: {len(reports)}')
    
    if reports:
        print('\n最近的测试报告:')
        for r in reports[:5]:
            print(f'  ID: {r.id}, 状态: {r.status}, 时间: {r.generated_at}, 步骤数: {r.total_count}')
        
finally:
    db.close()
