from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()

# 配置登录管理
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    try:
        user_id_int = int(user_id) if user_id else None
        return User.query.get(user_id_int) if user_id_int is not None else None
    except (ValueError, TypeError):
        return None
