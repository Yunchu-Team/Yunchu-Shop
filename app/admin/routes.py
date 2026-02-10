from flask import render_template, url_for, flash, redirect, request, current_app, jsonify
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models import User, Product, Order_Core, OrderItem, Cart, DiscountCode, InviteRelation, EarningRecord, WithdrawalRequest, CDKey, SiteSetting
from app.utils.crypto import encrypt_text
from app.extensions import db, bcrypt
from app.utils.image_processor import ImageProcessor
from app.utils.order_state_manager import OrderStateManager
from app.utils.aff_calculator import AffiliateCalculator
from app.utils.pagination import paginate
from config import Config
from datetime import datetime
import json
import os
import secrets
from sqlalchemy import extract

def generate_invite_code():
    return secrets.token_urlsafe(10)[:10]

order_state_manager = OrderStateManager(Config.ORDER_STATE_DATA_DIR)
affiliate_calculator = AffiliateCalculator(Config.AFF_COMMISSION_RATE)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'moderator']:
            flash('无权访问管理后台', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    today = datetime.utcnow().date()

    today_orders = Order_Core.query.filter(
        db.func.date(Order_Core.created_at) == today
    ).count()

    today_sales = db.session.query(
        db.func.sum(Order_Core.final_amount)
    ).filter(
        db.func.date(Order_Core.created_at) == today,
        Order_Core.cached_status.in_(['user_paid', 'shipped', 'completed'])
    ).scalar() or 0

    today_users = User.query.filter(
        db.func.date(User.created_at) == today
    ).count()

    total_users = User.query.count()

    total_products = Product.query.count()
    total_orders = Order_Core.query.count()
    pending_orders = Order_Core.query.filter(Order_Core.cached_status.in_(['pending_payment', 'user_paid', 'shipped'])).count()

    # 查询月度销售统计数据
    monthly_sales = []
    for month in range(1, 7):
        month_sales = db.session.query(
            db.func.sum(Order_Core.final_amount)
        ).filter(
            extract('month', Order_Core.created_at) == month,
            extract('year', Order_Core.created_at) == datetime.utcnow().year,
            Order_Core.cached_status.in_(['user_paid', 'shipped', 'completed'])
        ).scalar() or 0
        monthly_sales.append(float(month_sales))

    return render_template('admin/dashboard.html',
                           today_orders=today_orders,
                           today_sales=today_sales,
                           today_users=today_users,
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           monthly_sales=monthly_sales,
                           pending_orders=pending_orders)

@admin_bp.route('/users')
@login_required
@admin_required
def user_management():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    role = request.args.get('role')

    query = User.query

    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.display_name.ilike(f'%{search}%'))
        )

    if role:
        query = query.filter_by(role=role)

    query = query.order_by(User.created_at.desc())
    pagination = paginate(query, page=page, per_page=20)

    return render_template('admin/user_management.html', pagination=pagination, search=search, role=role)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)

    invite_relations = InviteRelation.query.filter_by(inviter_id=user_id).all()
    invitees = []
    for relation in invite_relations:
        invitee = User.query.get(relation.invitee_id)
        if invitee:
            invitees.append(invitee)

    earnings = EarningRecord.query.filter_by(user_id=user_id).order_by(EarningRecord.created_at.desc()).limit(10).all()
    withdrawals = WithdrawalRequest.query.filter_by(user_id=user_id).order_by(WithdrawalRequest.created_at.desc()).limit(10).all()

    return render_template('admin/user_detail.html', user=user, invitees=invitees, earnings=earnings, withdrawals=withdrawals)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()

    status = '启用' if user.is_active else '禁用'
    flash(f'用户已{status}', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/update-role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    if current_user.role != 'admin':
        flash('只有管理员可以修改用户角色', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))

    user = User.query.get_or_404(user_id)
    if user.username == 'QiuLingYan' or user.role == 'admin':
        flash('超级管理员角色不可修改', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    new_role = request.form.get('role')

    if new_role in ['user', 'moderator']:
        user.role = new_role
        db.session.commit()
        flash('用户角色已更新', 'success')
    else:
        flash('无效的角色', 'danger')

    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/products')
@login_required
@admin_required
def product_management():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')

    query = Product.query

    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.description.ilike(f'%{search}%'))
        )

    query = query.order_by(Product.created_at.desc())
    pagination = paginate(query, page=page, per_page=20)

    return render_template('admin/product_management.html', pagination=pagination, search=search)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price_raw = request.form.get('price')
        try:
            price = float(price_raw) if price_raw else 0.0
        except ValueError:
            price = 0.0
        description = request.form.get('description')
        category = request.form.get('category', '默认分类')
        tags = request.form.get('tags')
        image = request.files.get('image')
        stock_raw = request.form.get('stock')
        try:
            stock = int(stock_raw) if stock_raw else 0
        except ValueError:
            stock = 0

        if not all([name, price, description]):
            flash('请填写所有必填字段', 'danger')
            return render_template('admin/product_form.html')

        image_filename = None
        if image:
            image_processor = ImageProcessor(current_app.config['UPLOAD_FOLDER'])
            image_filename = image_processor.process_uploaded_image(image, 'products')

        product = Product(
            name=name,
            price=price,
            description=description,
            category=category,
            tags=tags,
            image_filename=image_filename,
            stock_virtual=stock
        )

        db.session.add(product)
        db.session.commit()

        flash('商品添加成功', 'success')
        return redirect(url_for('admin.product_management'))

    return render_template('admin/product_form.html')

