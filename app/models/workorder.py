from datetime import datetime
from app import db


class WorkOrder(db.Model):
    __tablename__ = 'workorders'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False, comment='install/maintenance/inspection/fault')
    status = db.Column(db.String(20), default='pending', index=True, comment='pending/processing/completed/cancelled')
    priority = db.Column(db.String(20), default='normal', comment='low/normal/high/urgent')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    point_id = db.Column(db.Integer, db.ForeignKey('points.id'), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    description = db.Column(db.Text)
    result = db.Column(db.Text)
    plan_start = db.Column(db.DateTime)
    plan_end = db.Column(db.DateTime)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship('Project', back_populates='workorders')
    point = db.relationship('Point', back_populates='workorders')
    creator = db.relationship('User', foreign_keys=[created_by], back_populates='created_workorders')
    assignee = db.relationship('User', foreign_keys=[assigned_to], back_populates='assigned_workorders')
    logs = db.relationship('WorkOrderLog', back_populates='workorder', lazy='dynamic', cascade='all, delete-orphan')
    material_usages = db.relationship('MaterialOutbound', back_populates='workorder', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'status': self.status,
            'priority': self.priority,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'point_id': self.point_id,
            'point_name': self.point.name if self.point else None,
            'created_by': self.created_by,
            'creator_name': self.creator.nickname if self.creator else None,
            'assigned_to': self.assigned_to,
            'assignee_name': self.assignee.nickname if self.assignee else None,
            'description': self.description,
            'result': self.result,
            'plan_start': self.plan_start.isoformat() if self.plan_start else None,
            'plan_end': self.plan_end.isoformat() if self.plan_end else None,
            'actual_start': self.actual_start.isoformat() if self.actual_start else None,
            'actual_end': self.actual_end.isoformat() if self.actual_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_brief_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'status': self.status,
            'priority': self.priority,
            'project_name': self.project.name if self.project else None,
            'assignee_name': self.assignee.nickname if self.assignee else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_detail_dict(self):
        data = self.to_dict()
        data['logs'] = [log.to_dict() for log in self.logs.order_by(db.asc('created_at')).all()]
        return data


class WorkOrderLog(db.Model):
    __tablename__ = 'workorder_logs'

    id = db.Column(db.Integer, primary_key=True)
    workorder_id = db.Column(db.Integer, db.ForeignKey('workorders.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    workorder = db.relationship('WorkOrder', back_populates='logs')
    user = db.relationship('User', back_populates='workorder_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'workorder_id': self.workorder_id,
            'user_id': self.user_id,
            'user_name': self.user.nickname if self.user else None,
            'action': self.action,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
