from pathlib import Path
from typing import Optional
from jinja2 import Template
from database import TestReport, ReportStep


TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "reports"

PDF_OPTIONS = {
    'encoding': 'UTF-8',
    'page-size': 'A4',
    'orientation': 'Portrait',
    'margin-top': '15mm',
    'margin-right': '15mm',
    'margin-bottom': '15mm',
    'margin-left': '15mm',
    'enable-local-file-access': None,
    'no-stop-slow-scripts': None,
}


class ReportExportService:
    def __init__(self, template_dir: Optional[str] = None):
        if template_dir:
            self.template_dir = Path(template_dir)
        else:
            self.template_dir = TEMPLATE_DIR
    
    def export_html(self, report_id: int, db) -> str:
        report_data = self._get_report_data(report_id, db)
        template = self._load_template("report_template.html")
        return template.render(report=report_data)
    
    def export_pdf(self, report_id: int, db) -> bytes:
        import pdfkit
        html_content = self.export_html(report_id, db)
        return pdfkit.from_string(html_content, False, options=PDF_OPTIONS)
    
    def _get_report_data(self, report_id: int, db) -> dict:
        report = db.query(TestReport).filter(TestReport.id == report_id).first()
        if not report:
            raise ValueError(f"报告不存在: {report_id}")
        
        steps = db.query(ReportStep).filter(ReportStep.report_id == report_id).order_by(ReportStep.step_index).all()
        
        total = report.total_count or 0
        pass_rate = round(report.pass_count / total * 100, 1) if total > 0 else 0.0
        
        task_name = ""
        if report.task_id:
            from database import TestTask
            task = db.query(TestTask).filter(TestTask.id == report.task_id).first()
            if task:
                task_name = task.name
        
        return {
            "id": report.id,
            "task_name": task_name,
            "total_count": report.total_count or 0,
            "pass_count": report.pass_count or 0,
            "fail_count": report.fail_count or 0,
            "skip_count": report.skip_count or 0,
            "pass_rate": pass_rate,
            "duration": report.duration or 0,
            "status": report.status or "completed",
            "generated_at": str(report.generated_at) if report.generated_at else "",
            "steps": [
                {
                    "step_index": s.step_index,
                    "step_name": s.step_name or "",
                    "step_desc": s.step_desc or "",
                    "status": s.status or "skipped",
                    "duration": s.duration or 0,
                    "error_message": s.error_message or "",
                    "expected_screenshot": s.expected_screenshot or "",
                    "actual_screenshot": s.actual_screenshot or "",
                }
                for s in steps
            ]
        }
    
    def _load_template(self, name: str) -> Template:
        template_path = self.template_dir / name
        if not template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as f:
            return Template(f.read())
