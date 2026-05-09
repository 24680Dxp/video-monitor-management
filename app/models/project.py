from datetime import datetime
from app import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer = db.Column(db.String(200))
    address = db.Column(db.String(500))
    industry = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active', index=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    points = db.relationship('Point', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')
    workorders = db.relationship('WorkOrder', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'customer': self.customer,
            'address': self.address,
            'industry': self.industry,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'points_count': self.points.count(),
            'workorders_count': self.workorders.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_detail_dict(self):
        data = self.to_dict()
        data['points'] = [p.to_dict() for p in self.points.limit(50).all()]
        data['workorders'] = [w.to_brief_dict() for w in self.workorders.order_by(db.desc('created_at')).limit(20).all()]
        return data