@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name', product.name)
        price_raw = request.form.get('price')
        try:
            product.price = float(price_raw) if price_raw else product.price
        except ValueError:
            product.price = product.price
        product.description = request.form.get('description', product.description)
        product.category = request.form.get('category', product.category)
        product.tags = request.form.get('tags', product.tags)

        image = request.files.get('image')
        if image:
            image_processor = ImageProcessor(current_app.config['UPLOAD_FOLDER'])
            if product.image_filename:
                image_processor.delete_image(product.image_filename)
            image_filename = image_processor.process_uploaded_image(image, 'products')
            product.image_filename = image_filename

        product.is_active = 'is_active' in request.form

        db.session.commit()
        flash('商品已更新', 'success')
        return redirect(url_for('admin.product_management'))

    return render_template('admin/product_form.html', product=product)

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    # 如果已有订单使用该商品，禁止删除，改为下架
    has_orders = OrderItem.query.filter_by(product_id=product_id).first()
    if has_orders:
        product.is_active = False
        db.session.commit()
        flash('该商品已有订单记录，已下架但无法删除', 'warning')
        if request.is_json:
            return jsonify({'success': True, 'message': '该商品已有订单记录，已下架但无法删除'})
        return redirect(url_for('admin.product_management'))

    if product.image_filename:
        image_processor = ImageProcessor(current_app.config['UPLOAD_FOLDER'])
        image_processor.delete_image(product.image_filename)

    # 清理相关购物车与卡密
    Cart.query.filter_by(product_id=product_id).delete()
    CDKey.query.filter_by(product_id=product_id).delete()

    db.session.delete(product)
    db.session.commit()

    flash('商品已删除', 'success')
    if request.is_json:
        return jsonify({'success': True, 'message': '商品已删除'})
    return redirect(url_for('admin.product_management'))

@admin_bp.route('/products/<int:product_id>/cdkeys')
@login_required
@admin_required
def product_cdkeys(product_id):
    product = Product.query.get_or_404(product_id)

    page = request.args.get('page', 1, type=int)
    query = CDKey.query.filter_by(product_id=product_id).order_by(CDKey.id.desc())
    pagination = paginate(query, page=page, per_page=50)

    return render_template('admin/product_cdkeys.html', product=product, pagination=pagination)

