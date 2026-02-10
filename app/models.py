from datetime import datetime
from app.extensions import db
from flask_login import UserMixin
import json

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    contact = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    avatar_filename = db.Column(db.String(100), nullable=True)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    balance_available = db.Column(db.Float, default=0.0)
    balance_pending = db.Column(db.Float, default=0.0)
    total_earned = db.Column(db.Float, default=0.0)
    
    orders = db.relationship('Order_Core', back_populates='user', lazy=True)
    cart_items = db.relationship('Cart', back_populates='user', lazy=True, cascade='all, delete-orphan')
    earnings = db.relationship('EarningRecord', backref='user', lazy=True)
    withdrawals = db.relationship('WithdrawalRequest', backref='user', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # 添加分类字段
    tags = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    image_filename = db.Column(db.String(100), nullable=True)
    view_count = db.Column(db.Integer, default=0)
    sold_count = db.Column(db.Integer, default=0)
    stock_virtual = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', back_populates='product', lazy=True)
    cdkeys = db.relationship('CDKey', backref='product', lazy=True)
    
    @property
    def image_url(self):
        """返回图片的完整URL"""
        if self.image_filename:
            # 如果已经是完整的URL（如GitHub raw链接），直接返回
            if self.image_filename.startswith('http://') or self.image_filename.startswith('https://'):
                return self.image_filename
            # 否则返回本地路径
            return f"/uploads/{self.image_filename}"
        return "https://via.placeholder.com/300x200"

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='cart_items', lazy=True)
    product = db.relationship('Product', lazy=True)

class DiscountCode(db.Model):
    __tablename__ = 'discount_code'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Float, nullable=False)
    min_order_amount = db.Column(db.Float, default=0.0)
    max_uses = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    valid_to = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    orders = db.relationship('Order_Core', back_populates='discount_code', lazy=True)

class Order_Core(db.Model):
    __tablename__ = 'order_core'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(6), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    discount_code_id = db.Column(db.Integer, db.ForeignKey('discount_code.id'), nullable=True)
    original_amount = db.Column(db.Float, nullable=False)
    final_amount = db.Column(db.Float, nullable=False)
    cached_status = db.Column(db.String(20), default='pending_payment')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='orders', lazy=True)
    discount_code = db.relationship('DiscountCode', back_populates='orders', lazy=True)
    order_items = db.relationship('OrderItem', back_populates='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_core.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    order = db.relationship('Order_Core', back_populates='order_items', lazy=True)
    product = db.relationship('Product', back_populates='order_items', lazy=True)

class InviteRelation(db.Model):
    __tablename__ = 'invite_relation'
    id = db.Column(db.Integer, primary_key=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code_used = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class EarningRecord(db.Model):
    __tablename__ = 'earning_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order_core.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime, nullable=True)

class WithdrawalRequest(db.Model):
    __tablename__ = 'withdrawal_request'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='submitted')
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class CDKey(db.Model):
    __tablename__ = 'cdkey'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='unsold')
    sold_at = db.Column(db.DateTime, nullable=True)
    order_id = db.Column(db.Integer, nullable=True)

class SiteSetting(db.Model):
    __tablename__ = 'site_setting'
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='云初の小店')
    site_logo = db.Column(db.String(200), nullable=True)
    footer_text = db.Column(db.String(200), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    wechat_qr = db.Column(db.String(200), nullable=True)
    alipay_qr = db.Column(db.String(200), nullable=True)
    bank_qr = db.Column(db.String(200), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    gh_repo = db.Column(db.String(200), nullable=True)
    gh_branch = db.Column(db.String(100), nullable=True)
    gh_token_enc = db.Column(db.Text, nullable=True)
    about_us = db.Column(db.Text, nullable=True)
    quick_links = db.Column(db.Text, nullable=True)
    bank_label = db.Column(db.String(50), nullable=True)

    @classmethod
    def get(cls):
        setting = cls.query.get(1)
        if not setting:
            setting = cls(id=1)
            db.session.add(setting)
            db.session.commit()
        return setting
