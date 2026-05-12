"""
测试执行结果保存到数据库的验证脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, TestReport, ReportStep, TestCase
from core.executor_optimized import execute_testcase_sync
from datetime import datetime

def test_database_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    db = None
    try:
        db = db_manager.get_session()
        print("[OK] 数据库连接成功")
        
        report_count = db.query(TestReport).count()
        print(f"[OK] 当前报告总数: {report_count}")
        
        step_count = db.query(ReportStep).count()
        print(f"[OK] 当前步骤总数: {step_count}")
        
        return True
    except Exception as e:
        print(f"[ERROR] 数据库连接失败: {e}")
        return False
    finally:
        if db:
            db.close()

def test_execute_and_save():
    """测试执行用例并保存到数据库"""
    print("\n=== 测试执行用例并保存到数据库 ===")
    db = None
    try:
        db = db_manager.get_session()
        
        testcases = db.query(TestCase).all()
        if not testcases:
            print("[ERROR] 没有找到测试用例")
            return False
        
        testcase = testcases[0]
        print(f"[OK] 找到测试用例: {testcase.name} (ID: {testcase.id})")
        
        testcase_dict = {
            "id": testcase.id,
            "name": testcase.name,
            "description": testcase.description,
            "steps": testcase.get_steps() if hasattr(testcase, 'get_steps') else [],
            "url": testcase.script_data.get("url") if hasattr(testcase, 'script_data') and testcase.script_data and testcase.script_data.get("url") else None
        }
        
        print(f"[OK] 测试用例步骤数: {len(testcase_dict['steps'])}")
        print(f"[OK] 测试用例URL: {testcase_dict['url']}")
        
        print("\n开始执行测试用例...")
        result = execute_testcase_sync(
            testcase=testcase_dict,
            headless=True,
            save_to_db=True,
            log_level='normal',
            timeout=30,
            retry_count=3,
            screenshot_quality=80
        )
        
        print(f"\n[OK] 执行完成")
        print(f"  - 执行ID: {result.get('execution_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 步骤数: {len(result.get('steps', []))}")
        print(f"  - 报告ID: {result.get('report_id')}")
        
        if result.get('report_id'):
            print(f"\n=== 验证数据库中的报告记录 ===")
            report = db.query(TestReport).filter(TestReport.id == result.get('report_id')).first()
            if report:
                print(f"[OK] 找到报告记录: ID={report.id}")
                print(f"  - 测试用例ID: {report.summary.get('testcase_id') if report.summary else 'N/A'}")
                print(f"  - 测试用例名称: {report.summary.get('testcase_name') if report.summary else 'N/A'}")
                print(f"  - 总步骤数: {report.total_count}")
                print(f"  - 成功数: {report.pass_count}")
                print(f"  - 失败数: {report.fail_count}")
                print(f"  - 状态: {report.status}")
                print(f"  - 持续时间: {report.duration}秒")
                print(f"  - 生成时间: {report.generated_at}")
                
                steps = db.query(ReportStep).filter(ReportStep.report_id == report.id).all()
                print(f"\n[OK] 报告步骤数: {len(steps)}")
                for step in steps:
                    print(f"  - 步骤{step.step_index}: {step.step_name[:50]}... [{step.status}]")
                
                return True
            else:
                print(f"[ERROR] 未找到报告记录，ID: {result.get('report_id')}")
                return False
        else:
            print("[ERROR] 执行结果中没有报告ID")
            return False
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if db:
            db.close()

def check_recent_reports():
    """检查最近的报告记录"""
    print("\n=== 检查最近的报告记录 ===")
    db = None
    try:
        db = db_manager.get_session()
        
        reports = db.query(TestReport).order_by(TestReport.generated_at.desc()).limit(5).all()
        
        if not reports:
            print("[ERROR] 没有找到任何报告记录")
            return False
        
        print(f"[OK] 找到 {len(reports)} 个最近的报告:")
        for i, report in enumerate(reports, 1):
            print(f"\n{i}. 报告ID: {report.id}")
            print(f"   - 生成时间: {report.generated_at}")
            print(f"   - 状态: {report.status}")
            print(f"   - 总步骤: {report.total_count}, 成功: {report.pass_count}, 失败: {report.fail_count}")
            if report.summary:
                print(f"   - 测试用例: {report.summary.get('testcase_name', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"[ERROR] 查询失败: {e}")
        return False
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("执行结果保存到数据库验证测试")
    print("=" * 60)
    
    success = True
    
    if not test_database_connection():
        success = False
        print("\n✗ 数据库连接测试失败，停止后续测试")
        sys.exit(1)
    
    if not test_execute_and_save():
        success = False
    
    if not check_recent_reports():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] 所有测试通过！执行结果保存功能正常")
    else:
        print("[ERROR] 部分测试失败，请检查日志")
    print("=" * 60)
