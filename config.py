import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有安装python-dotenv包，跳过加载环境变量
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join('app', 'static', 'uploads')
    ORDER_STATE_DATA_DIR = os.environ.get('ORDER_STATE_DATA_DIR') or os.path.join('data', 'order_states')
    NEZHA_URL = os.environ.get('NEZHA_URL')
    NEZHA_TOKEN = os.environ.get('NEZHA_TOKEN')
    
    # 图片上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # 分页配置
    POSTS_PER_PAGE = 20
    
    # 邀请系统配置
    AFF_COMMISSION_RATE = 0.1  # 10% 佣金比例
    MIN_WITHDRAWAL_AMOUNT = 10  # 最低提现金额
    SETTLEMENT_PERIOD = 7  # 结算周期（天）

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    
    # 生产环境特定配置
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}