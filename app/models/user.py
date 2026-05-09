from datetime import datetime
from app import db
import bcrypt


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', back_populates='role', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), index=True)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = db.relationship('Role', back_populates='users')
    created_workorders = db.relationship('WorkOrder', foreign_keys='WorkOrder.created_by', back_populates='creator', lazy='dynamic')
    assigned_workorders = db.relationship('WorkOrder', foreign_keys='WorkOrder.assigned_to', back_populates='assignee', lazy='dynamic')
    workorder_logs = db.relationship('WorkOrderLog', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'phone': self.phone,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_brief_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname
        }
