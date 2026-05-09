import pytest
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import TestReport, ReportStep, Base


@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


class TestReportModels:
    def test_create_report_with_counts(self, db_session):
        report = TestReport(
            task_id=1,
            total_count=5,
            pass_count=4,
            fail_count=1,
            skip_count=0,
            duration=120,
            status="completed",
            summary={"pass_rate": 80.0}
        )
        db_session.add(report)
        db_session.flush()
        
        assert report.id is not None
        assert report.total_count == 5
        assert report.pass_count == 4
        assert report.fail_count == 1
        assert report.skip_count == 0
        assert report.status == "completed"
    
    def test_create_report_step(self, db_session):
        report = TestReport(
            task_id=1,
            total_count=1,
            pass_count=1,
            fail_count=0,
            skip_count=0,
            status="completed"
        )
        db_session.add(report)
        db_session.flush()
        
        step = ReportStep(
            report_id=report.id,
            step_index=1,
            step_name="打开页面",
            step_desc="访问 https://example.com",
            status="passed",
            duration=2000,
            actual_screenshot="/screenshots/step_1.png"
        )
        db_session.add(step)
        db_session.flush()
        
        assert step.id is not None
        assert step.report_id == report.id
        assert step.status == "passed"
    
    def test_report_steps_relationship(self, db_session):
        report = TestReport(
            task_id=1,
            total_count=2,
            pass_count=2,
            fail_count=0,
            skip_count=0,
            status="completed"
        )
        db_session.add(report)
        db_session.flush()
        
        step1 = ReportStep(report_id=report.id, step_index=1, step_name="步骤1", status="passed")
        step2 = ReportStep(report_id=report.id, step_index=2, step_name="步骤2", status="passed")
        db_session.add_all([step1, step2])
        db_session.flush()
        
        db_session.expire_all()
        report = db_session.query(TestReport).filter(TestReport.id == report.id).first()
        assert len(report.steps) == 2
    
    def test_report_step_fail_with_error(self, db_session):
        report = TestReport(
            task_id=1,
            total_count=1,
            pass_count=0,
            fail_count=1,
            skip_count=0,
            status="partial"
        )
        db_session.add(report)
        db_session.flush()
        
        step = ReportStep(
            report_id=report.id,
            step_index=1,
            step_name="点击按钮",
            status="failed",
            error_message="Element not found: #submit-btn"
        )
        db_session.add(step)
        db_session.flush()
        
        assert step.status == "failed"
        assert step.error_message is not None
