"""
数据库初始化脚本 - 自动创建数据库和表
"""
import pymysql
from sqlalchemy import create_engine, text
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_CONFIG

def create_database():
    """创建数据库"""
    connection = pymysql.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        charset=DATABASE_CONFIG['charset']
    )
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ 数据库 '{DATABASE_CONFIG['database']}' 创建成功")
        connection.commit()
    finally:
        connection.close()

def create_tables():
    """创建数据表"""
    from database import init_database, Base
    from config import DATABASE_URL
    
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    print("✅ 数据表创建成功")

def main():
    print("🚀 开始初始化数据库...")
    
    try:
        print("📦 创建数据库...")
        create_database()
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False
    
    try:
        print("📋 创建数据表...")
        create_tables()
    except Exception as e:
        print(f"❌ 创建数据表失败: {e}")
        return False
    
    print("✅ 数据库初始化完成!")
    return True

if __name__ == "__main__":
    main()
