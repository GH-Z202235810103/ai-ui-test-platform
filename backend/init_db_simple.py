"""
初始化数据库并创建测试数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, Base, TestCase
from config import DATABASE_URL
from sqlalchemy import create_engine

def init_db():
    """初始化数据库"""
    print("=== 初始化数据库 ===")
    print(f"数据库URL: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    print("[OK] 数据表创建成功")
    
    db_manager.init_database(DATABASE_URL)
    print("[OK] 数据库管理器初始化成功")

def create_test_data():
    """创建测试数据"""
    print("\n=== 创建测试数据 ===")
    db = None
    try:
        db = db_manager.get_session()
        
        testcases = db.query(TestCase).all()
        if testcases:
            print(f"[OK] 已存在 {len(testcases)} 个测试用例")
            return
        
        testcase = TestCase(
            name="测试用例1",
            description="这是一个测试用例",
            script_data={
                "url": "https://www.baidu.com",
                "steps": [
                    "打开百度首页",
                    "在搜索框输入'测试'",
                    "点击搜索按钮"
                ]
            }
        )
        db.add(testcase)
        db.commit()
        print(f"[OK] 创建测试用例成功，ID: {testcase.id}")
        
    except Exception as e:
        print(f"[ERROR] 创建测试数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    init_db()
    create_test_data()
    print("\n[OK] 数据库初始化完成！")
