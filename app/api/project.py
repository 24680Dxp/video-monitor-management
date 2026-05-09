from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api_bp
from app import db
from app.models.project import Project
from app.models.point import Point


@api_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """获取项目列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    industry = request.args.get('industry')
    keyword = request.args.get('keyword', '')

    query = Project.query

    if status:
        query = query.filter(Project.status == status)
    if industry:
        query = query.filter(Project.industry == industry)
    if keyword:
        query = query.filter(
            db.or_(
                Project.name.like(f'%{keyword}%'),
                Project.code.like(f'%{keyword}%'),
                Project.customer.like(f'%{keyword}%')
            )
        )

    pagination = query.order_by(Project.created_at.desc()).paginate(
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


@api_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """创建新项目"""
    data = request.get_json()

    if not data or not data.get('name') or not data.get('code'):
        return jsonify({'success': False, 'message': '请提供项目名称和项目代码'}), 400

    if Project.query.filter_by(code=data['code']).first():
        return jsonify({'success': False, 'message': '项目代码已存在'}), 400

    project = Project(
        name=data['name'],
        code=data['code'],
        customer=data.get('customer'),
        address=data.get('address'),
        industry=data.get('industry'),
        status=data.get('status', 'active'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        description=data.get('description')
    )

    db.session.add(project)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '项目创建成功',
        'data': project.to_dict()
    }), 201


@api_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """获取项目详情"""
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    return jsonify({
        'success': True,
        'data': project.to_detail_dict()
    }), 200


@api_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """更新项目信息"""
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    data = request.get_json()

    if 'name' in data:
        project.name = data['name']
    if 'code' in data:
        if data['code'] != project.code and Project.query.filter_by(code=data['code']).first():
            return jsonify({'success': False, 'message': '项目代码已存在'}), 400
        project.code = data['code']
    if 'customer' in data:
        project.customer = data['customer']
    if 'address' in data:
        project.address = data['address']
    if 'industry' in data:
        project.industry = data['industry']
    if 'status' in data:
        project.status = data['status']
    if 'start_date' in data:
        project.start_date = data['start_date']
    if 'end_date' in data:
        project.end_date = data['end_date']
    if 'description' in data:
        project.description = data['description']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': project.to_dict()
    }), 200


@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """删除项目"""
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '删除成功'
    }), 200


@api_bp.route('/projects/<int:project_id>/points', methods=['GET'])
@jwt_required()
def get_project_points(project_id):
    """获取项目下的点位列表"""
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status = request.args.get('status')

    query = Point.query.filter_by(project_id=project_id)

    if status:
        query = query.filter(Point.status == status)

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


@api_bp.route('/projects/<int:project_id>/workorders', methods=['GET'])
@jwt_required()
def get_project_workorders(project_id):
    """获取项目下的工单列表"""
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    from app.models.workorder import WorkOrder

    pagination = WorkOrder.query.filter_by(project_id=project_id).order_by(
        WorkOrder.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'data': {
            'items': [wo.to_brief_dict() for wo in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }), 200


@api_bp.route('/projects/<int:project_id>/stats', methods=['GET'])
@jwt_required()
def get_project_stats(project_id):
    """获取项目统计数据"""
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    from app.models.workorder import WorkOrder
    from app.models.point import Point

    total_workorders = WorkOrder.query.filter_by(project_id=project_id).count()
    pending_workorders = WorkOrder.query.filter_by(project_id=project_id, status='pending').count()
    processing_workorders = WorkOrder.query.filter_by(project_id=project_id, status='processing').count()
    completed_workorders = WorkOrder.query.filter_by(project_id=project_id, status='completed').count()

    total_points = Point.query.filter_by(project_id=project_id).count()
    active_points = Point.query.filter_by(project_id=project_id, status='active').count()

    return jsonify({
        'success': True,
        'data': {
            'project_id': project_id,
            'project_name': project.name,
            'workorders': {
                'total': total_workorders,
                'pending': pending_workorders,
                'processing': processing_workorders,
                'completed': completed_workorders,
                'completion_rate': round(completed_workorders / total_workorders * 100, 2) if total_workorders > 0 else 0
            },
            'points': {
                'total': total_points,
                'active': active_points
            }
        }
    }), 200
