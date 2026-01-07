"""数据库初始化脚本"""

import os
import sys

# 从.env文件中读取配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 手动设置环境变量（如果还没有设置）
if not os.getenv('DB_USER'):
    os.environ['DB_USER'] = os.getenv('DB_USER', 'root')
if not os.getenv('DB_PASSWORD'):
    os.environ['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'AAAaaa211')
if not os.getenv('DB_HOST'):
    os.environ['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
if not os.getenv('DB_PORT'):
    os.environ['DB_PORT'] = os.getenv('DB_PORT', '3306')
if not os.getenv('DB_NAME'):
    os.environ['DB_NAME'] = os.getenv('DB_NAME', 'jieke')

from main import app, db
from models.user import User

def init_database():
    with app.app_context():
        print('=' * 60)
        print('数据库初始化')
        print('=' * 60)
        print(f'数据库URL: {app.config["SQLALCHEMY_DATABASE_URI"]}')
        print()
        
        # 创建所有表
        print('创建数据库表...')
        db.create_all()
        print('[成功] 表创建成功')
        print()
        
        # 创建默认管理员用户（如果不存在）
        print('检查默认用户...')
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print('创建admin用户...')
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print('[成功] admin 用户创建成功')
            print('  用户名: admin')
            print('  密码: admin123')
        else:
            print('[成功] admin 用户已存在')
        
        print()
        print('=' * 60)
        print('[成功] 数据库初始化完成')
        print('=' * 60)

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f'[错误] 初始化失败: {e}', file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
