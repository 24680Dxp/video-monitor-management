from datetime import datetime
from app import db


class Dict(db.Model):
    __tablename__ = 'dicts'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('category', 'code', name='uk_category_code'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'code': self.code,
            'name': self.name,
            'sort_order': self.sort_order,
            'status': self.status
        }
