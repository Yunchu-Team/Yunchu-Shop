from flask import render_template, url_for, flash, redirect, request, jsonify, session, current_app
from flask_login import current_user, login_required
from app.order import order_bp
from app.models import Cart, Product, Order_Core, OrderItem, DiscountCode, CDKey, InviteRelation
from app.extensions import db
from app.utils.order_state_manager import OrderStateManager
from app.utils.aff_calculator import AffiliateCalculator
from config import Config
from datetime import datetime
import random

order_state_manager = OrderStateManager(Config.ORDER_STATE_DATA_DIR)
affiliate_calculator = AffiliateCalculator(Config.AFF_COMMISSION_RATE)

def generate_order_no():
    return f"{random.randint(0, 999999):06d}"

def get_available_stock(product_id):
    cdkey_count = CDKey.query.filter_by(product_id=product_id, status='unsold').count()
    if cdkey_count > 0:
        return cdkey_count
    product = Product.query.get(product_id)
    return product.stock_virtual if product else 0

def get_cart():
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        cart = []
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product and product.is_active:
                cart.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': item.quantity,
                    'image': product.image_filename
                })
        return cart
    else:
        return session.get('cart', [])

def save_cart(cart):
    if current_user.is_authenticated:
        Cart.query.filter_by(user_id=current_user.id).delete()
        for item in cart:
            cart_item = Cart(
                user_id=current_user.id,
                product_id=item['product_id'],
                quantity=item['quantity']
            )
            db.session.add(cart_item)
        db.session.commit()
    else:
        session['cart'] = cart

@order_bp.route('/cart')
def cart_page():
    cart = get_cart()
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template('order/cart.html', cart=cart, total=total)

@order_bp.route('/cart/count')
def cart_count():
    cart = get_cart()
    total = sum(item['price'] * item['quantity'] for item in cart)
    count = sum(item['quantity'] for item in cart)
    return jsonify({'success': True, 'cart_count': count, 'total': total})

@order_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    payload = request.get_json(silent=True) or {}
    product_id = payload.get('product_id')
    quantity = payload.get('quantity', 1)
    
    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': '参数错误'})
    
    product = Product.query.get_or_404(product_id)
    
    if not product.is_active:
        return jsonify({'success': False, 'message': '该商品已下架'})
    
    if quantity < 1:
        return jsonify({'success': False, 'message': '数量不能小于1'})
    
    if get_available_stock(product_id) < quantity:
        return jsonify({'success': False, 'message': '库存不足'})
    
    cart = get_cart()
    
    existing_item = next((item for item in cart if item['product_id'] == product_id), None)
    
    if existing_item:
        new_quantity = existing_item['quantity'] + quantity
        if get_available_stock(product_id) < new_quantity:
            return jsonify({'success': False, 'message': '库存不足'})
        existing_item['quantity'] = new_quantity
    else:
        cart.append({
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity,
            'image': product.image_filename
        })
    
    save_cart(cart)
    
    cart_count = sum(item['quantity'] for item in cart)
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    return jsonify({
        'success': True,
        'message': '商品已添加到购物车',
        'cart_count': cart_count,
        'total': total
    })

@order_bp.route('/cart/update', methods=['POST'])
def update_cart():
    payload = request.get_json(silent=True) or {}
    product_id = payload.get('product_id')
    quantity = payload.get('quantity')
    
    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': '参数错误'})
    
    if quantity < 1:
        return jsonify({'success': False, 'message': '数量不能小于1'})
    
    product = Product.query.get_or_404(product_id)
    
    if get_available_stock(product_id) < quantity:
        return jsonify({'success': False, 'message': '库存不足'})
    
    cart = get_cart()
    
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            break
    
    save_cart(cart)
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    cart_count = sum(item['quantity'] for item in cart)
    
    return jsonify({
        'success': True,
        'message': '购物车已更新',
        'total': total,
        'cart_count': cart_count
    })

@order_bp.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    payload = request.get_json(silent=True) or {}
    product_id = payload.get('product_id')
    
    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': '参数错误'})
    
    cart = get_cart()
    cart = [item for item in cart if item['product_id'] != product_id]
    
    save_cart(cart)
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    cart_count = sum(item['quantity'] for item in cart)
    
    return jsonify({
        'success': True,
        'message': '商品已从购物车移除',
        'total': total,
        'cart_count': cart_count
    })

@order_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    save_cart([])
    
    return jsonify({
        'success': True,
        'message': '购物车已清空',
        'cart_count': 0
    })

