from app import create_app
from app.extensions import db, bcrypt
from app.models import User
import os
import secrets

app = create_app()

def init_admin():
    """初始化超级管理员账号"""
    with app.app_context():
        # 检查是否已存在超级管理员
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 生成邀请码
            invite_code = secrets.token_hex(4).upper()

            admin = User(
                username='admin',
                display_name='超级管理员',
                password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                email='admin@example.com',
                role='admin',
                is_active=True,
                invite_code=invite_code,
                balance_available=0.0,
                balance_pending=0.0,
                total_earned=0.0
            )
            db.session.add(admin)
            db.session.commit()
            print(f'超级管理员已创建: admin / admin123 (请立即修改初始密码!)')
            print(f'管理员邀请码: {invite_code}')
        else:
            print('超级管理员已存在')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_admin()
    app.run(debug=False, host='0.0.0.0', port=5091)
