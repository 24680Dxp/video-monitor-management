from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api_bp
from app import db
from app.models.workorder import WorkOrder, WorkOrderLog
from app.models.user import User
from datetime import datetime


@api_bp.route('/workorders', methods=['GET'])
@jwt_required()
def get_workorders():
    """获取工单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    project_id = request.args.get('project_id', type=int)
    priority = request.args.get('priority')
    type = request.args.get('type')
    assigned_to = request.args.get('assigned_to', type=int)
    keyword = request.args.get('keyword', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = WorkOrder.query

    if status:
        query = query.filter(WorkOrder.status == status)
    if project_id:
        query = query.filter(WorkOrder.project_id == project_id)
    if priority:
        query = query.filter(WorkOrder.priority == priority)
    if type:
        query = query.filter(WorkOrder.type == type)
    if assigned_to:
        query = query.filter(WorkOrder.assigned_to == assigned_to)
    if keyword:
        query = query.filter(
            db.or_(
                WorkOrder.title.like(f'%{keyword}%'),
                WorkOrder.description.like(f'%{keyword}%')
            )
        )
    if start_date:
        query = query.filter(WorkOrder.created_at >= start_date)
    if end_date:
        query = query.filter(WorkOrder.created_at <= end_date)

    pagination = query.order_by(WorkOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

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


@api_bp.route('/workorders', methods=['POST'])
@jwt_required()
def create_workorder():
    """创建新工单"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('title') or not data.get('project_id'):
        return jsonify({'success': False, 'message': '请提供工单标题和项目ID'}), 400

    workorder = WorkOrder(
        title=data['title'],
        type=data.get('type', 'maintenance'),
        priority=data.get('priority', 'normal'),
        project_id=data['project_id'],
        point_id=data.get('point_id'),
        created_by=user_id,
        assigned_to=data.get('assigned_to'),
        description=data.get('description'),
        plan_start=datetime.fromisoformat(data['plan_start']) if data.get('plan_start') else None,
        plan_end=datetime.fromisoformat(data['plan_end']) if data.get('plan_end') else None
    )

    db.session.add(workorder)
    db.session.flush()

    log = WorkOrderLog(
        workorder_id=workorder.id,
        user_id=user_id,
        action='created',
        content=f'创建了工单：{workorder.title}'
    )
    db.session.add(log)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '工单创建成功',
        'data': workorder.to_dict()
    }), 201


@api_bp.route('/workorders/<int:workorder_id>', methods=['GET'])
@jwt_required()
def get_workorder(workorder_id):
    """获取工单详情"""
    workorder = WorkOrder.query.get(workorder_id)

    if not workorder:
        return jsonify({'success': False, 'message': '工单不存在'}), 404

    return jsonify({
        'success': True,
        'data': workorder.to_detail_dict()
    }), 200


@api_bp.route('/workorders/<int:workorder_id>', methods=['PUT'])
@jwt_required()
def update_workorder(workorder_id):
    """更新工单"""
    user_id = get_jwt_identity()
    workorder = WorkOrder.query.get(workorder_id)

    if not workorder:
        return jsonify({'success': False, 'message': '工单不存在'}), 404

    data = request.get_json()
    changes = []

    if 'title' in data and data['title'] != workorder.title:
        changes.append(f'标题: {workorder.title} -> {data["title"]}')
        workorder.title = data['title']

    if 'type' in data and data['type'] != workorder.type:
        changes.append(f'类型: {workorder.type} -> {data["type"]}')
        workorder.type = data['type']

    if 'priority' in data and data['priority'] != workorder.priority:
        changes.append(f'优先级: {workorder.priority} -> {data["priority"]}')
        workorder.priority = data['priority']

    if 'assigned_to' in data and data['assigned_to'] != workorder.assigned_to:
        assignee = User.query.get(data['assigned_to'])
        changes.append(f'指派给: {workorder.assignee.nickname if workorder.assignee else "无"} -> {assignee.nickname if assignee else "无"}')
        workorder.assigned_to = data['assigned_to']

    if 'description' in data:
        workorder.description = data['description']

    if 'result' in data:
        workorder.result = data['result']

    if 'plan_start' in data:
        workorder.plan_start = datetime.fromisoformat(data['plan_start']) if data['plan_start'] else None

    if 'plan_end' in data:
        workorder.plan_end = datetime.fromisoformat(data['plan_end']) if data['plan_end'] else None

    if changes:
        log = WorkOrderLog(
            workorder_id=workorder.id,
            user_id=user_id,
            action='updated',
            content='更新了工单：' + '; '.join(changes)
        )
        db.session.add(log)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': workorder.to_dict()
    }), 200


