# -*- coding: utf-8 -*-
"""
测试报告和趋势分析功能验证脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager, TestReport, ReportStep, TestCase
from datetime import datetime, timedelta
import json

# 初始化数据库管理器
db_manager = DatabaseManager()
db_manager.init_database()

def test_database_reports():
    """测试数据库中的报告记录"""
    print("\n" + "="*60)
    print("[TEST] Database Reports")
    print("="*60)
    
    db = db_manager.get_session()
    try:
        # 查询所有报告
        reports = db.query(TestReport).order_by(TestReport.generated_at.desc()).all()
        
        print(f"\n[OK] Found {len(reports)} test reports")
        
        if len(reports) == 0:
            print("\n[WARN] No test reports in database")
            print("[TIP] Please execute test cases to generate reports")
            return False
        
        # 显示最近的报告
        print("\n[LIST] Recent 5 reports:")
        for i, report in enumerate(reports[:5], 1):
            total = report.total_count or 0
            passed = report.pass_count or 0
            failed = report.fail_count or 0
            pass_rate = round(passed / total * 100, 2) if total > 0 else 0
            
            print(f"\n{i}. Report ID: {report.id}")
            print(f"   Status: {report.status}")
            print(f"   Total: {total}, Passed: {passed}, Failed: {failed}")
            print(f"   Pass Rate: {pass_rate}%")
            print(f"   Generated: {report.generated_at}")
            
            # 查询步骤详情
            steps = db.query(ReportStep).filter(ReportStep.report_id == report.id).all()
            print(f"   Steps: {len(steps)}")
            
            if report.summary:
                summary = report.summary if isinstance(report.summary, dict) else json.loads(report.summary) if report.summary else {}
                print(f"   Test Case: {summary.get('testcase_name', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_trends_api():
    """测试趋势分析API"""
    print("\n" + "="*60)
    print("[TEST] Trends API")
    print("="*60)
    
    db = db_manager.get_session()
    try:
        # 模拟API调用
        days = 30
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(TestReport).filter(TestReport.generated_at >= start_date)
        reports = query.order_by(TestReport.generated_at).all()
        
        trends = []
        for report in reports:
            total = report.total_count or 0
            pass_rate = round(report.pass_count / total * 100, 2) if total > 0 else 0.0
            trends.append({
                "date": report.generated_at.strftime("%Y-%m-%d") if report.generated_at else "",
                "total": total,
                "passed": report.pass_count or 0,
                "failed": report.fail_count or 0,
                "pass_rate": pass_rate,
                "avg_duration": report.duration or 0
            })
        
        total_reports = len(reports)
        avg_pass_rate = round(sum(t["pass_rate"] for t in trends) / total_reports, 2) if total_reports > 0 else 0.0
        total_tests = sum(t["total"] for t in trends)
        
        print(f"\n[OK] Trends statistics:")
        print(f"   Time range: Last {days} days")
        print(f"   Total reports: {total_reports}")
        print(f"   Avg pass rate: {avg_pass_rate}%")
        print(f"   Total tests: {total_tests}")
        
        if len(trends) > 0:
            print(f"\n[CHART] Trends data (last 5):")
            for trend in trends[-5:]:
                print(f"   {trend['date']}: Pass rate {trend['pass_rate']}%, Total steps {trend['total']}")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_report_detail():
    """测试报告详情"""
    print("\n" + "="*60)
    print("[TEST] Report Detail")
    print("="*60)
    
    db = db_manager.get_session()
    try:
        # 获取最新的报告
        report = db.query(TestReport).order_by(TestReport.generated_at.desc()).first()
        
        if not report:
            print("\n[WARN] No test report found")
            return False
        
        print(f"\n[OK] Report detail:")
        print(f"   ID: {report.id}")
        print(f"   Status: {report.status}")
        print(f"   Total steps: {report.total_count}")
        print(f"   Passed: {report.pass_count}")
        print(f"   Failed: {report.fail_count}")
        print(f"   Skipped: {report.skip_count}")
        print(f"   Duration: {report.duration}s")
        print(f"   Generated: {report.generated_at}")
        
        # 查询步骤详情
        steps = db.query(ReportStep).filter(ReportStep.report_id == report.id).order_by(ReportStep.step_index).all()
        
        print(f"\n[NOTE] Steps detail ({len(steps)} steps):")
        for step in steps[:5]:  # 只显示前5个步骤
            print(f"   {step.step_index}. {step.step_name}")
            print(f"      Status: {step.status}")
            if step.error_message:
                print(f"      Error: {step.error_message[:50]}...")
            if step.actual_screenshot:
                print(f"      Screenshot: {step.actual_screenshot}")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_export_functionality():
    """测试导出功能"""
    print("\n" + "="*60)
    print("[TEST] Export Functionality")
    print("="*60)
    
    try:
        from core.report_export import ReportExportService
        
        db = db_manager.get_session()
        try:
            # 获取最新的报告
            report = db.query(TestReport).order_by(TestReport.generated_at.desc()).first()
            
            if not report:
                print("\n[WARN] No test report found")
                return False
            
            export_service = ReportExportService()
            
            # 测试HTML导出
            print("\n[OK] Testing HTML export...")
            html_content = export_service.export_html(report.id, db)
            print(f"   HTML content length: {len(html_content)} chars")
            print(f"   [OK] HTML export successful")
            
            # 测试PDF导出
            print("\n[OK] Testing PDF export...")
            try:
                pdf_bytes = export_service.export_pdf(report.id, db)
                print(f"   PDF file size: {len(pdf_bytes)} bytes")
                print(f"   [OK] PDF export successful")
            except Exception as e:
                print(f"   [WARN] PDF export failed (may need wkhtmltopdf): {e}")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("[START] Testing Report and Trends Functionality")
    print("="*60)
    
    results = {
        "Database Reports": test_database_reports(),
        "Trends API": test_trends_api(),
        "Report Detail": test_report_detail(),
        "Export Functionality": test_export_functionality()
    }
    
    print("\n" + "="*60)
    print("[SUMMARY] Test Results")
    print("="*60)
    
    for name, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("[OK] All tests passed!")
    else:
        print("[WARN] Some tests failed, please check the error messages above")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
