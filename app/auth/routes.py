from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, current_user
from app.auth import auth_bp
from app.models import User
from app.extensions import db, bcrypt

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        
        if not username or not password:
            error = '用户名和密码不能为空'
        else:
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password_hash, password):
                if user.is_active:
                    login_user(user)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('index'))
                else:
                    error = '账户已被禁用'
            else:
                error = '用户名或密码错误'
        
        if error:
            flash(error, 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    invite_code = request.args.get('invite_code')
    
    if request.method == 'POST':
        username = request.form.get('username')
        display_name = request.form.get('display_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        entered_invite_code = request.form.get('invite_code')
        
        error = None
        
        if not all([username, display_name, password, email]):
            error = '请填写所有必填项'
        elif password != confirm_password:
            error = '两次输入的密码不一致'
        elif len(password) < 6:
            error = '密码至少需要6个字符'
        elif User.query.filter_by(username=username).first():
            error = '用户名已存在'
        elif User.query.filter_by(email=email).first():
            error = '邮箱已被使用'
        elif invite_code and entered_invite_code != invite_code:
            error = '邀请码错误'
        elif entered_invite_code and not User.query.filter_by(invite_code=entered_invite_code).first():
            error = '邀请码不存在'
        
        if error:
            flash(error, 'danger')
        else:
            # 创建新用户
            user = User(
                username=username,
                display_name=display_name,
                email=email,
                password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
                role='user',
                is_active=True
            )
            
            db.session.add(user)
            db.session.flush()  # 获取用户ID，但暂不提交
            
            # 如果有邀请码，则建立邀请关系
            if entered_invite_code:
                from app.models import InviteRelation
                inviter = User.query.filter_by(invite_code=entered_invite_code).first()
                if inviter:
                    invite_relation = InviteRelation(
                        inviter_id=inviter.id,
                        invitee_id=user.id
                    )
                    db.session.add(invite_relation)
            
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', invite_code=invite_code)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('index'))
