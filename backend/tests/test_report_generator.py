import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock
from core.report_generator import ReportGenerator


class TestReportGenerator:
    def setup_method(self):
        self.mock_db = MagicMock()
        self.generator = ReportGenerator(self.mock_db)
    
    def test_generate_report_creates_report_record(self):
        execution_result = {
            "success": True,
            "task_id": 1,
            "total_steps": 5,
            "passed_steps": 4,
            "failed_steps": 1,
            "skipped_steps": 0,
            "duration": 120,
            "steps": [
                {"name": "步骤1", "status": "passed", "duration": 2000, "error": None, "screenshot": "/screenshots/1.png"},
                {"name": "步骤2", "status": "passed", "duration": 3000, "error": None, "screenshot": "/screenshots/2.png"},
                {"name": "步骤3", "status": "failed", "duration": 1000, "error": "Element not found", "screenshot": "/screenshots/3.png"},
                {"name": "步骤4", "status": "passed", "duration": 2500, "error": None, "screenshot": "/screenshots/4.png"},
                {"name": "步骤5", "status": "passed", "duration": 1500, "error": None, "screenshot": "/screenshots/5.png"},
            ]
        }
        
        report = self.generator.generate_report(1, execution_result)
        
        assert report.total_count == 5
        assert report.pass_count == 4
        assert report.fail_count == 1
        assert report.skip_count == 0
        assert report.duration == 120
        assert report.status == "completed"
    
    def test_generate_report_partial_status(self):
        execution_result = {
            "success": False,
            "task_id": 1,
            "total_steps": 3,
            "passed_steps": 1,
            "failed_steps": 2,
            "skipped_steps": 0,
            "duration": 60,
            "steps": [
                {"name": "步骤1", "status": "passed", "duration": 1000, "error": None, "screenshot": None},
                {"name": "步骤2", "status": "failed", "duration": 500, "error": "Timeout", "screenshot": None},
                {"name": "步骤3", "status": "failed", "duration": 0, "error": "Skipped due to previous failure", "screenshot": None},
            ]
        }
        
        report = self.generator.generate_report(1, execution_result)
        
        assert report.status == "partial"
    
    def test_generate_summary(self):
        execution_result = {
            "success": True,
            "total_steps": 4,
            "passed_steps": 3,
            "failed_steps": 1,
            "skipped_steps": 0,
            "duration": 100,
            "steps": []
        }
        
        summary = self.generator._generate_summary(execution_result)
        
        assert summary["pass_rate"] == 75.0
        assert summary["total_duration"] == 100
    
    def test_generate_report_with_steps(self):
        execution_result = {
            "success": True,
            "task_id": 1,
            "total_steps": 2,
            "passed_steps": 2,
            "failed_steps": 0,
            "skipped_steps": 0,
            "duration": 30,
            "steps": [
                {"name": "打开页面", "status": "passed", "duration": 2000, "error": None, "screenshot": "/screenshots/1.png"},
                {"name": "点击按钮", "status": "passed", "duration": 1000, "error": None, "screenshot": "/screenshots/2.png"},
            ]
        }
        
        report = self.generator.generate_report(1, execution_result)
        
        assert self.mock_db.add.call_count >= 3
        assert self.mock_db.commit.called
