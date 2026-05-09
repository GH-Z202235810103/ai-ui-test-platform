import pytest
import sys
sys.path.insert(0, 'backend')
from unittest.mock import MagicMock, patch
from core.report_export import ReportExportService


class TestReportExportService:
    def setup_method(self):
        self.service = ReportExportService()
    
    def test_export_html_returns_string(self):
        mock_db = MagicMock()
        mock_report = MagicMock()
        mock_report.id = 1
        mock_report.task_id = 1
        mock_report.total_count = 5
        mock_report.pass_count = 4
        mock_report.fail_count = 1
        mock_report.skip_count = 0
        mock_report.duration = 120
        mock_report.status = "completed"
        mock_report.summary = {"pass_rate": 80.0}
        mock_report.generated_at = "2026-05-03"
        mock_report.steps = []
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_report
        
        result = self.service.export_html(1, mock_db)
        
        assert isinstance(result, str)
        assert "测试报告" in result
    
    def test_export_pdf_calls_pdfkit(self):
        mock_db = MagicMock()
        mock_report = MagicMock()
        mock_report.id = 1
        mock_report.task_id = 1
        mock_report.total_count = 2
        mock_report.pass_count = 2
        mock_report.fail_count = 0
        mock_report.skip_count = 0
        mock_report.duration = 30
        mock_report.status = "completed"
        mock_report.summary = {"pass_rate": 100.0}
        mock_report.generated_at = "2026-05-03"
        mock_report.steps = []
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_report
        
        with patch('pdfkit.from_string') as mock_from_string:
            mock_from_string.return_value = b"fake-pdf-content"
            result = self.service.export_pdf(1, mock_db)
            
            assert result == b"fake-pdf-content"
            mock_from_string.assert_called_once()
