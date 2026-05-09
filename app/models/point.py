from datetime import datetime
from app import db


class Point(db.Model):
    __tablename__ = 'points'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), index=True)
    address = db.Column(db.String(500))
    latitude = db.Column(db.Numeric(10, 6))
    longitude = db.Column(db.Numeric(10, 6))
    device_type = db.Column(db.String(50))
    device_model = db.Column(db.String(100))
    device_sn = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active', index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship('Project', back_populates='points')
    workorders = db.relationship('WorkOrder', back_populates='point', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'name': self.name,
            'code': self.code,
            'address': self.address,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'device_type': self.device_type,
            'device_model': self.device_model,
            'device_sn': self.device_sn,
            'ip_address': self.ip_address,
            'status': self.status,
            'description': self.description,
            'workorders_count': self.workorders.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