@order_bp.route('/checkout')
@login_required
def checkout():
    cart = get_cart()
    
    if not cart:
        flash('购物车为空', 'warning')
        return redirect(url_for('product.product_list'))
    
    original_amount = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template('order/checkout.html', cart=cart, original_amount=original_amount)

@order_bp.route('/cart/apply-discount', methods=['POST'])
def apply_discount():
    cart = get_cart()
    original_amount = sum(item['price'] * item['quantity'] for item in cart)
    
    payload = request.get_json(silent=True) or {}
    code = payload.get('code')
    
    if not code:
        return jsonify({'success': False, 'message': '请输入折扣码'})
    
    discount_code = DiscountCode.query.filter_by(code=code, is_active=True).first()
    
    if not discount_code:
        return jsonify({'success': False, 'message': '折扣码无效'})
    
    if discount_code.valid_from and discount_code.valid_from > datetime.utcnow():
        return jsonify({'success': False, 'message': '折扣码未到生效时间'})
    
    if discount_code.valid_to and discount_code.valid_to < datetime.utcnow():
        return jsonify({'success': False, 'message': '折扣码已过期'})
    
    if discount_code.max_uses and discount_code.used_count >= discount_code.max_uses:
        return jsonify({'success': False, 'message': '折扣码使用次数已达上限'})
    
    if original_amount < discount_code.min_order_amount:
        return jsonify({
            'success': False,
            'message': f'订单金额需达到¥{discount_code.min_order_amount}才能使用此折扣码'
        })
    
    if discount_code.type == 'percentage':
        discount_amount = original_amount * (discount_code.value / 100)
    else:
        discount_amount = discount_code.value
    
    final_amount = max(0, original_amount - discount_amount)
    
    return jsonify({
        'success': True,
        'discount_amount': discount_amount,
        'final_amount': final_amount,
        'message': f'已应用折扣码，优惠¥{discount_amount:.2f}'
    })

@order_bp.route('/checkout/validate-discount', methods=['POST'])
@login_required
def validate_discount():
    payload = request.get_json(silent=True) or {}
    code = payload.get('code')
    original_amount = payload.get('original_amount', 0)
    try:
        original_amount = float(original_amount)
    except (TypeError, ValueError):
        original_amount = 0
    
    if not code:
        return jsonify({'success': False, 'message': '请输入折扣码'})
    
    discount_code = DiscountCode.query.filter_by(code=code, is_active=True).first()
    
    if not discount_code:
        return jsonify({'success': False, 'message': '折扣码无效'})
    
    if discount_code.valid_from and discount_code.valid_from > datetime.utcnow():
        return jsonify({'success': False, 'message': '折扣码未到生效时间'})
    
    if discount_code.valid_to and discount_code.valid_to < datetime.utcnow():
        return jsonify({'success': False, 'message': '折扣码已过期'})
    
    if discount_code.max_uses and discount_code.used_count >= discount_code.max_uses:
        return jsonify({'success': False, 'message': '折扣码使用次数已达上限'})
    
    if original_amount < discount_code.min_order_amount:
        return jsonify({
            'success': False,
            'message': f'订单金额需达到¥{discount_code.min_order_amount}才能使用此折扣码'
        })
    
    if discount_code.type == 'percentage':
        discount_amount = original_amount * (discount_code.value / 100)
    else:
        discount_amount = discount_code.value
    
    final_amount = max(0, original_amount - discount_amount)
    
    return jsonify({
        'success': True,
        'discount_amount': discount_amount,
        'final_amount': final_amount,
        'message': f'已应用折扣码，优惠¥{discount_amount:.2f}'
    })