@api_bp.route('/workorders/<int:workorder_id>', methods=['DELETE'])
@jwt_required()
def delete_workorder(workorder_id):
    """删除工单"""
    user_id = get_jwt_identity()
    workorder = WorkOrder.query.get(workorder_id)

    if not workorder:
        return jsonify({'success': False, 'message': '工单不存在'}), 404

    log = WorkOrderLog(
        workorder_id=workorder.id,
        user_id=user_id,
        action='deleted',
        content=f'删除了工单：{workorder.title}'
    )
    db.session.add(log)

    db.session.delete(workorder)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '删除成功'
    }), 200


@api_bp.route('/workorders/<int:workorder_id>/status', methods=['PUT'])
@jwt_required()
def update_workorder_status(workorder_id):
    """更新工单状态"""
    user_id = get_jwt_identity()
    workorder = WorkOrder.query.get(workorder_id)

    if not workorder:
        return jsonify({'success': False, 'message': '工单不存在'}), 404

    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({'success': False, 'message': '请提供状态'}), 400

    old_status = workorder.status
    workorder.status = new_status

    status_names = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'cancelled': '已取消'
    }

    log = WorkOrderLog(
        workorder_id=workorder.id,
        user_id=user_id,
        action='status_changed',
        content=f'状态从「{status_names.get(old_status, old_status)}」变更为「{status_names.get(new_status, new_status)}」'
    )
    db.session.add(log)

    if new_status == 'processing' and not workorder.actual_start:
        workorder.actual_start = datetime.utcnow()
        log.content += '，已开始处理'

    if new_status == 'completed':
        workorder.actual_end = datetime.utcnow()
        if data.get('result'):
            workorder.result = data['result']
        log.content += '，处理完成'

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '状态更新成功',
        'data': workorder.to_dict()
    }), 200


@api_bp.route('/workorders/<int:workorder_id>/logs', methods=['GET'])
@jwt_required()
def get_workorder_logs(workorder_id):
    """获取工单处理日志"""
    workorder = WorkOrder.query.get(workorder_id)

    if not workorder:
        return jsonify({'success': False, 'message': '工单不存在'}), 404

    logs = workorder.logs.order_by(WorkOrderLog.created_at.asc()).all()

    return jsonify({
        'success': True,
        'data': [log.to_dict() for log in logs]
    }), 200


@api_bp.route('/workorders/<int:workorder_id>/logs', methods=['POST'])
@jwt_required()
def add_workorder_log(workorder_id):
    """添加工单处理日志"""
    user_id = get_jwt_identity()
    workorder = WorkOrder.query.get(workorder_id)

    if not workorder:
        return jsonify({'success': False, 'message': '工单不存在'}), 404

    data = request.get_json()

    log = WorkOrderLog(
        workorder_id=workorder.id,
        user_id=user_id,
        action=data.get('action', 'comment'),
        content=data.get('content', '')
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '日志添加成功',
        'data': log.to_dict()
    }), 201


@api_bp.route('/workorders/<int:workorder_id>/progress', methods=['GET'])
@jwt_required()
def get_workorder_progress(workorder_id):
    """获取工单处理进度"""
    workorder = WorkOrder.query.get(workorder_id)

    if not workorder:
        return jsonify({'success': False, 'message': '工单不存在'}), 404

    logs = workorder.logs.order_by(WorkOrderLog.created_at.asc()).all()
    total_logs = len(logs)

    progress = 0
    if workorder.status == 'completed':
        progress = 100
    elif workorder.status == 'processing':
        if workorder.plan_start and workorder.plan_end:
            total_duration = (workorder.plan_end - workorder.plan_start).total_seconds()
            elapsed = (datetime.utcnow() - workorder.actual_start).total_seconds() if workorder.actual_start else 0
            progress = min(100, int(elapsed / total_duration * 100))
        else:
            progress = 50
    elif workorder.status == 'pending':
        progress = 10

    return jsonify({
        'success': True,
        'data': {
            'workorder_id': workorder.id,
            'status': workorder.status,
            'progress': progress,
            'total_logs': total_logs,
            'plan_start': workorder.plan_start.isoformat() if workorder.plan_start else None,
            'plan_end': workorder.plan_end.isoformat() if workorder.plan_end else None,
            'actual_start': workorder.actual_start.isoformat() if workorder.actual_start else None,
            'actual_end': workorder.actual_end.isoformat() if workorder.actual_end else None,
            'timeline': [
                {
                    'time': log.created_at.isoformat(),
                    'action': log.action,
                    'content': log.content,
                    'user': log.user.nickname if log.user else None
                } for log in logs
            ]
        }
    }), 200
