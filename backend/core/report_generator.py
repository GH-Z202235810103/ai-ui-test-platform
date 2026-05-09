from datetime import datetime
from typing import Dict
from database import TestReport, ReportStep


class ReportGenerator:
    def __init__(self, db):
        self.db = db
    
    def generate_report(self, task_id: int, execution_result: Dict) -> TestReport:
        report = TestReport(
            task_id=task_id,
            total_count=execution_result.get('total_steps', 0),
            pass_count=execution_result.get('passed_steps', 0),
            fail_count=execution_result.get('failed_steps', 0),
            skip_count=execution_result.get('skipped_steps', 0),
            duration=execution_result.get('duration', 0),
            status="completed" if execution_result.get('success') else "partial",
            summary=self._generate_summary(execution_result),
            generated_at=datetime.utcnow()
        )
        self.db.add(report)
        self.db.flush()
        
        for idx, step_result in enumerate(execution_result.get('steps', []), 1):
            step = ReportStep(
                report_id=report.id,
                step_index=idx,
                step_name=step_result.get('name', f'步骤{idx}'),
                step_desc=step_result.get('description', ''),
                status=step_result.get('status', 'skipped'),
                duration=step_result.get('duration', 0),
                error_message=step_result.get('error'),
                expected_screenshot=step_result.get('expected_screenshot'),
                actual_screenshot=step_result.get('screenshot') or step_result.get('actual_screenshot')
            )
            self.db.add(step)
        
        self.db.commit()
        return report
    
    def _generate_summary(self, execution_result: Dict) -> Dict:
        total = execution_result.get('total_steps', 0)
        passed = execution_result.get('passed_steps', 0)
        pass_rate = round(passed / total * 100, 2) if total > 0 else 0.0
        
        errors = []
        for step in execution_result.get('steps', []):
            if step.get('error'):
                errors.append({
                    "step": step.get('name', ''),
                    "error": step.get('error')
                })
        
        return {
            "pass_rate": pass_rate,
            "total_duration": execution_result.get('duration', 0),
            "error_summary": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
