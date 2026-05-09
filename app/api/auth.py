from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.api import api_bp
from app import db
from app.models.user import User, Role
from datetime import timedelta


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': '请提供用户名和密码'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    if user.status != 1:
        return jsonify({'success': False, 'message': '用户账号已被禁用'}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role.code if user.role else 'user'},
        expires_delta=timedelta(hours=24)
    )

    return jsonify({
        'success': True,
        'data': {
            'token': access_token,
            'user': user.to_dict()
        }
    }), 200


@api_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出接口"""
    return jsonify({'success': True, 'message': '登出成功'}), 200


@api_bp.route('/auth/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': '请提供用户名和密码'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400

    role = Role.query.filter_by(code='user').first()

    user = User(
        username=data['username'],
        nickname=data.get('nickname', data['username']),
        email=data.get('email'),
        phone=data.get('phone'),
        role_id=role.id if role else None
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '注册成功',
        'data': user.to_dict()
    }), 201


@api_bp.route('/auth/current-user', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    return jsonify({
        'success': True,
        'data': user.to_dict()
    }), 200


@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')

    query = User.query

    if keyword:
        query = query.filter(
            db.or_(
                User.username.like(f'%{keyword}%'),
                User.nickname.like(f'%{keyword}%'),
                User.email.like(f'%{keyword}%')
            )
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'data': {
            'items': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }), 200


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    return jsonify({
        'success': True,
        'data': user.to_dict()
    }), 200


@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    data = request.get_json()

    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'role_id' in data:
        user.role_id = data['role_id']
    if 'status' in data:
        user.status = data['status']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': user.to_dict()
    }), 200


@api_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """创建新用户"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': '请提供用户名和密码'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400

    user = User(
        username=data['username'],
        nickname=data.get('nickname', data['username']),
        email=data.get('email'),
        phone=data.get('phone'),
        role_id=data.get('role_id')
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '创建成功',
        'data': user.to_dict()
    }), 201


@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '删除成功'
    }), 200


@api_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """获取角色列表"""
    roles = Role.query.all()

    return jsonify({
        'success': True,
        'data': [role.to_dict() for role in roles]
    }), 200
