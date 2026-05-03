from database import init_database, get_db
from database import VisualElement

# 初始化数据库
init_database()

# 获取数据库会话
db = next(get_db())

# 查询所有视觉模板
templates = db.query(VisualElement).all()

# 打印模板信息
print('模板数量:', len(templates))
for t in templates:
    print('名称:', t.name, '路径:', t.screenshot_path)

# 关闭数据库会话
db.close()
