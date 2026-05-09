from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api_bp
from app import db
from app.models.point import Point
from app.models.workorder import WorkOrder, WorkOrderLog


@api_bp.route('/points', methods=['GET'])
@jwt_required()
def get_points():
    """获取点位列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status')
    keyword = request.args.get('keyword', '')

    query = Point.query

    if project_id:
        query = query.filter(Point.project_id == project_id)
    if status:
        query = query.filter(Point.status == status)
    if keyword:
        query = query.filter(
            db.or_(
                Point.name.like(f'%{keyword}%'),
                Point.code.like(f'%{keyword}%'),
                Point.address.like(f'%{keyword}%'),
                Point.ip_address.like(f'%{keyword}%')
            )
        )

    pagination = query.order_by(Point.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'data': {
            'items': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }), 200


@api_bp.route('/points/all', methods=['GET'])
@jwt_required()
def get_all_points():
    """获取所有点位（用于地图展示）"""
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status')

    query = Point.query

    if project_id:
        query = query.filter(Point.project_id == project_id)
    if status:
        query = query.filter(Point.status == status)

    query = query.filter(Point.latitude.isnot(None), Point.longitude.isnot(None))

    points = query.all()

    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in points]
    }), 200


@api_bp.route('/points', methods=['POST'])
@jwt_required()
def create_point():
    """创建新点位"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('name') or not data.get('project_id'):
        return jsonify({'success': False, 'message': '请提供点位名称和项目ID'}), 400

    point = Point(
        project_id=data['project_id'],
        name=data['name'],
        code=data.get('code'),
        address=data.get('address'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        device_type=data.get('device_type'),
        device_model=data.get('device_model'),
        device_sn=data.get('device_sn'),
        ip_address=data.get('ip_address'),
        status=data.get('status', 'active'),
        description=data.get('description')
    )

    db.session.add(point)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '点位创建成功',
        'data': point.to_dict()
    }), 201


@api_bp.route('/points/<int:point_id>', methods=['GET'])
@jwt_required()
def get_point(point_id):
    """获取点位详情"""
    point = Point.query.get(point_id)

    if not point:
        return jsonify({'success': False, 'message': '点位不存在'}), 404

    data = point.to_dict()
    data['recent_workorders'] = [
        wo.to_brief_dict() for wo in
        WorkOrder.query.filter_by(point_id=point_id).order_by(db.desc('created_at')).limit(10).all()
    ]

    return jsonify({
        'success': True,
        'data': data
    }), 200


@api_bp.route('/points/<int:point_id>', methods=['PUT'])
@jwt_required()
def update_point(point_id):
    """更新点位信息"""
    point = Point.query.get(point_id)

    if not point:
        return jsonify({'success': False, 'message': '点位不存在'}), 404

    data = request.get_json()

    if 'name' in data:
        point.name = data['name']
    if 'code' in data:
        point.code = data['code']
    if 'address' in data:
        point.address = data['address']
    if 'latitude' in data:
        point.latitude = data['latitude']
    if 'longitude' in data:
        point.longitude = data['longitude']
    if 'device_type' in data:
        point.device_type = data['device_type']
    if 'device_model' in data:
        point.device_model = data['device_model']
    if 'device_sn' in data:
        point.device_sn = data['device_sn']
    if 'ip_address' in data:
        point.ip_address = data['ip_address']
    if 'status' in data:
        point.status = data['status']
    if 'description' in data:
        point.description = data['description']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': point.to_dict()
    }), 200


@api_bp.route('/points/<int:point_id>', methods=['DELETE'])
@jwt_required()
def delete_point(point_id):
    """删除点位"""
    point = Point.query.get(point_id)

    if not point:
        return jsonify({'success': False, 'message': '点位不存在'}), 404

    db.session.delete(point)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '删除成功'
    }), 200


@api_bp.route('/points/<int:point_id>/history', methods=['GET'])
@jwt_required()
def get_point_history(point_id):
    """获取点位维护历史"""
    point = Point.query.get(point_id)

    if not point:
        return jsonify({'success': False, 'message': '点位不存在'}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = WorkOrder.query.filter_by(point_id=point_id).order_by(
        WorkOrder.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'data': {
            'items': [wo.to_dict() for wo in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }), 200


@api_bp.route('/points/<int:point_id>/create-workorder', methods=['POST'])
@jwt_required()
def create_workorder_for_point(point_id):
    """为点位创建工单"""
    user_id = get_jwt_identity()
    point = Point.query.get(point_id)

    if not point:
        return jsonify({'success': False, 'message': '点位不存在'}), 404

    data = request.get_json()

    workorder = WorkOrder(
        title=data.get('title', f'{point.name} - 维护工单'),
        type=data.get('type', 'maintenance'),
        priority=data.get('priority', 'normal'),
        project_id=point.project_id,
        point_id=point_id,
        created_by=user_id,
        assigned_to=data.get('assigned_to'),
        description=data.get('description')
    )

    db.session.add(workorder)
    db.session.flush()

    log = WorkOrderLog(
        workorder_id=workorder.id,
        user_id=user_id,
        action='created',
        content=f'为点位「{point.name}」创建了工单'
    )
    db.session.add(log)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '工单创建成功',
        'data': workorder.to_dict()
    }), 201
