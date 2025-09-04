from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey

# Association table for group membership
group_members = Table('group_members', db.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('distribution_group.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100))
    location = db.Column(db.String(100))
    role = db.Column(db.String(100))
    manager = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    can_manage_groups = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Many-to-many relationship with groups
    groups = db.relationship('DistributionGroup', secondary=group_members, 
                           back_populates='members')

class DistributionGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    email = db.Column(db.String(120), unique=True, nullable=False)
    group_type = db.Column(db.String(50), default='Distribution')  # Distribution, Security, etc.
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    members = db.relationship('User', secondary=group_members, 
                            back_populates='groups')

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_type = db.Column(db.String(50), nullable=False)  # 'full_admin', 'group_manager', 'user_editor'
    scope = db.Column(db.String(100))  # Optional scope for permissions
    granted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id])
    granted_by = db.relationship('User', foreign_keys=[granted_by_id])

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))  # 'user', 'group', 'permission'
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    
    user = db.relationship('User')
