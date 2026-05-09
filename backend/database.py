"""
数据库模型
"""
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum, BLOB, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
import json

Base = declarative_base()

class ProjectStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class CaseStatus(enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"

class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"

class TaskType(enum.Enum):
    MANUAL = "manual"
    SCHEDULE = "schedule"
    TRIGGER = "trigger"

class Project(Base):
    """项目表"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    base_url = Column(String(500))
    config = Column(JSON)
    status = Column(String(20), default="active")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
    test_tasks = relationship("TestTask", back_populates="project", cascade="all, delete-orphan")

class TestCase(Base):
    """测试用例表"""
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    script_data = Column(JSON, nullable=False)
    type = Column(String(50))
    project_id = Column(Integer, ForeignKey("projects.id"))
    visual_elements = Column(JSON)
    ai_metadata = Column(JSON)
    version = Column(Integer, default=1)
    status = Column(String(20), default="draft")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="test_cases")
    
    def get_steps(self):
        if self.script_data and isinstance(self.script_data, dict):
            return self.script_data.get("steps", [])
        return []

class TestTask(Base):
    """测试任务表"""
    __tablename__ = "test_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(20), default="manual")
    config = Column(JSON)
    execution_status = Column(String(20), default="pending")
    project_id = Column(Integer, ForeignKey("projects.id"))
    case_ids = Column(JSON)
    progress = Column(Integer, default=0)
    started_at = Column(TIMESTAMP, nullable=True)
    finished_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="test_tasks")
    test_reports = relationship("TestReport", back_populates="task", cascade="all, delete-orphan")

class TestReport(Base):
    """测试报告表"""
    __tablename__ = "test_reports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id"))
    
    total_count = Column(Integer, default=0)
    pass_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    skip_count = Column(Integer, default=0)
    
    summary = Column(JSON)
    details = Column(Text)
    duration = Column(Integer)
    screenshot_refs = Column(JSON)
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(String(20), default="completed")
    
    task = relationship("TestTask", back_populates="test_reports")
    steps = relationship("ReportStep", back_populates="report", cascade="all, delete-orphan")

class ReportStep(Base):
    """报告步骤表"""
    __tablename__ = "report_steps"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"))
    
    step_index = Column(Integer)
    step_name = Column(String(255))
    step_desc = Column(Text)
    status = Column(String(20))
    duration = Column(Integer)
    error_message = Column(Text)
    expected_screenshot = Column(String(500))
    actual_screenshot = Column(String(500))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    report = relationship("TestReport", back_populates="steps")

class VisualElement(Base):
    """视觉元素特征表"""
    __tablename__ = "visual_elements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    element_type = Column(String(100))
    screenshot_path = Column(String(500))
    feature_data = Column(BLOB)
    usage_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    match_threshold = Column(Float, default=0.9)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_used_at = Column(TIMESTAMP, nullable=True)

class Recording(Base):
    """录制用例表"""
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(500))
    actions = Column(JSON)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

engine = None
SessionLocal = None

class DatabaseManager:
    """数据库管理器"""
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
    
    def init_database(self, database_url: str = None):
        """初始化数据库"""
        if database_url is None:
            from config import DATABASE_URL
            database_url = DATABASE_URL
        
        # 配置连接池参数
        pool_size = 10  # 连接池大小
        max_overflow = 20  # 最大溢出连接数
        pool_timeout = 30  # 连接池超时时间（秒）
        pool_recycle = 3600  # 连接回收时间（秒）
        
        self.engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_use_lifo=True  # 使用后进先出策略
        )
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        return self.engine
    
    def get_session(self):
        """获取数据库会话"""
        if self.SessionLocal is None:
            self.init_database()
        return self.SessionLocal()
    
    def get_db(self):
        """FastAPI依赖项：获取数据库会话"""
        db = self.get_session()
        try:
            yield db
        finally:
            try:
                db.close()
            except Exception:
                # 忽略关闭时的错误
                pass

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

# 保持向后兼容的函数
def init_database(database_url: str = None):
    """初始化数据库（向后兼容）"""
    return db_manager.init_database(database_url)

def get_session():
    """获取数据库会话（向后兼容）"""
    return db_manager.get_session()

def get_db():
    """FastAPI依赖项：获取数据库会话（向后兼容）"""
    yield from db_manager.get_db()