@order_bp.route('/create', methods=['POST'])
@login_required
def create_order():
    data = request.get_json(silent=True) or {}
    discount_code_str = data.get('discount_code')
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    address = data.get('address')
    payment_method = data.get('payment_method')
    
    if not payment_method:
        return jsonify({'success': False, 'message': '请选择支付方式'})
    
    cart = get_cart()
    
    if not cart:
        return jsonify({'success': False, 'message': '购物车为空'})
    
    original_amount = sum(item['price'] * item['quantity'] for item in cart)
    final_amount = original_amount
    discount_code_id = None
    
    # 校验库存与商品状态
    for cart_item in cart:
        product = Product.query.get(cart_item['product_id'])
        if not product or not product.is_active:
            return jsonify({'success': False, 'message': '购物车中包含已下架商品'})
        if get_available_stock(product.id) < cart_item['quantity']:
            return jsonify({'success': False, 'message': f'商品 {product.name} 库存不足'})
    
    if discount_code_str:
        discount_code = DiscountCode.query.filter_by(code=discount_code_str, is_active=True).first()
        if not discount_code:
            return jsonify({'success': False, 'message': '折扣码无效'})
        if discount_code:
            if discount_code.valid_from and discount_code.valid_from > datetime.utcnow():
                return jsonify({'success': False, 'message': '折扣码未到生效时间'})
            if discount_code.valid_to and discount_code.valid_to < datetime.utcnow():
                return jsonify({'success': False, 'message': '折扣码已过期'})
            if discount_code.max_uses and discount_code.used_count >= discount_code.max_uses:
                return jsonify({'success': False, 'message': '折扣码使用次数已达上限'})
            if original_amount < discount_code.min_order_amount:
                return jsonify({'success': False, 'message': f'订单金额需达到¥{discount_code.min_order_amount}才能使用此折扣码'})
            if discount_code.type == 'percentage':
                discount_amount = original_amount * (discount_code.value / 100)
            else:
                discount_amount = discount_code.value
            final_amount = max(0, original_amount - discount_amount)
            discount_code_id = discount_code.id
            discount_code.used_count += 1
    
    order_no = generate_order_no()
    while Order_Core.query.filter_by(order_no=order_no).first():
        order_no = generate_order_no()

    order = Order_Core(
        user_id=current_user.id,
        order_no=order_no,
        discount_code_id=discount_code_id,
        original_amount=original_amount,
        final_amount=final_amount,
        cached_status='pending_payment'
    )
    
    db.session.add(order)
    db.session.commit()
    
    items_data = []
    for cart_item in cart:
        product = Product.query.get(cart_item['product_id'])
        if product:
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=cart_item['quantity'],
                price=product.price
            )
            db.session.add(order_item)
            
            items_data.append({
                'product_id': product.id,
                'name': product.name,
                'quantity': cart_item['quantity'],
                'price': product.price
            })
            
            product.sold_count += cart_item['quantity']
    
    db.session.commit()
    
    customer_info = {
        'name': name,
        'phone': phone,
        'email': email,
        'address': address,
        'payment_method': payment_method
    }
    order_state_manager.create_initial_state(order.id, current_user.id, items_data, customer=customer_info, order_no=order.order_no)
    
    save_cart([])
    
    return jsonify({
        'success': True,
        'order_id': order.id,
        'order_no': order.order_no,
        'message': '订单创建成功'
    })

@order_bp.route('/detail/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order_Core.query.get_or_404(order_id)
    
    if order.user_id != current_user.id and current_user.role not in ['admin', 'moderator']:
        flash('无权访问此订单', 'danger')
        return redirect(url_for('index'))
    
    order_state = order_state_manager.get_order_state(order_id)
    
    return render_template('order/order_detail.html', order=order, order_state=order_state)

@order_bp.route('/pay/<int:order_id>', methods=['POST'])
@login_required
def pay_order(order_id):
    order = Order_Core.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作此订单'})
    
    if order.cached_status != 'pending_payment':
        return jsonify({'success': False, 'message': '订单状态不允许支付'})
    
    order_state_manager.update_state(order_id, 'user_paid', '用户已支付')
    order.cached_status = 'user_paid'
    db.session.commit()
    
    return jsonify({'success': True, 'message': '支付成功'})

@order_bp.route('/confirm/<int:order_id>', methods=['POST'])
@login_required
def confirm_receipt(order_id):
    order = Order_Core.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作此订单'})

    if order.cached_status != 'shipped':
        return jsonify({'success': False, 'message': '订单状态不允许确认收货'})

    order_state_manager.update_state(order_id, 'completed', '用户确认收货')
    order.cached_status = 'completed'
    db.session.commit()

    invite_relation = InviteRelation.query.filter_by(invitee_id=order.user_id).first()
    if invite_relation:
        try:
            affiliate_calculator.create_earning_record(invite_relation.inviter_id, order.id, order.final_amount)
        except Exception:
            return jsonify({'success': True, 'message': '订单已完成，收益结算稍后处理'})

    return jsonify({'success': True, 'message': '订单已完成'})

@order_bp.route('/ack/<int:order_id>', methods=['POST'])
@login_required
def acknowledge_rejected(order_id):
    order = Order_Core.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作此订单'})

    if order.cached_status != 'rejected':
        return jsonify({'success': False, 'message': '订单状态不允许确认已知晓'})

    order_state_manager.update_state(order_id, 'rejected', '用户已知晓拒绝')
    order.cached_status = 'rejected'
    db.session.commit()

    return jsonify({'success': True, 'message': '已知晓'})