@admin_bp.route('/products/<int:product_id>/cdkeys/add', methods=['POST'])
@login_required
@admin_required
def add_cdkeys(product_id):
    product = Product.query.get_or_404(product_id)
    keys_text = request.form.get('keys')

    if not keys_text:
        flash('请输入卡密', 'danger')
        return redirect(url_for('admin.product_cdkeys', product_id=product_id))

    keys = [key.strip() for key in keys_text.split('\n') if key.strip()]
    
    added_count = 0
    
    for key in keys:
        cdkey = CDKey(
            product_id=product_id,
            key=key,
            status='unsold'
        )
        db.session.add(cdkey)
        added_count += 1

    product.stock_virtual = CDKey.query.filter_by(product_id=product_id, status='unsold').count()
    db.session.commit()

    if added_count > 0:
        flash(f'已成功添加{added_count}个卡密', 'success')
    if added_count == 0:
        flash('没有有效的卡密被添加', 'warning')
    
    return redirect(url_for('admin.product_cdkeys', product_id=product_id))

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        display_name = request.form.get('display_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        contact = request.form.get('contact')

        if not all([username, display_name, email, password]):
            flash('请填写所有必填字段', 'danger')
            return render_template('admin/user_form.html')

        if User.query.filter_by(username=username).first():
            flash('用户名已被使用', 'danger')
            return render_template('admin/user_form.html')

        if User.query.filter_by(email=email).first():
            flash('邮箱已被使用', 'danger')
            return render_template('admin/user_form.html')

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(
            username=username,
            display_name=display_name,
            email=email,
            password_hash=password_hash,
            contact=contact,
            role=role,
            invite_code=generate_invite_code()
        )

        db.session.add(user)
        db.session.commit()

        flash('用户添加成功', 'success')
        return redirect(url_for('admin.user_management'))

    return render_template('admin/user_form.html')

@admin_bp.route('/orders')
@login_required
@admin_required
def order_management():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    search = request.args.get('search')

    query = Order_Core.query

    if status:
        query = query.filter_by(cached_status=status)

    if search:
        query = query.join(User).filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    query = query.order_by(Order_Core.created_at.desc())
    pagination = paginate(query, page=page, per_page=20)

    return render_template('admin/order_management.html', pagination=pagination, status=status, search=search)

@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order_Core.query.get_or_404(order_id)
    order_state = order_state_manager.get_order_state(order_id)

    return render_template('admin/order_detail.html', order=order, order_state=order_state)

@admin_bp.route('/orders/<int:order_id>/ship', methods=['POST'])
@login_required
@admin_required
def ship_order(order_id):
    order = Order_Core.query.get_or_404(order_id)

    if order.cached_status != 'user_paid':
        flash('订单状态不允许发货', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))

    # 检查是否需要手动发货
    has_cdkey = False
    for order_item in order.order_items:
        available = CDKey.query.filter_by(
            product_id=order_item.product_id,
            status='unsold'
        ).limit(order_item.quantity).all()
        if len(available) >= order_item.quantity:
            has_cdkey = True
            break

    # 如果有卡密，自动发货
    if has_cdkey:
        assigned_keys = []
        for order_item in order.order_items:
            cdkeys = CDKey.query.filter_by(
                product_id=order_item.product_id,
                status='unsold'
            ).limit(order_item.quantity).all()

            for cdkey in cdkeys:
                cdkey.status = 'sold'
                cdkey.sold_at = datetime.utcnow()
                cdkey.order_id = order_id
                assigned_keys.append(cdkey.key)

            product = Product.query.get(order_item.product_id)
            if product:
                product.stock_virtual = CDKey.query.filter_by(product_id=order_item.product_id, status='unsold').count()

        if assigned_keys:
            order_state_manager.assign_cdkey(order_id, assigned_keys)

        order_state_manager.update_state(order_id, 'shipped', '订单已发货')
        order.cached_status = 'shipped'
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'message': '订单已发货'})
        flash('订单已发货', 'success')
        return redirect(url_for('admin.order_detail', order_id=order_id))
    else:
        # 没有卡密，需要手动输入发货内容
        if request.is_json:
            data = request.get_json()
            ship_content = data.get('ship_content', '')
            
            if not ship_content:
                return jsonify({'success': False, 'message': '请输入发货内容'})
            
            order_state_manager.update_state(order_id, 'shipped', f'订单已发货：{ship_content}')
            order.cached_status = 'shipped'
            db.session.commit()
            
            return jsonify({'success': True, 'message': '订单已发货'})
        else:
            # 非AJAX请求，返回错误信息
            flash('该订单需要手动发货，请在订单详情页面操作', 'warning')
            return redirect(url_for('admin.order_detail', order_id=order_id))

