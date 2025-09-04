import os
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, Permission, AuditLog
from app import db
from utils import log_audit_event
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def simulate_windows_auth(username, password):
    """
    Simulate Windows authentication. In production, this would integrate
    with actual Windows authentication (LDAP, Kerberos, etc.)
    """
    # For demonstration, create some default users if they don't exist
    default_users = [
        {'username': 'admin', 'email': 'admin@company.com', 'display_name': 'System Administrator', 
         'department': 'IT', 'is_admin': True, 'can_manage_groups': True, 'password': 'admin123'},
        {'username': 'hr.manager', 'email': 'hr.manager@company.com', 'display_name': 'HR Manager',
         'department': 'Human Resources', 'can_manage_groups': True, 'password': 'hr123'},
        {'username': 'gp.user', 'email': 'gp.user@company.com', 'display_name': 'GP User',
         'department': 'General Practice', 'can_manage_groups': False, 'password': 'gp123'},
        {'username': 'comm.user', 'email': 'comm.user@company.com', 'display_name': 'Communications User',
         'department': 'Communications', 'can_manage_groups': False, 'password': 'comm123'}
    ]
    
    for user_data in default_users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                display_name=user_data['display_name'],
                department=user_data['department'],
                is_admin=user_data.get('is_admin', False),
                can_manage_groups=user_data.get('can_manage_groups', False)
            )
            db.session.add(user)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # Simulate authentication check
    user = User.query.filter_by(username=username).first()
    if user:
        # In production, this would verify against Windows credentials
        for default_user in default_users:
            if default_user['username'] == username and default_user['password'] == password:
                return user
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        # Authenticate user
        user = simulate_windows_auth(username, password)
        
        if user:
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_audit_event(user.id, 'login', 'user', user.id, 'User logged in successfully')
            
            flash(f'Welcome back, {user.display_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            log_audit_event(None, 'login_failed', 'user', None, f'Failed login attempt for username: {username}')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    log_audit_event(user_id, 'logout', 'user', user_id, 'User logged out')
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

def require_permission(permission_type):
    """Decorator to check if user has specific permission"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.is_admin:
                return f(*args, **kwargs)
            
            if permission_type == 'manage_groups' and current_user.can_manage_groups:
                return f(*args, **kwargs)
            
            # Check specific permissions
            permission = Permission.query.filter_by(
                user_id=current_user.id,
                permission_type=permission_type
            ).first()
            
            if permission:
                return f(*args, **kwargs)
            
            flash('You do not have permission to access this resource.', 'error')
            return redirect(url_for('main.dashboard'))
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator
