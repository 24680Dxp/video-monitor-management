from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api_bp
from app import db
from app.models.material import Material, MaterialInbound, MaterialOutbound


@api_bp.route('/materials', methods=['GET'])
@jwt_required()
def get_materials():
    """获取物资列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    keyword = request.args.get('keyword', '')

    query = Material.query

    if category:
        query = query.filter(Material.category == category)
    if status:
        query = query.filter(Material.status == status)
    if keyword:
        query = query.filter(
            db.or_(
                Material.name.like(f'%{keyword}%'),
                Material.code.like(f'%{keyword}%'),
                Material.spec.like(f'%{keyword}%')
            )
        )

    pagination = query.order_by(Material.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'data': {
            'items': [m.to_dict() for m in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }), 200


@api_bp.route('/materials', methods=['POST'])
@jwt_required()
def create_material():
    """创建新物资"""
    data = request.get_json()

    if not data or not data.get('name') or not data.get('code'):
        return jsonify({'success': False, 'message': '请提供物资名称和物资编码'}), 400

    if Material.query.filter_by(code=data['code']).first():
        return jsonify({'success': False, 'message': '物资编码已存在'}), 400

    material = Material(
        name=data['name'],
        code=data['code'],
        category=data.get('category'),
        spec=data.get('spec'),
        unit=data.get('unit', '个'),
        price=data.get('price', 0.00),
        low_stock_threshold=data.get('low_stock_threshold', 10),
        current_stock=data.get('current_stock', 0),
        status=data.get('status', 'active')
    )

    db.session.add(material)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '物资创建成功',
        'data': material.to_dict()
    }), 201


@api_bp.route('/materials/<int:material_id>', methods=['GET'])
@jwt_required()
def get_material(material_id):
    """获取物资详情"""
    material = Material.query.get(material_id)

    if not material:
        return jsonify({'success': False, 'message': '物资不存在'}), 404

    return jsonify({
        'success': True,
        'data': material.to_dict()
    }), 200


@api_bp.route('/materials/<int:material_id>', methods=['PUT'])
@jwt_required()
def update_material(material_id):
    """更新物资信息"""
    material = Material.query.get(material_id)

    if not material:
        return jsonify({'success': False, 'message': '物资不存在'}), 404

    data = request.get_json()

    if 'name' in data:
        material.name = data['name']
    if 'code' in data:
        if data['code'] != material.code and Material.query.filter_by(code=data['code']).first():
            return jsonify({'success': False, 'message': '物资编码已存在'}), 400
        material.code = data['code']
    if 'category' in data:
        material.category = data['category']
    if 'spec' in data:
        material.spec = data['spec']
    if 'unit' in data:
        material.unit = data['unit']
    if 'price' in data:
        material.price = data['price']
    if 'low_stock_threshold' in data:
        material.low_stock_threshold = data['low_stock_threshold']
    if 'status' in data:
        material.status = data['status']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': material.to_dict()
    }), 200


@api_bp.route('/materials/<int:material_id>', methods=['DELETE'])
@jwt_required()
def delete_material(material_id):
    """删除物资"""
    material = Material.query.get(material_id)

    if not material:
        return jsonify({'success': False, 'message': '物资不存在'}), 404

    db.session.delete(material)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '删除成功'
    }), 200


@api_bp.route('/materials/inbound', methods=['POST'])
@jwt_required()
def inbound_material():
    """物资入库"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('material_id') or not data.get('quantity'):
        return jsonify({'success': False, 'message': '请提供物资ID和数量'}), 400

    material = Material.query.get(data['material_id'])
    if not material:
        return jsonify({'success': False, 'message': '物资不存在'}), 404

    quantity = int(data['quantity'])
    if quantity <= 0:
        return jsonify({'success': False, 'message': '数量必须大于0'}), 400

    inbound = MaterialInbound(
        material_id=data['material_id'],
        quantity=quantity,
        batch_no=data.get('batch_no'),
        supplier=data.get('supplier'),
        remark=data.get('remark'),
        operator_id=user_id
    )

    material.current_stock += quantity

    db.session.add(inbound)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '入库成功',
        'data': {
            'inbound': inbound.to_dict(),
            'material': material.to_dict()
        }
    }), 201


@api_bp.route('/materials/inbounds', methods=['GET'])
@jwt_required()
def get_inbounds():
    """获取入库记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    material_id = request.args.get('material_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = MaterialInbound.query

    if material_id:
        query = query.filter(MaterialInbound.material_id == material_id)
    if start_date:
        query = query.filter(MaterialInbound.inbound_at >= start_date)
    if end_date:
        query = query.filter(MaterialInbound.inbound_at <= end_date)

    pagination = query.order_by(MaterialInbound.inbound_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'data': {
            'items': [i.to_dict() for i in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }), 200


@api_bp.route('/materials/outbound', methods=['POST'])
@jwt_required()
def outbound_material():
    """物资出库"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('material_id') or not data.get('quantity'):
        return jsonify({'success': False, 'message': '请提供物资ID和数量'}), 400

    material = Material.query.get(data['material_id'])
    if not material:
        return jsonify({'success': False, 'message': '物资不存在'}), 404

    quantity = int(data['quantity'])
    if quantity <= 0:
        return jsonify({'success': False, 'message': '数量必须大于0'}), 400

    if material.current_stock < quantity:
        return jsonify({'success': False, 'message': f'库存不足，当前库存：{material.current_stock}'}), 400

    outbound = MaterialOutbound(
        material_id=data['material_id'],
        quantity=quantity,
        workorder_id=data.get('workorder_id'),
        reason=data.get('reason'),
        operator_id=user_id
    )

    material.current_stock -= quantity

    db.session.add(outbound)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '出库成功',
        'data': {
            'outbound': outbound.to_dict(),
            'material': material.to_dict()
        }
    }), 201


@api_bp.route('/materials/outbounds', methods=['GET'])
@jwt_required()
def get_outbounds():
    """获取出库记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    material_id = request.args.get('material_id', type=int)
    workorder_id = request.args.get('workorder_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = MaterialOutbound.query

    if material_id:
        query = query.filter(MaterialOutbound.material_id == material_id)
    if workorder_id:
        query = query.filter(MaterialOutbound.workorder_id == workorder_id)
    if start_date:
        query = query.filter(MaterialOutbound.outbound_at >= start_date)
    if end_date:
        query = query.filter(MaterialOutbound.outbound_at <= end_date)

    pagination = query.order_by(MaterialOutbound.outbound_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'data': {
            'items': [o.to_dict() for o in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }), 200


@api_bp.route('/materials/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    """查询库存"""
    category = request.args.get('category')
    low_stock_only = request.args.get('low_stock', 'false').lower() == 'true'

    query = Material.query.filter_by(status='active')

    if category:
        query = query.filter(Material.category == category)

    if low_stock_only:
        query = query.filter(Material.current_stock <= Material.low_stock_threshold)

    materials = query.all()

    total_value = sum(float(m.price) * m.current_stock for m in materials)

    return jsonify({
        'success': True,
        'data': {
            'items': [m.to_dict() for m in materials],
            'total_count': len(materials),
            'total_value': total_value
        }
    }), 200


@api_bp.route('/materials/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock():
    """获取低库存预警物资"""
    materials = Material.query.filter(
        Material.status == 'active',
        Material.current_stock <= Material.low_stock_threshold
    ).all()

    return jsonify({
        'success': True,
        'data': [m.to_dict() for m in materials]
    }), 200


@api_bp.route('/materials/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取物资分类列表"""
    categories = db.session.query(Material.category).distinct().filter(
        Material.category.isnot(None)
    ).all()

    return jsonify({
        'success': True,
        'data': [c[0] for c in categories if c[0]]
    }), 200
