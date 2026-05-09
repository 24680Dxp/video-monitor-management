from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required
from app.api import api_bp
from app import db
from app.models.workorder import WorkOrder
from app.models.project import Project
from app.models.point import Point
from app.models.material import Material, MaterialInbound, MaterialOutbound
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import func
import xlwt
from io import BytesIO


@api_bp.route('/reports/workorder-stats', methods=['GET'])
@jwt_required()
def get_workorder_stats():
    """工单统计"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    project_id = request.args.get('project_id', type=int)

    query = WorkOrder.query

    if project_id:
        query = query.filter(WorkOrder.project_id == project_id)
    if start_date:
        query = query.filter(WorkOrder.created_at >= start_date)
    if end_date:
        query = query.filter(WorkOrder.created_at <= end_date)

    total = query.count()
    pending = query.filter(WorkOrder.status == 'pending').count()
    processing = query.filter(WorkOrder.status == 'processing').count()
    completed = query.filter(WorkOrder.status == 'completed').count()
    cancelled = query.filter(WorkOrder.status == 'cancelled').count()

    by_type = db.session.query(
        WorkOrder.type,
        func.count(WorkOrder.id)
    ).filter(
        WorkOrder.project_id == project_id if project_id else True,
        WorkOrder.created_at >= start_date if start_date else True,
        WorkOrder.created_at <= end_date if end_date else True
    ).group_by(WorkOrder.type).all()

    by_priority = db.session.query(
        WorkOrder.priority,
        func.count(WorkOrder.id)
    ).filter(
        WorkOrder.project_id == project_id if project_id else True,
        WorkOrder.created_at >= start_date if start_date else True,
        WorkOrder.created_at <= end_date if end_date else True
    ).group_by(WorkOrder.priority).all()

    completion_rate = round(completed / total * 100, 2) if total > 0 else 0

    return jsonify({
        'success': True,
        'data': {
            'total': total,
            'pending': pending,
            'processing': processing,
            'completed': completed,
            'cancelled': cancelled,
            'completion_rate': completion_rate,
            'by_type': [{'type': t, 'count': c} for t, c in by_type],
            'by_priority': [{'priority': p, 'count': c} for p, c in by_priority]
        }
    }), 200


@api_bp.route('/reports/project-stats', methods=['GET'])
@jwt_required()
def get_all_projects_stats():
    """项目统计（用于报表）"""
    status = request.args.get('status')

    query = Project.query
    if status:
        query = query.filter(Project.status == status)

    total_projects = query.count()
    active_projects = query.filter(Project.status == 'active').count()

    projects_data = []
    for project in query.all():
        total_workorders = WorkOrder.query.filter_by(project_id=project.id).count()
        completed_workorders = WorkOrder.query.filter_by(project_id=project.id, status='completed').count()
        total_points = Point.query.filter_by(project_id=project.id).count()

        projects_data.append({
            'project_id': project.id,
            'project_name': project.name,
            'project_code': project.code,
            'customer': project.customer,
            'status': project.status,
            'total_workorders': total_workorders,
            'completed_workorders': completed_workorders,
            'completion_rate': round(completed_workorders / total_workorders * 100, 2) if total_workorders > 0 else 0,
            'total_points': total_points
        })

    projects_data.sort(key=lambda x: x['completion_rate'], reverse=True)

    return jsonify({
        'success': True,
        'data': {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'projects': projects_data
        }
    }), 200


@api_bp.route('/reports/material-stats', methods=['GET'])
@jwt_required()
def get_material_stats():
    """物资统计"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    project_id = request.args.get('project_id', type=int)

    total_materials = Material.query.filter_by(status='active').count()
    total_stock_value = db.session.query(
        func.sum(Material.price * Material.current_stock)
    ).filter(Material.status == 'active').scalar() or 0

    low_stock_count = Material.query.filter(
        Material.status == 'active',
        Material.current_stock <= Material.low_stock_threshold
    ).count()

    outbound_query = MaterialOutbound.query
    if start_date:
        outbound_query = outbound_query.filter(MaterialOutbound.outbound_at >= start_date)
    if end_date:
        outbound_query = outbound_query.filter(MaterialOutbound.outbound_at <= end_date)

    total_outbound = outbound_query.count()
    total_outbound_value = db.session.query(
        func.sum(Material.price * MaterialOutbound.quantity)
    ).join(Material).filter(
        MaterialOutbound.id.in_([o.id for o in outbound_query.all()])
    ).scalar() or 0

    by_category = db.session.query(
        Material.category,
        func.count(Material.id),
        func.sum(Material.current_stock)
    ).filter(Material.status == 'active', Material.category.isnot(None)).group_by(Material.category).all()

    recent_consumption = outbound_query.order_by(MaterialOutbound.outbound_at.desc()).limit(10).all()

    return jsonify({
        'success': True,
        'data': {
            'total_materials': total_materials,
            'total_stock_value': float(total_stock_value),
            'low_stock_count': low_stock_count,
            'total_outbound': total_outbound,
            'total_outbound_value': float(total_outbound_value),
            'by_category': [
                {
                    'category': c,
                    'material_count': count,
                    'total_stock': stock
                } for c, count, stock in by_category
            ],
            'recent_consumption': [o.to_dict() for o in recent_consumption]
        }
    }), 200


