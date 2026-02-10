from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import login_required, current_user
from app.user import user_bp
from app.models import User, Order_Core, InviteRelation, EarningRecord, WithdrawalRequest
from app.extensions import db, bcrypt
from app.utils.image_processor import ImageProcessor
from app.utils.pagination import paginate
from datetime import datetime

@user_bp.route('/profile')
@login_required
def profile():
    return redirect(url_for('user.profile_edit'))

@user_bp.route('/profile/edit')
@login_required
def profile_edit():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    display_name = request.form.get('display_name')
    email = request.form.get('email')
    contact = request.form.get('contact')
    invite_code = request.form.get('invite_code')
    avatar = request.files.get('avatar')
    
    if display_name:
        current_user.display_name = display_name
    
    if email and email != current_user.email:
        if User.query.filter_by(email=email).first():
            flash('邮箱已被使用', 'danger')
            return redirect(url_for('user.profile'))
        current_user.email = email
    
    if contact:
        current_user.contact = contact

    if invite_code and invite_code != current_user.invite_code:
        if User.query.filter_by(invite_code=invite_code).first():
            flash('邀请码已被使用', 'danger')
            return redirect(url_for('user.profile_edit'))
        current_user.invite_code = invite_code
    
    if avatar:
        image_processor = ImageProcessor(current_app.config['UPLOAD_FOLDER'])
        avatar_filename = image_processor.process_uploaded_image(avatar, 'avatars')
        if avatar_filename:
            current_user.avatar_filename = avatar_filename
    
    db.session.commit()
    flash('个人资料已更新', 'success')
    return redirect(url_for('user.profile'))

@user_bp.route('/password/change', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('请填写所有字段', 'danger')
        return redirect(url_for('user.settings'))
    
    if not bcrypt.check_password_hash(current_user.password_hash, current_password):
        flash('当前密码错误', 'danger')
        return redirect(url_for('user.settings'))
    
    if new_password != confirm_password:
        flash('两次输入的新密码不一致', 'danger')
        return redirect(url_for('user.settings'))
    
    if len(new_password) < 6:
        flash('新密码至少需要6个字符', 'danger')
        return redirect(url_for('user.settings'))
    
    current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    flash('密码已修改', 'success')
    return redirect(url_for('user.settings'))

@user_bp.route('/orders')
@login_required
def order_history():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = Order_Core.query.filter_by(user_id=current_user.id)
    
    if status:
        query = query.filter_by(cached_status=status)
    
    query = query.order_by(Order_Core.created_at.desc())
    pagination = paginate(query, page=page, per_page=10)
    
    return render_template('user/order_history.html', pagination=pagination, status=status)

@user_bp.route('/invite')
@login_required
def invite_management():
    invite_relations = InviteRelation.query.filter_by(inviter_id=current_user.id).all()
    
    invitees = []
    for relation in invite_relations:
        invitee = User.query.get(relation.invitee_id)
        if invitee:
            invitees.append({
                'username': invitee.username,
                'display_name': invitee.display_name,
                'created_at': relation.created_at
            })
    
    invite_link = f"{request.host_url}auth/register?invite_code={current_user.invite_code}"
    
    return render_template('user/invite_management.html', 
                           invitees=invitees,
                           invite_link=invite_link,
                           invite_code=current_user.invite_code)

@user_bp.route('/earnings')
@login_required
def earnings():
    page = request.args.get('page', 1, type=int)
    
    query = EarningRecord.query.filter_by(user_id=current_user.id).order_by(EarningRecord.created_at.desc())
    pagination = paginate(query, page=page, per_page=20)
    
    total_earned = current_user.total_earned
    balance_available = current_user.balance_available
    balance_pending = current_user.balance_pending
    
    return render_template('user/earnings.html',
                           pagination=pagination,
                           total_earned=total_earned,
                           balance_available=balance_available,
                           balance_pending=balance_pending)

@user_bp.route('/withdrawal')
@login_required
def withdrawal():
    page = request.args.get('page', 1, type=int)
    
    query = WithdrawalRequest.query.filter_by(user_id=current_user.id).order_by(WithdrawalRequest.created_at.desc())
    pagination = paginate(query, page=page, per_page=10)
    
    return render_template('user/withdrawal.html', 
                           pagination=pagination,
                           min_withdrawal_amount=current_app.config['MIN_WITHDRAWAL_AMOUNT'])

@user_bp.route('/withdrawal/request', methods=['POST'])
@login_required
def request_withdrawal():
    amount_raw = request.form.get('amount')
    try:
        amount = float(amount_raw) if amount_raw else 0.0
    except ValueError:
        amount = 0.0
    
    if not amount or amount <= 0:
        flash('请输入有效的提现金额', 'danger')
        return redirect(url_for('user.withdrawal'))
    
    if amount < current_app.config['MIN_WITHDRAWAL_AMOUNT']:
        flash(f'最低提现金额为¥{current_app.config["MIN_WITHDRAWAL_AMOUNT"]}', 'danger')
        return redirect(url_for('user.withdrawal'))
    
    if amount > current_user.balance_available:
        flash('可提现余额不足', 'danger')
        return redirect(url_for('user.withdrawal'))
    
    withdrawal_request = WithdrawalRequest(
        user_id=current_user.id,
        amount=amount,
        status='submitted'
    )
    
    db.session.add(withdrawal_request)
    db.session.commit()
    
    flash('提现申请已提交，请等待审核', 'success')
    return redirect(url_for('user.withdrawal'))

@user_bp.route('/settings')
@login_required
def settings():
    return render_template('user/settings.html')
