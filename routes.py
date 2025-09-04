from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from models import User, DistributionGroup, Permission, AuditLog
from app import db
from auth import require_permission
from utils import log_audit_event, generate_pdf_report
from datetime import datetime, timedelta
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get dashboard statistics
    total_users = User.query.filter_by(active=True).count()
    total_groups = DistributionGroup.query.filter_by(active=True).count()
    user_groups = len(current_user.groups) if current_user.groups else 0
    
    # Recent activity
    recent_logs = AuditLog.query.filter_by(user_id=current_user.id)\
                              .order_by(AuditLog.timestamp.desc())\
                              .limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_groups': total_groups,
        'user_groups': user_groups,
        'recent_logs': recent_logs
    }
    
    return render_template('dashboard.html', stats=stats)

@main_bp.route('/groups')
@login_required
def groups():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = DistributionGroup.query.filter_by(active=True)
    
    if search:
        query = query.filter(
            DistributionGroup.name.contains(search) |
            DistributionGroup.description.contains(search)
        )
    
    groups = query.order_by(DistributionGroup.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('groups.html', groups=groups, search=search)

@main_bp.route('/groups/<int:group_id>')
@login_required
def group_detail(group_id):
    group = DistributionGroup.query.get_or_404(group_id)
    members = group.members
    
    # Check if user can manage this group
    can_manage = (current_user.is_admin or current_user.can_manage_groups or
                  group.created_by_id == current_user.id)
    
    return render_template('group_detail.html', group=group, members=members, can_manage=can_manage)

@main_bp.route('/groups/<int:group_id>/add_member', methods=['POST'])
@login_required
@require_permission('manage_groups')
def add_group_member(group_id):
    group = DistributionGroup.query.get_or_404(group_id)
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('Please select a user to add.', 'error')
        return redirect(url_for('main.group_detail', group_id=group_id))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.group_detail', group_id=group_id))
    
    if user in group.members:
        flash(f'{user.display_name} is already a member of this group.', 'warning')
    else:
        group.members.append(user)
        db.session.commit()
        
        log_audit_event(current_user.id, 'add_group_member', 'group', group.id,
                       f'Added user {user.display_name} to group {group.name}')
        
        flash(f'{user.display_name} has been added to the group.', 'success')
    
    return redirect(url_for('main.group_detail', group_id=group_id))

@main_bp.route('/groups/<int:group_id>/remove_member', methods=['POST'])
@login_required
@require_permission('manage_groups')
def remove_group_member(group_id):
    group = DistributionGroup.query.get_or_404(group_id)
    user_id = request.form.get('user_id')
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.group_detail', group_id=group_id))
    
    if user in group.members:
        group.members.remove(user)
        db.session.commit()
        
        log_audit_event(current_user.id, 'remove_group_member', 'group', group.id,
                       f'Removed user {user.display_name} from group {group.name}')
        
        flash(f'{user.display_name} has been removed from the group.', 'success')
    else:
        flash(f'{user.display_name} is not a member of this group.', 'warning')
    
    return redirect(url_for('main.group_detail', group_id=group_id))

@main_bp.route('/users')
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    
    query = User.query.filter_by(active=True)
    
    if search:
        query = query.filter(
            User.display_name.contains(search) |
            User.email.contains(search) |
            User.username.contains(search)
        )
    
    if department:
        query = query.filter_by(department=department)
    
    users = query.order_by(User.display_name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get unique departments for filter
    departments = db.session.query(User.department).distinct().filter(
        User.department.isnot(None), User.active == True
    ).all()
    departments = [d[0] for d in departments if d[0]]
    
    return render_template('users.html', users=users, search=search, 
                         selected_department=department, departments=departments)

@main_bp.route('/users/<int:user_id>')
@login_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    
    # Check if current user can edit this user's information
    can_edit = (current_user.is_admin or current_user.can_manage_groups or
                current_user.id == user.id)
    
    return render_template('user_detail.html', user=user, can_edit=can_edit)

@main_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Permission check
    can_edit_all = current_user.is_admin or current_user.can_manage_groups
    can_edit_basic = current_user.id == user.id
    
    if not (can_edit_all or can_edit_basic):
        flash('You do not have permission to edit this user.', 'error')
        return redirect(url_for('main.user_detail', user_id=user_id))
    
    if request.method == 'POST':
        # Basic fields that users can edit themselves
        if can_edit_basic or can_edit_all:
            user.phone = request.form.get('phone', '').strip()
        
        # Administrative fields
        if can_edit_all:
            user.display_name = request.form.get('display_name', '').strip()
            user.location = request.form.get('location', '').strip()
            user.role = request.form.get('role', '').strip()
            user.manager = request.form.get('manager', '').strip()
            user.department = request.form.get('department', '').strip()
        
        db.session.commit()
        
        log_audit_event(current_user.id, 'edit_user', 'user', user.id,
                       f'Updated user information for {user.display_name}')
        
        flash('User information updated successfully.', 'success')
        return redirect(url_for('main.user_detail', user_id=user_id))
    
    return render_template('edit_user.html', user=user, can_edit_all=can_edit_all)

@main_bp.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@main_bp.route('/reports/group_membership')
@login_required
def group_membership_report():
    group_id = request.args.get('group_id')
    format_type = request.args.get('format', 'html')
    
    if group_id:
        group = DistributionGroup.query.get_or_404(group_id)
        members = group.members
        
        if format_type == 'pdf':
            pdf_data = generate_pdf_report('Group Membership Report', group, members)
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=group_report_{group.name}.pdf'
            return response
        
        return render_template('group_report.html', group=group, members=members)
    
    groups = DistributionGroup.query.filter_by(active=True).order_by(DistributionGroup.name).all()
    return render_template('select_group_report.html', groups=groups)

@main_bp.route('/admin')
@login_required
@require_permission('full_admin')
def admin():
    # Administrative statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(active=True).count()
    total_groups = DistributionGroup.query.count()
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_groups': total_groups,
        'recent_activity': recent_activity
    }
    
    return render_template('admin.html', stats=stats)

@main_bp.route('/admin/create_group', methods=['POST'])
@login_required
@require_permission('manage_groups')
def create_group():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    email = request.form.get('email', '').strip()
    
    if not name or not email:
        flash('Group name and email are required.', 'error')
        return redirect(url_for('main.groups'))
    
    # Check if group already exists
    existing_group = DistributionGroup.query.filter_by(name=name).first()
    if existing_group:
        flash('A group with this name already exists.', 'error')
        return redirect(url_for('main.groups'))
    
    existing_email = DistributionGroup.query.filter_by(email=email).first()
    if existing_email:
        flash('A group with this email already exists.', 'error')
        return redirect(url_for('main.groups'))
    
    group = DistributionGroup(
        name=name,
        description=description,
        email=email,
        created_by_id=current_user.id
    )
    
    db.session.add(group)
    db.session.commit()
    
    log_audit_event(current_user.id, 'create_group', 'group', group.id,
                   f'Created new group: {group.name}')
    
    flash(f'Group "{name}" has been created successfully.', 'success')
    return redirect(url_for('main.groups'))

@main_bp.route('/api/users/search')
@login_required
def search_users_api():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    users = User.query.filter(
        User.active == True,
        (User.display_name.contains(query) | User.email.contains(query))
    ).limit(10).all()
    
    results = [{
        'id': user.id,
        'display_name': user.display_name,
        'email': user.email,
        'department': user.department
    } for user in users]
    
    return jsonify(results)