@api_bp.route('/reports/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """仪表盘统计数据"""
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    today_start = datetime.combine(today, datetime.min.time())
    week_ago_start = datetime.combine(week_ago, datetime.min.time())

    today_workorders = WorkOrder.query.filter(
        WorkOrder.created_at >= today_start
    ).count()

    pending_workorders = WorkOrder.query.filter(
        WorkOrder.status.in_(['pending', 'processing'])
    ).count()

    active_projects = Project.query.filter_by(status='active').count()

    low_stock_materials = Material.query.filter(
        Material.status == 'active',
        Material.current_stock <= Material.low_stock_threshold
    ).count()

    total_workorders = WorkOrder.query.count()
    completed_workorders = WorkOrder.query.filter_by(status='completed').count()
    completion_rate = round(completed_workorders / total_workorders * 100, 2) if total_workorders > 0 else 0

    workorder_trend = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day + timedelta(days=1), datetime.min.time())
        count = WorkOrder.query.filter(
            WorkOrder.created_at >= day_start,
            WorkOrder.created_at < day_end
        ).count()
        workorder_trend.append({
            'date': day.isoformat(),
            'count': count
        })

    workorder_trend.reverse()

    by_status = db.session.query(
        WorkOrder.status,
        func.count(WorkOrder.id)
    ).group_by(WorkOrder.status).all()

    by_type = db.session.query(
        WorkOrder.type,
        func.count(WorkOrder.id)
    ).group_by(WorkOrder.type).all()

    recent_workorders = WorkOrder.query.order_by(
        WorkOrder.created_at.desc()
    ).limit(10).all()

    return jsonify({
        'success': True,
        'data': {
            'kpi': {
                'today_workorders': today_workorders,
                'pending_workorders': pending_workorders,
                'active_projects': active_projects,
                'low_stock_materials': low_stock_materials,
                'completion_rate': completion_rate
            },
            'workorder_trend': workorder_trend,
            'by_status': [{'status': s, 'count': c} for s, c in by_status],
            'by_type': [{'type': t, 'count': c} for t, c in by_type],
            'recent_workorders': [wo.to_brief_dict() for wo in recent_workorders]
        }
    }), 200


@api_bp.route('/reports/export', methods=['GET'])
@jwt_required()
def export_report():
    """导出报表"""
    report_type = request.args.get('type', 'workorders')
    format = request.args.get('format', 'xlsx')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if format != 'xlsx':
        return jsonify({'success': False, 'message': '仅支持导出Excel格式'}), 400

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('工单统计')

    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    style.font = font

    ws.write(0, 0, '序号', style)
    ws.write(0, 1, '工单标题', style)
    ws.write(0, 2, '工单类型', style)
    ws.write(0, 3, '状态', style)
    ws.write(0, 4, '优先级', style)
    ws.write(0, 5, '项目名称', style)
    ws.write(0, 6, '指派给', style)
    ws.write(0, 7, '创建时间', style)
    ws.write(0, 8, '完成时间', style)

    query = WorkOrder.query

    if start_date:
        query = query.filter(WorkOrder.created_at >= start_date)
    if end_date:
        query = query.filter(WorkOrder.created_at <= end_date)

    workorders = query.order_by(WorkOrder.created_at.desc()).all()

    type_names = {
        'install': '安装',
        'maintenance': '维护',
        'inspection': '巡检',
        'fault': '故障'
    }
    status_names = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'cancelled': '已取消'
    }
    priority_names = {
        'low': '低',
        'normal': '普通',
        'high': '高',
        'urgent': '紧急'
    }

    for i, wo in enumerate(workorders, 1):
        ws.write(i, 0, i)
        ws.write(i, 1, wo.title)
        ws.write(i, 2, type_names.get(wo.type, wo.type))
        ws.write(i, 3, status_names.get(wo.status, wo.status))
        ws.write(i, 4, priority_names.get(wo.priority, wo.priority))
        ws.write(i, 5, wo.project.name if wo.project else '')
        ws.write(i, 6, wo.assignee.nickname if wo.assignee else '')
        ws.write(i, 7, wo.created_at.strftime('%Y-%m-%d %H:%M') if wo.created_at else '')
        ws.write(i, 8, wo.actual_end.strftime('%Y-%m-%d %H:%M') if wo.actual_end else '')

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.ms-excel'
    response.headers['Content-Disposition'] = f'attachment; filename=工单统计_{datetime.utcnow().strftime("%Y%m%d")}.xls'

    return response


@api_bp.route('/reports/engineer-performance', methods=['GET'])
@jwt_required()
def get_engineer_performance():
    """工程师绩效统计"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = User.query.join(WorkOrder, WorkOrder.assigned_to == User.id)

    if start_date:
        query = query.filter(WorkOrder.created_at >= start_date)
    if end_date:
        query = query.filter(WorkOrder.created_at <= end_date)

    users = User.query.join(WorkOrder, WorkOrder.assigned_to == User.id).distinct().all()

    performance_data = []
    for user in users:
        assigned_workorders = WorkOrder.query.filter(WorkOrder.assigned_to == user.id)
        if start_date:
            assigned_workorders = assigned_workorders.filter(WorkOrder.created_at >= start_date)
        if end_date:
            assigned_workorders = assigned_workorders.filter(WorkOrder.created_at <= end_date)

        total = assigned_workorders.count()
        completed = assigned_workorders.filter(WorkOrder.status == 'completed').count()
        avg_duration = None

        completed_workorders = assigned_workorders.filter(WorkOrder.status == 'completed').all()
        if completed_workorders:
            total_duration = sum(
                (wo.actual_end - wo.actual_start).total_seconds()
                for wo in completed_workorders
                if wo.actual_end and wo.actual_start
            )
            if completed > 0:
                avg_duration = round(total_duration / completed / 3600, 2)

        performance_data.append({
            'user_id': user.id,
            'user_name': user.nickname or user.username,
            'total_workorders': total,
            'completed_workorders': completed,
            'completion_rate': round(completed / total * 100, 2) if total > 0 else 0,
            'avg_duration_hours': avg_duration
        })

    performance_data.sort(key=lambda x: x['completed_workorders'], reverse=True)

    return jsonify({
        'success': True,
        'data': performance_data
    }), 200
