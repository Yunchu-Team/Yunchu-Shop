from flask import Flask, render_template, send_from_directory
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from config import config
from app.extensions import db, login_manager, bcrypt, migrate, csrf

from app.auth import auth_bp
from app.admin import admin_bp
from app.user import user_bp
from app.product import product_bp
from app.order import order_bp
from app.utils.schema_migrate import ensure_sqlite_schema

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(order_bp, url_prefix='/order')
    
    @app.route('/')
    def index():
        from app.models import Product
        
        # 查询热门商品（按销量排序，最多4个）
        hot_products = Product.query.filter_by(is_active=True).order_by(Product.sold_count.desc()).limit(4).all()
        
        # 查询最新商品（按创建时间排序，最多4个）
        new_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(4).all()
        
        return render_template('index.html', 
                             hot_products=hot_products, 
                             new_products=new_products)
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        upload_folder = app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename)

    with app.app_context():
        ensure_sqlite_schema(db)

    @app.context_processor
    def inject_site_settings():
        from app.models import SiteSetting
        settings = SiteSetting.get()
        quick_links = []
        if settings.quick_links:
            try:
                import json
                quick_links = json.loads(settings.quick_links)
            except Exception:
                quick_links = []
        return {'site_settings': settings, 'quick_links': quick_links}
    
    return app
