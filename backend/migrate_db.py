import sys
sys.path.insert(0, '.')

from database import get_db, TestReport, ReportStep, Base
from sqlalchemy import inspect, text

db = next(get_db())
engine = db.get_bind()

try:
    inspector = inspect(engine)
    
    reports_columns = inspector.get_columns('test_reports')
    report_column_names = [col['name'] for col in reports_columns]
    
    print(f"当前 test_reports 列: {report_column_names}")
    
    columns_to_add = [
        ('total_count', 'INTEGER DEFAULT 0'),
        ('pass_count', 'INTEGER DEFAULT 0'),
        ('fail_count', 'INTEGER DEFAULT 0'),
        ('skip_count', 'INTEGER DEFAULT 0'),
        ('status', 'VARCHAR(20) DEFAULT "completed"')
    ]
    
    with engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            if col_name not in report_column_names:
                print(f"添加列: {col_name}")
                conn.execute(text(f"ALTER TABLE test_reports ADD COLUMN {col_name} {col_type}"))
        
        tables = inspector.get_table_names()
        if 'report_steps' not in tables:
            print("创建 report_steps 表")
            Base.metadata.tables['report_steps'].create(engine)
        
        conn.commit()
    
    print("数据库迁移完成")
    
except Exception as e:
    print(f"迁移失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
