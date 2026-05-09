import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db

app = create_app()


def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()

        from app.models.user import User, Role

        if not Role.query.filter_by(code='admin').first():
            admin_role = Role(name='系统管理员', code='admin', permissions='all')
            db.session.add(admin_role)

        if not Role.query.filter_by(code='user').first():
            user_role = Role(name='普通用户', code='user', permissions='read')
            db.session.add(user_role)

        if not Role.query.filter_by(code='engineer').first():
            engineer_role = Role(name='工程师', code='engineer', permissions='read,write,workorder')
            db.session.add(engineer_role)

        if not Role.query.filter_by(code='manager').first():
            manager_role = Role(name='运营主管', code='manager', permissions='read,write,report')
            db.session.add(manager_role)

        db.session.commit()

        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                nickname='系统管理员',
                email='admin@example.com',
                role_id=admin_role.id
            )
            admin.set_password('admin123')
            db.session.add(admin)

            demo_user = User(
                username='zhangsan',
                nickname='张三',
                email='zhangsan@example.com',
                role_id=engineer_role.id
            )
            demo_user.set_password('123456')
            db.session.add(demo_user)

            db.session.commit()
            print('默认用户创建完成')
            print('  - admin / admin123 (系统管理员)')
            print('  - zhangsan / 123456 (工程师)')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
