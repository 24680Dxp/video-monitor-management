from datetime import datetime
from app import db


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), index=True)
    spec = db.Column(db.String(100))
    unit = db.Column(db.String(20), default='个')
    price = db.Column(db.Numeric(10, 2), default=0.00)
    low_stock_threshold = db.Column(db.Integer, default=10)
    current_stock = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    inbounds = db.relationship('MaterialInbound', back_populates='material', lazy='dynamic')
    outbounds = db.relationship('MaterialOutbound', back_populates='material', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'category': self.category,
            'spec': self.spec,
            'unit': self.unit,
            'price': float(self.price) if self.price else 0.00,
            'low_stock_threshold': self.low_stock_threshold,
            'current_stock': self.current_stock,
            'status': self.status,
            'is_low_stock': self.current_stock <= self.low_stock_threshold,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MaterialInbound(db.Model):
    __tablename__ = 'material_inbounds'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    batch_no = db.Column(db.String(50))
    supplier = db.Column(db.String(100))
    remark = db.Column(db.Text)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    inbound_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    material = db.relationship('Material', back_populates='inbounds')
    operator = db.relationship('User', foreign_keys=[operator_id])

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'material_name': self.material.name if self.material else None,
            'material_code': self.material.code if self.material else None,
            'quantity': self.quantity,
            'batch_no': self.batch_no,
            'supplier': self.supplier,
            'remark': self.remark,
            'operator_id': self.operator_id,
            'operator_name': self.operator.nickname if self.operator else None,
            'inbound_at': self.inbound_at.isoformat() if self.inbound_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MaterialOutbound(db.Model):
    __tablename__ = 'material_outbounds'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    workorder_id = db.Column(db.Integer, db.ForeignKey('workorders.id'), index=True)
    reason = db.Column(db.String(200))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outbound_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    material = db.relationship('Material', back_populates='outbounds')
    workorder = db.relationship('WorkOrder', back_populates='material_usages')
    operator = db.relationship('User', foreign_keys=[operator_id])

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'material_name': self.material.name if self.material else None,
            'material_code': self.material.code if self.material else None,
            'quantity': self.quantity,
            'workorder_id': self.workorder_id,
            'workorder_title': self.workorder.title if self.workorder else None,
            'reason': self.reason,
            'operator_id': self.operator_id,
            'operator_name': self.operator.nickname if self.operator else None,
            'outbound_at': self.outbound_at.isoformat() if self.outbound_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
