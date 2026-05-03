"""
数据迁移脚本 - 将JSON文件数据迁移到MySQL
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_database, get_session, Project, TestCase, TestTask, TestReport, VisualElement, Recording
from config import DATA_DIR

def migrate_test_cases():
    """迁移测试用例"""
    test_cases_file = DATA_DIR / "test_cases.json"
    if not test_cases_file.exists():
        print("⚠️ 测试用例文件不存在，跳过迁移")
        return 0
    
    with open(test_cases_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    db = get_session()
    count = 0
    
    for tc in data:
        existing = db.query(TestCase).filter(TestCase.name == tc.get('name')).first()
        if existing:
            print(f"  ⏭️ 测试用例已存在: {tc.get('name')}")
            continue
        
        test_case = TestCase(
            name=tc.get('name', '未命名用例'),
            description=tc.get('description', ''),
            script_data={
                'steps': tc.get('steps', []),
                'url': tc.get('url', '')
            },
            type=tc.get('type', 'recorded'),
            status=tc.get('status', 'draft'),
            created_at=datetime.fromisoformat(tc['created_at']) if tc.get('created_at') else datetime.utcnow()
        )
        db.add(test_case)
        count += 1
        print(f"  ✅ 迁移测试用例: {tc.get('name')}")
    
    db.commit()
    db.close()
    return count

def migrate_recordings():
    """迁移录制用例"""
    recordings_file = DATA_DIR / "recordings.json"
    if not recordings_file.exists():
        print("⚠️ 录制用例文件不存在，跳过迁移")
        return 0
    
    with open(recordings_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    db = get_session()
    count = 0
    
    for rec in data:
        existing = db.query(Recording).filter(Recording.name == rec.get('name')).first()
        if existing:
            print(f"  ⏭️ 录制用例已存在: {rec.get('name')}")
            continue
        
        recording = Recording(
            name=rec.get('name', '未命名录制'),
            description=rec.get('description', ''),
            url=rec.get('url', ''),
            actions=rec.get('actions', []),
            created_at=datetime.fromisoformat(rec['created_at']) if rec.get('created_at') else datetime.utcnow()
        )
        db.add(recording)
        count += 1
        print(f"  ✅ 迁移录制用例: {rec.get('name')}")
    
    db.commit()
    db.close()
    return count

def migrate_visual_templates():
    """迁移视觉模板"""
    templates_dir = Path(__file__).parent / "visual_templates"
    if not templates_dir.exists():
        print("⚠️ 模板目录不存在，跳过迁移")
        return 0
    
    db = get_session()
    count = 0
    
    for template_file in templates_dir.glob("*.png"):
        template_name = template_file.stem
        type_file = templates_dir / f"{template_name}_type.json"
        threshold_file = templates_dir / f"{template_name}_threshold.json"
        
        element_type = "other"
        if type_file.exists():
            with open(type_file, 'r', encoding='utf-8') as f:
                type_data = json.load(f)
                element_type = type_data.get('type', 'other')
        
        match_threshold = 0.8
        if threshold_file.exists():
            with open(threshold_file, 'r', encoding='utf-8') as f:
                threshold_data = json.load(f)
                match_threshold = threshold_data.get('threshold', 0.8)
        
        existing = db.query(VisualElement).filter(VisualElement.name == template_name).first()
        if existing:
            print(f"  ⏭️ 视觉模板已存在: {template_name}")
            continue
        
        visual_element = VisualElement(
            name=template_name,
            element_type=element_type,
            screenshot_path=str(template_file),
            match_threshold=match_threshold
        )
        db.add(visual_element)
        count += 1
        print(f"  ✅ 迁移视觉模板: {template_name} ({element_type})")
    
    db.commit()
    db.close()
    return count

def create_default_project():
    """创建默认项目"""
    db = get_session()
    
    existing = db.query(Project).filter(Project.name == "默认项目").first()
    if existing:
        print("  ⏭️ 默认项目已存在")
        db.close()
        return existing.id
    
    project = Project(
        name="默认项目",
        description="系统默认项目",
        base_url="https://www.example.com",
        status="active"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    project_id = project.id
    db.close()
    
    print(f"  ✅ 创建默认项目 (ID: {project_id})")
    return project_id

def main():
    print("🚀 开始数据迁移...")
    print()
    
    try:
        print("📦 初始化数据库连接...")
        init_database()
        
        print("\n📋 创建默认项目...")
        project_id = create_default_project()
        
        print("\n📋 迁移测试用例...")
        tc_count = migrate_test_cases()
        
        print("\n🎬 迁移录制用例...")
        rec_count = migrate_recordings()
        
        print("\n👁️ 迁移视觉模板...")
        tpl_count = migrate_visual_templates()
        
        print()
        print("=" * 50)
        print("✅ 数据迁移完成!")
        print(f"  - 测试用例: {tc_count} 个")
        print(f"  - 录制用例: {rec_count} 个")
        print(f"  - 视觉模板: {tpl_count} 个")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 数据迁移失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
