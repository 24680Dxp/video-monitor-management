#!/usr/bin/env python3
"""API接口测试脚本（修复版）"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ['FLASK_ENV'] = 'testing'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

from app import create_app, db
from app.models import User, Role, Project, Point, WorkOrder, Material
from datetime import datetime

def test_api_endpoints():
    """测试API接口"""
    app = create_app('testing')
    client = app.test_client()

    with app.app_context():
        db.create_all()

        admin_role = Role(name='系统管理员', code='admin', permissions='all')
        db.session.add(admin_role)
        db.session.commit()

        admin = User(username='admin', nickname='测试管理员', role_id=admin_role.id)
        admin.set_password('test123')
        db.session.add(admin)
        db.session.commit()

        project = Project(
            name='API测试项目',
            code='API001',
            customer='测试客户',
            status='active'
        )
        db.session.add(project)
        db.session.commit()

        point = Point(
            project_id=project.id,
            name='API测试点位',
            code='API-PT001',
            status='active'
        )
        db.session.add(point)
        db.session.commit()

        workorder = WorkOrder(
            title='API测试工单',
            type='maintenance',
            status='pending',
            priority='normal',
            project_id=project.id,
            created_by=admin.id
        )
        db.session.add(workorder)
        db.session.commit()

        material = Material(
            name='API测试物资',
            code='API-MAT001',
            current_stock=10
        )
        db.session.add(material)
        db.session.commit()

    print("\n" + "=" * 60)
    print("🌐 API接口测试")
    print("=" * 60)

    print("\n1️⃣  测试健康检查接口...")
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    print(f"   ✓ GET /health - {data}")

    print("\n2️⃣  测试用户登录接口...")
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'test123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'token' in data['data']
    token = data['data']['token']
    print(f"   ✓ POST /api/auth/login - 登录成功")

    headers = {'Authorization': f'Bearer {token}'}

    print("\n3️⃣  测试获取当前用户...")
    response = client.get('/api/auth/current-user', headers=headers)
    print(f"   响应状态码: {response.status_code}")
    if response.status_code != 200:
        print(f"   响应内容: {response.data}")
        return
    data = json.loads(response.data)
    assert data['data']['username'] == 'admin'
    print(f"   ✓ GET /api/auth/current-user - 用户: {data['data']['username']}")

    print("\n4️⃣  测试获取工单列表...")
    response = client.get('/api/workorders', headers=headers)
    if response.status_code != 200:
        print(f"   响应内容: {response.data}")
        return
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'items' in data['data']
    print(f"   ✓ GET /api/workorders - 工单总数: {data['data']['total']}")

    print("\n5️⃣  测试创建工单...")
    response = client.post('/api/workorders', headers=headers, json={
        'title': '新测试工单',
        'type': 'install',
        'priority': 'high',
        'project_id': 1,
        'description': '通过API创建的测试工单'
    })
    if response.status_code != 201:
        print(f"   响应内容: {response.data}")
        return
    data = json.loads(response.data)
    assert data['success'] == True
    print(f"   ✓ POST /api/workorders - 创建工单: {data['data']['title']}")

    print("\n6️⃣  测试获取项目列表...")
    response = client.get('/api/projects', headers=headers)
    if response.status_code != 200:
        print(f"   响应内容: {response.data}")
        return
    data = json.loads(response.data)
    assert data['success'] == True
    print(f"   ✓ GET /api/projects - 项目总数: {data['data']['total']}")

    print("\n7️⃣  测试获取点位列表...")
    response = client.get('/api/points', headers=headers)
    if response.status_code != 200:
        print(f"   响应内容: {response.data}")
        return
    data = json.loads(response.data)
    assert data['success'] == True
    print(f"   ✓ GET /api/points - 点位总数: {data['data']['total']}")

    print("\n8️⃣  测试获取物资列表...")
    response = client.get('/api/materials', headers=headers)
    if response.status_code != 200:
        print(f"   响应内容: {response.data}")
        return
    data = json.loads(response.data)
    assert data['success'] == True
    print(f"   ✓ GET /api/materials - 物资总数: {data['data']['total']}")

    print("\n9️⃣  测试仪表盘数据...")
    response = client.get('/api/reports/dashboard', headers=headers)
    if response.status_code != 200:
        print(f"   响应内容: {response.data}")
        return
    data = json.loads(response.data)
    assert data['success'] == True
    print(f"   ✓ GET /api/reports/dashboard - KPI数据获取成功")

    print("\n🔟 测试工单统计...")
    response = client.get('/api/reports/workorder-stats', headers=headers)
    if response.status_code != 200:
        print(f"   响应内容: {response.data}")
        return
    data = json.loads(response.data)
    assert data['success'] == True
    print(f"   ✓ GET /api/reports/workorder-stats - 统计完成")

    print("\n" + "=" * 60)
    print("✅ 所有API接口测试通过！")
    print("=" * 60)

if __name__ == '__main__':
    test_api_endpoints()