@admin_bp.route('/orders/<int:order_id>/complete', methods=['POST'])
@login_required
@admin_required
def complete_order(order_id):
    order = Order_Core.query.get_or_404(order_id)

    if order.cached_status != 'shipped':
        flash('订单状态不允许完成', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))

    order_state_manager.update_state(order_id, 'completed', '订单已完成')
    order.cached_status = 'completed'
    db.session.commit()

    invite_relation = InviteRelation.query.filter_by(invitee_id=order.user_id).first()
    if invite_relation:
        affiliate_calculator.create_earning_record(invite_relation.inviter_id, order.id, order.final_amount)

    flash('订单已完成', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin_bp.route('/orders/<int:order_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_order(order_id):
    order = Order_Core.query.get_or_404(order_id)
    reason = request.form.get('reason', '订单被拒绝')

    if order.cached_status == 'completed':
        flash('已完成的订单不能拒绝', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))

    order_state_manager.update_state(order_id, 'rejected', reason)
    order.cached_status = 'rejected'
    db.session.commit()

    flash('订单已拒绝', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin_bp.route('/discounts')
@login_required
@admin_required
def discount_management():
    page = request.args.get('page', 1, type=int)

    query = DiscountCode.query.order_by(DiscountCode.created_at.desc())
    pagination = paginate(query, page=page, per_page=20)

    return render_template('admin/discount_management.html', pagination=pagination)

@admin_bp.route('/discounts/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_discount():
    if request.method == 'POST':
        code = request.form.get('code')
        discount_type = request.form.get('type')
        value_raw = request.form.get('value')
        try:
            value = float(value_raw) if value_raw else 0.0
        except ValueError:
            value = 0.0
        min_order_amount_raw = request.form.get('min_order_amount')
        try:
            min_order_amount = float(min_order_amount_raw) if min_order_amount_raw else 0.0
        except ValueError:
            min_order_amount = 0.0
        max_uses_raw = request.form.get('max_uses')
        try:
            max_uses = int(max_uses_raw) if max_uses_raw else None
        except ValueError:
            max_uses = None
        valid_from = request.form.get('valid_from')
        valid_to = request.form.get('valid_to')

        if not all([code, discount_type, value]):
            flash('请填写所有必填字段', 'danger')
            return render_template('admin/discount_form.html')

        if DiscountCode.query.filter_by(code=code).first():
            flash('折扣码已存在', 'danger')
            return render_template('admin/discount_form.html')

        discount = DiscountCode(
            code=code,
            type=discount_type,
            value=value,
            min_order_amount=min_order_amount,
            max_uses=max_uses,
            valid_from=datetime.strptime(valid_from, '%Y-%m-%d') if valid_from else datetime.utcnow(),
            valid_to=datetime.strptime(valid_to, '%Y-%m-%d') if valid_to else None
        )

        db.session.add(discount)
        db.session.commit()

        flash('折扣码添加成功', 'success')
        return redirect(url_for('admin.discount_management'))

    return render_template('admin/discount_form.html')

@admin_bp.route('/discounts/edit/<int:discount_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_discount(discount_id):
    discount = DiscountCode.query.get_or_404(discount_id)
    
    if request.method == 'POST':
        code = request.form.get('code')
        discount_type = request.form.get('type')
        value_raw = request.form.get('value')
        try:
            value = float(value_raw) if value_raw else 0.0
        except ValueError:
            value = 0.0
        min_order_amount_raw = request.form.get('min_order_amount')
        try:
            min_order_amount = float(min_order_amount_raw) if min_order_amount_raw else 0.0
        except ValueError:
            min_order_amount = 0.0
        max_uses_raw = request.form.get('max_uses')
        try:
            max_uses = int(max_uses_raw) if max_uses_raw else None
        except ValueError:
            max_uses = None
        valid_from = request.form.get('valid_from')
        valid_to = request.form.get('valid_to')

        if not all([code, discount_type, value]):
            flash('请填写所有必填字段', 'danger')
            return render_template('admin/discount_form.html', discount=discount)

        if DiscountCode.query.filter_by(code=code).filter(DiscountCode.id != discount_id).first():
            flash('折扣码已存在', 'danger')
            return render_template('admin/discount_form.html', discount=discount)

        discount.code = code
        discount.type = discount_type
        discount.value = value
        discount.min_order_amount = min_order_amount
        discount.max_uses = max_uses
        discount.valid_from = datetime.strptime(valid_from, '%Y-%m-%d') if valid_from else datetime.utcnow()
        discount.valid_to = datetime.strptime(valid_to, '%Y-%m-%d') if valid_to else None

        db.session.commit()

        flash('折扣码更新成功', 'success')
        return redirect(url_for('admin.discount_management'))

    return render_template('admin/discount_form.html', discount=discount)

@admin_bp.route('/discounts/<int:discount_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_discount(discount_id):
    discount = DiscountCode.query.get_or_404(discount_id)
    discount.is_active = not discount.is_active
    db.session.commit()

    status = '启用' if discount.is_active else '禁用'
    if request.is_json:
        return jsonify({'success': True, 'message': f'折扣码已{status}'})
    flash(f'折扣码已{status}', 'success')
    return redirect(url_for('admin.discount_management'))

@admin_bp.route('/discounts/<int:discount_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_discount(discount_id):
    discount = DiscountCode.query.get_or_404(discount_id)
    
    # 检查折扣码是否已被使用
    if discount.used_count > 0:
        return jsonify({'success': False, 'message': '无法删除已被使用的折扣码'})
    
    db.session.delete(discount)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '折扣码已删除'})

@admin_bp.route('/affiliate')
@login_required
@admin_required
def affiliate_management():
    commission_rate = current_app.config['AFF_COMMISSION_RATE']
    settlement_period = current_app.config['SETTLEMENT_PERIOD']
    min_withdrawal = current_app.config['MIN_WITHDRAWAL_AMOUNT']

    total_earnings = db.session.query(db.func.sum(EarningRecord.amount)).scalar() or 0
    pending_earnings = db.session.query(db.func.sum(EarningRecord.amount)).filter_by(status='pending').scalar() or 0
    available_earnings = db.session.query(db.func.sum(EarningRecord.amount)).filter_by(status='available').scalar() or 0

    page = request.args.get('page', 1, type=int)
    query = WithdrawalRequest.query.order_by(WithdrawalRequest.created_at.desc())
    pagination = paginate(query, page=page, per_page=20)

    return render_template('admin/affiliate_management.html',
                           commission_rate=commission_rate,
                           settlement_period=settlement_period,
                           min_withdrawal=min_withdrawal,
                           total_earnings=total_earnings,
                           pending_earnings=pending_earnings,
                           available_earnings=available_earnings,
                           pagination=pagination)

@admin_bp.route('/affiliate/settle', methods=['POST'])
@login_required
@admin_required
def settle_earnings():
    count = affiliate_calculator.settle_earnings(current_app.config['SETTLEMENT_PERIOD'])
    flash(f'已结算{count}笔收益', 'success')
    return redirect(url_for('admin.affiliate_management'))

@admin_bp.route('/withdrawal/<int:withdrawal_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_withdrawal(withdrawal_id):
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)

    if withdrawal.status != 'submitted':
        flash('提现申请状态不允许批准', 'danger')
        return redirect(url_for('admin.affiliate_management'))

    withdrawal.status = 'approved'
    withdrawal.feedback = request.form.get('feedback', '')

    affiliate_calculator.process_withdrawal(withdrawal)

    flash('提现申请已批准', 'success')
    return redirect(url_for('admin.affiliate_management'))

@admin_bp.route('/withdrawal/<int:withdrawal_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_withdrawal(withdrawal_id):
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)

    if withdrawal.status != 'submitted':
        flash('提现申请状态不允许拒绝', 'danger')
        return redirect(url_for('admin.affiliate_management'))

    withdrawal.status = 'rejected'
    withdrawal.feedback = request.form.get('feedback', '提现被拒绝')

    db.session.commit()

    flash('提现申请已拒绝', 'success')
    return redirect(url_for('admin.affiliate_management'))

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    site_settings = SiteSetting.get()
    quick_links = []
    if site_settings and site_settings.quick_links:
        try:
            quick_links = json.loads(site_settings.quick_links)
        except (TypeError, json.JSONDecodeError):
            quick_links = []
    return render_template('admin/settings.html',
                           commission_rate=current_app.config['AFF_COMMISSION_RATE'],
                           settlement_period=current_app.config['SETTLEMENT_PERIOD'],
                           min_withdrawal=current_app.config['MIN_WITHDRAWAL_AMOUNT'],
                           site_settings=site_settings,
                           quick_links=quick_links)

@admin_bp.route('/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    if current_user.role != 'admin':
        flash('只有管理员可以修改设置', 'danger')
        return redirect(url_for('admin.settings'))

    commission_rate_raw = request.form.get('commission_rate')
    try:
        commission_rate = float(commission_rate_raw) if commission_rate_raw else 0.0
    except ValueError:
        commission_rate = 0.0
    
    settlement_period_raw = request.form.get('settlement_period')
    try:
        settlement_period = int(settlement_period_raw) if settlement_period_raw else 30
    except ValueError:
        settlement_period = 30
    
    min_withdrawal_raw = request.form.get('min_withdrawal')
    try:
        min_withdrawal = float(min_withdrawal_raw) if min_withdrawal_raw else 0.0
    except ValueError:
        min_withdrawal = 0.0
    site_name = request.form.get('site_name')
    footer_text = request.form.get('footer_text')
    contact_email = request.form.get('contact_email')
    about_us = request.form.get('about_us')
    quick_links_text = request.form.get('quick_links')
    bank_label = request.form.get('bank_label')
    gh_repo = request.form.get('gh_repo')
    gh_branch = request.form.get('gh_branch')
    gh_token = request.form.get('gh_token')
    logo = request.files.get('site_logo')
    wechat_qr = request.files.get('wechat_qr')
    alipay_qr = request.files.get('alipay_qr')
    bank_qr = request.files.get('bank_qr')
    logo_url = request.form.get('site_logo_url')
    wechat_qr_url = request.form.get('wechat_qr_url')
    alipay_qr_url = request.form.get('alipay_qr_url')
    bank_qr_url = request.form.get('bank_qr_url')

    current_app.config['AFF_COMMISSION_RATE'] = commission_rate
    current_app.config['SETTLEMENT_PERIOD'] = settlement_period
    current_app.config['MIN_WITHDRAWAL_AMOUNT'] = min_withdrawal

    settings = SiteSetting.get()
    if site_name:
        settings.site_name = site_name
    settings.footer_text = footer_text
    settings.contact_email = contact_email
    settings.about_us = about_us
    settings.bank_label = bank_label
    settings.gh_repo = gh_repo or settings.gh_repo
    settings.gh_branch = gh_branch or settings.gh_branch or 'main'
    if gh_token:
        settings.gh_token_enc = encrypt_text(gh_token, current_app.config['SECRET_KEY'])

    # 解析快速链接（每行: 标题|URL）
    if quick_links_text is not None:
        links = []
        for line in quick_links_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if '|' in line:
                title, url = line.split('|', 1)
                title = title.strip()
                url = url.strip()
                if title and url:
                    links.append({'title': title, 'url': url})
        settings.quick_links = json.dumps(links, ensure_ascii=False)

    image_processor = ImageProcessor(current_app.config['UPLOAD_FOLDER'])

    if logo:
        if settings.site_logo:
            image_processor.delete_image(settings.site_logo)
        settings.site_logo = image_processor.process_uploaded_image(logo, 'site')
    elif logo_url:
        settings.site_logo = logo_url.strip()

    if wechat_qr:
        if settings.wechat_qr:
            image_processor.delete_image(settings.wechat_qr)
        settings.wechat_qr = image_processor.process_uploaded_image(wechat_qr, 'payments')
    elif wechat_qr_url:
        settings.wechat_qr = wechat_qr_url.strip()

    if alipay_qr:
        if settings.alipay_qr:
            image_processor.delete_image(settings.alipay_qr)
        settings.alipay_qr = image_processor.process_uploaded_image(alipay_qr, 'payments')
    elif alipay_qr_url:
        settings.alipay_qr = alipay_qr_url.strip()

    if bank_qr:
        if settings.bank_qr:
            image_processor.delete_image(settings.bank_qr)
        settings.bank_qr = image_processor.process_uploaded_image(bank_qr, 'payments')
    elif bank_qr_url:
        settings.bank_qr = bank_qr_url.strip()

    settings.updated_at = datetime.utcnow()
    db.session.commit()

    flash('设置已更新', 'success')
    return redirect(url_for('admin.settings'))

@admin_bp.route('/products/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_product_status():  # 这个函数名决定了端点名称
    """切换商品上下架状态"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        status = data.get('status')

        product = Product.query.get_or_404(product_id)
        
        # 根据前端传递的状态值更新商品的is_active属性
        if status == 'active':
            product.is_active = True
        elif status == 'inactive':
            product.is_active = False
        else:
            return jsonify({'success': False, 'message': '无效的状态值'}), 400

        db.session.commit()
        
        return jsonify({'success': True, 'message': '商品状态更新成功'})
    except Exception as e:
        current_app.logger.error(f"切换商品状态时出错: {str(e)}")
        return jsonify({'success': False, 'message': '操作失败，请重试'}), 500

@admin_bp.route('/products/export')
@login_required
@admin_required
def export_products():
    """导出商品列表为CSV格式"""
    try:
        import csv
        import io
        from flask import make_response
        
        products = Product.query.all()
        
        # 创建内存中的CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(['ID', '商品名称', '分类', '价格', '描述', '标签', '库存', '销量', '状态', '创建时间'])
        
        # 写入数据
        for product in products:
            writer.writerow([
                product.id,
                product.name,
                product.category,
                product.price,
                product.description,
                product.tags,
                product.stock,
                product.sold_count,
                '上架' if product.is_active else '下架',
                product.created_at.strftime('%Y-%m-%d %H:%M:%S') if product.created_at else ''
            ])
        
        # 获取CSV内容
        csv_content = output.getvalue()
        output.close()
        
        # 创建响应
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
    except Exception as e:
        current_app.logger.error(f"导出商品时出错: {str(e)}")
        flash('导出商品失败', 'danger')
        return redirect(url_for('admin.product_management'))

@admin_bp.route('/orders/update_status', methods=['POST'])
@login_required
@admin_required
def update_order_status():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        status = data.get('status')
        reason = data.get('reason', '')

        order = Order_Core.query.get_or_404(order_id)
        
        # 验证状态转换是否合法
        valid_transitions = {
            'pending_payment': ['user_paid', 'rejected'],
            'user_paid': ['shipped', 'rejected'],
            'shipped': ['completed', 'rejected'],
            'completed': [],
            'rejected': ['pending_payment']  # 可以从拒绝状态恢复
        }
        
        if order.cached_status not in valid_transitions or status not in valid_transitions[order.cached_status]:
            return jsonify({'success': False, 'message': '不允许的状态转换'}), 400

        # 执行状态变更
        if status == 'rejected':
            order_state_manager.update_state(order_id, 'rejected', reason or '订单被拒绝')
        else:
            order_state_manager.update_state(order_id, status, f'订单状态更新为 {status}')
            
        order.cached_status = status
        db.session.commit()

        # 如果是完成订单，处理返佣
        if status == 'completed':
            invite_relation = InviteRelation.query.filter_by(invitee_id=order.user_id).first()
            if invite_relation:
                affiliate_calculator.create_earning_record(invite_relation.inviter_id, order.id, order.final_amount)

        return jsonify({'success': True, 'message': '订单状态更新成功'})
    except Exception as e:
        current_app.logger.error(f"更新订单状态时出错: {str(e)}")
        return jsonify({'success': False, 'message': '更新失败，请重试'}), 500
