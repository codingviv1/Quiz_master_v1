from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard' if not current_user.is_admin else 'admin.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard' if not current_user.is_admin else 'admin.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user:
            if user.is_locked:
                flash('Account is locked due to too many failed attempts. Please contact an administrator.', 'danger')
                return render_template('auth/login.html')
                
            if user.check_password(password):
                login_user(user)
                user.update_login_timestamp()
                flash(f'Welcome back, {user.full_name}!', 'success')
                return redirect(url_for('user.dashboard' if not user.is_admin else 'admin.dashboard'))
            else:
                user.increment_login_attempt()
                if user.is_locked:
                    flash('Account locked due to too many failed login attempts. Please contact an administrator.', 'danger')
                else:
                    flash('Invalid email or password', 'danger')
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            email=email,
            full_name=full_name,
            qualification=qualification,
            date_of_birth=date_of_birth
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/unlock_account/<int:user_id>', methods=['POST'])
@login_required
def unlock_account(user_id):
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('auth.login'))
        
    user = User.query.get_or_404(user_id)
    user.unlock_account()
    flash(f'Account for {user.email} has been unlocked', 'success')
    return redirect(url_for('admin.manage_users')) 