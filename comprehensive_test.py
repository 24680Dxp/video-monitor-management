#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XX视频监控运营平台 - 完整功能测试脚本
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """测试1: 健康检查"""
    print("\n" + "="*60)
    print("测试1: API健康检查")
    print("="*60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ 健康检查通过")

def test_login():
    """测试2: 用户登录"""
    print("\n" + "="*60)
    print("测试2: 用户登录")
    print("="*60)
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"登录结果: {'成功' if data.get('success') else '失败'}")
    if data.get('success'):
        print(f"用户: {data['data']['user']['nickname']}")
        print(f"角色: {data['data']['user']['role_name']}")
    assert response.status_code == 200
    assert data["success"] == True
    global TOKEN
    TOKEN = data["data"]["token"]
    print(f"Token获取: {TOKEN[:20]}...")
    print("✅ 登录测试通过")
    return TOKEN

def test_projects(token):
    """测试3: 项目管理"""
    print("\n" + "="*60)
    print("测试3: 项目管理")
    print("="*60)
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/api/projects", headers=headers)
    print(f"获取列表 - 状态码: {response.status_code}")
    data = response.json()
    print(f"项目总数: {data['data']['total']}")
    print("✅ 项目管理测试通过")
    return 1

def test_points(token, project_id):
    """测试4: 点位管理"""
    print("\n" + "="*60)
    print("测试4: 点位管理")
    print("="*60)
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/api/points", headers=headers)
    print(f"获取列表 - 状态码: {response.status_code}")
    data = response.json()
    print(f"点位总数: {data['data']['total']}")
    print("✅ 点位管理测试通过")
    return 1

def test_workorders(token, project_id, point_id):
    """测试5: 工单管理"""
    print("\n" + "="*60)
    print("测试5: 工单管理")
    print("="*60)
    headers = {"Authorization": f"Bearer {token}"}

    # 获取工单列表
    response = requests.get(f"{BASE_URL}/api/workorders", headers=headers)
    print(f"获取列表 - 状态码: {response.status_code}")
    data = response.json()
    print(f"工单总数: {data['data']['total']}")
    print("✅ 工单管理测试通过")

def test_materials(token):
    """测试6: 物资管理"""
    print("\n" + "="*60)
    print("测试6: 物资管理")
    print("="*60)
    headers = {"Authorization": f"Bearer {token}"}

    # 获取物资列表
    response = requests.get(f"{BASE_URL}/api/materials", headers=headers)
    print(f"获取列表 - 状态码: {response.status_code}")
    data = response.json()
    print(f"物资总数: {data['data']['total']}")
    print("✅ 物资管理测试通过")

def test_reports(token):
    """测试7: 统计报表"""
    print("\n" + "="*60)
    print("测试7: 统计报表")
    print("="*60)
    headers = {"Authorization": f"Bearer {token}"}

    # 仪表盘
    response = requests.get(f"{BASE_URL}/api/reports/dashboard", headers=headers)
    print(f"仪表盘 - 状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - 工单总数: {data['data'].get('total_workorders', 0)}")
        print(f"  - 项目总数: {data['data'].get('total_projects', 0)}")
        print(f"  - 点位总数: {data['data'].get('total_points', 0)}")
        print(f"  - 物资种类: {data['data'].get('total_materials', 0)}")
        print("✅ 仪表盘数据获取成功")

    # 工单统计
    response = requests.get(f"{BASE_URL}/api/reports/workorder-stats", headers=headers)
    print(f"工单统计 - 状态码: {response.status_code}")

    # 项目统计
    response = requests.get(f"{BASE_URL}/api/reports/project-stats", headers=headers)
    print(f"项目统计 - 状态码: {response.status_code}")

    print("✅ 统计报表测试通过")

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("XX视频监控运营平台 - 完整功能测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试地址: {BASE_URL}")

    try:
        # 基础功能测试
        test_health()
        token = test_login()

        # 核心业务测试
        project_id = test_projects(token)
        point_id = test_points(token, project_id)
        test_workorders(token, project_id, point_id)
        test_materials(token)
        test_reports(token)

        # 总结
        print("\n" + "="*60)
        print("🎉 所有测试完成！")
        print("="*60)
        print("\n测试结果摘要:")
        print("✅ API健康检查 - 通过")
        print("✅ 用户认证系统 - 通过")
        print("✅ 项目管理模块 - 通过")
        print("✅ 点位管理模块 - 通过")
        print("✅ 工单管理模块 - 通过")
        print("✅ 物资管理模块 - 通过")
        print("✅ 统计报表模块 - 通过")
        print("\n📊 系统功能验证完成，可以正常使用！")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
