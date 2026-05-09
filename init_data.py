from app import create_app, db
from app.models import User, Role, Project, Point, WorkOrder, Material, Dict
from datetime import datetime, timedelta
import random


def init_sample_data():
    """初始化示例数据"""
    app = create_app()

    with app.app_context():
        print('开始创建示例数据...')

        projects = [
            Project(
                name='XX区政府视频监控项目',
                code='PRJ001',
                customer='XX区人民政府',
                address='XX市XX区XX路1号',
                industry='政府机关',
                status='active',
                start_date=datetime.utcnow().date() - timedelta(days=180),
                end_date=datetime.utcnow().date() + timedelta(days=185),
                description='覆盖全区主要街道和公共场所的视频监控系统'
            ),
            Project(
                name='XX学校智慧校园项目',
                code='PRJ002',
                customer='XX学校',
                address='XX市XX区XX路2号',
                industry='教育',
                status='active',
                start_date=datetime.utcnow().date() - timedelta(days=90),
                end_date=datetime.utcnow().date() + timedelta(days=275),
                description='校园安全和智慧教学视频监控系统'
            ),
            Project(
                name='XX医院安防监控项目',
                code='PRJ003',
                customer='XX医院',
                address='XX市XX区XX路3号',
                industry='医疗',
                status='active',
                start_date=datetime.utcnow().date() - timedelta(days=60),
                end_date=datetime.utcnow().date() + timedelta(days=305),
                description='医院内部安全和病房看护视频监控系统'
            )
        ]

        for p in projects:
            db.session.add(p)
        db.session.commit()
        print(f'已创建 {len(projects)} 个项目')

        materials_data = [
            {'name': '海康威视摄像头', 'code': 'CAM001', 'category': '摄像设备', 'spec': 'DS-2CD3T86FWDV2-I3S', 'unit': '台', 'price': 680.00, 'current_stock': 45, 'low_stock_threshold': 10},
            {'name': '大华网络摄像机', 'code': 'CAM002', 'category': '摄像设备', 'spec': 'DH-IPC-HFW5442T-ASE', 'unit': '台', 'price': 720.00, 'current_stock': 38, 'low_stock_threshold': 10},
            {'name': 'TP-Link交换机', 'code': 'SW001', 'category': '网络设备', 'spec': 'TL-SG3428', 'unit': '台', 'price': 1250.00, 'current_stock': 12, 'low_stock_threshold': 5},
            {'name': '华为防火墙', 'code': 'FW001', 'category': '网络安全', 'spec': 'USG6550E', 'unit': '台', 'price': 8500.00, 'current_stock': 3, 'low_stock_threshold': 2},
            {'name': '西部数据硬盘', 'code': 'HDD001', 'category': '存储设备', 'spec': 'WD Purple 4TB', 'unit': '块', 'price': 580.00, 'current_stock': 8, 'low_stock_threshold': 15},
            {'name': '三星SSD固态硬盘', 'code': 'SSD001', 'category': '存储设备', 'spec': '870 EVO 1TB', 'unit': '块', 'price': 650.00, 'current_stock': 25, 'low_stock_threshold': 10},
            {'name': '宇视录像机', 'code': 'NVR001', 'category': '存储设备', 'spec': 'NVR301-16S3', 'unit': '台', 'price': 2800.00, 'current_stock': 6, 'low_stock_threshold': 3},
            {'name': '网线CAT6', 'code': 'CABLE001', 'category': '线材', 'spec': 'CAT6 305米/箱', 'unit': '箱', 'price': 420.00, 'current_stock': 18, 'low_stock_threshold': 5},
            {'name': '光纤跳线', 'code': 'FC001', 'category': '线材', 'spec': 'SC-SC 3米', 'unit': '根', 'price': 35.00, 'current_stock': 52, 'low_stock_threshold': 20},
            {'name': '电源适配器', 'code': 'PWR001', 'category': '配件', 'spec': '12V 2A', 'unit': '个', 'price': 25.00, 'current_stock': 85, 'low_stock_threshold': 30},
            {'name': '水晶头', 'code': 'RJ001', 'category': '配件', 'spec': 'CAT6 100个/盒', 'unit': '盒', 'price': 45.00, 'current_stock': 32, 'low_stock_threshold': 10},
            {'name': 'PVC线槽', 'code': 'TRAY001', 'category': '安装材料', 'spec': '40*20 2米/根', 'unit': '根', 'price': 18.00, 'current_stock': 120, 'low_stock_threshold': 50}
        ]

        materials = []
        for m in materials_data:
            material = Material(**m)
            db.session.add(material)
            materials.append(material)
        db.session.commit()
        print(f'已创建 {len(materials)} 种物资')

        points_data = []
        point_types = ['枪机', '球机', '半球', '人脸抓拍机']
        point_status = ['online', 'offline', 'maintenance']

        for project in projects:
            for i in range(1, random.randint(15, 25)):
                point = Point(
                    project_id=project.id,
                    name=f'{project.name.split("视频")[0]} {chr(64+i)}区{point_types[i % len(point_types)]}{i}',
                    code=f'{project.code}-PT{i:03d}',
                    address=project.address,
                    latitude=39.9 + random.uniform(-0.1, 0.1),
                    longitude=116.4 + random.uniform(-0.1, 0.1),
                    device_type=point_types[i % len(point_types)],
                    device_model='DS-2CD3T86FWDV2-I3S' if i % 2 == 0 else 'DH-IPC-HFW5442T-ASE',
                    device_sn=f'SN{project.id}{i:08d}',
                    ip_address=f'192.168.{project.id}.{i+10}',
                    status='active' if random.random() > 0.1 else 'offline',
                    description=f'位于{project.address}的监控点位'
                )
                db.session.add(point)
                points_data.append(point)

        db.session.commit()
        print(f'已创建 {len(points_data)} 个点位')

        engineers = User.query.filter_by(role_id=Role.query.filter_by(code='engineer').first().id).all()
        if not engineers:
            engineers = User.query.filter(User.role_id.isnot(None)).all()

        workorder_types = ['install', 'maintenance', 'inspection', 'fault']
        workorder_statuses = ['pending', 'processing', 'completed', 'completed', 'completed']
        workorder_priorities = ['low', 'normal', 'normal', 'high', 'urgent']

        workorders = []
        for i in range(1, 51):
            project = random.choice(projects)
            point = random.choice([p for p in points_data if p.project_id == project.id])
            workorder = WorkOrder(
                title=f'{project.name} - {random.choice(["设备安装", "故障维修", "定期巡检", "系统升级", "画面调整"])}',
                type=random.choice(workorder_types),
                status=random.choice(workorder_statuses),
                priority=random.choice(workorder_priorities),
                project_id=project.id,
                point_id=point.id if random.random() > 0.3 else None,
                created_by=User.query.filter_by(username='admin').first().id,
                assigned_to=random.choice(engineers).id if engineers else None,
                description=f'工单编号WO{i:05d}，需要进行相关维护工作',
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                actual_start=datetime.utcnow() - timedelta(days=random.randint(0, 15)) if random.random() > 0.4 else None,
                actual_end=datetime.utcnow() - timedelta(days=random.randint(0, 7)) if random.random() > 0.3 else None
            )
            db.session.add(workorder)
            workorders.append(workorder)

        db.session.commit()
        print(f'已创建 {len(workorders)} 个工单')

        dict_data = [
            {'category': 'workorder_type', 'code': 'install', 'name': '安装', 'sort_order': 1},
            {'category': 'workorder_type', 'code': 'maintenance', 'name': '维护', 'sort_order': 2},
            {'category': 'workorder_type', 'code': 'inspection', 'name': '巡检', 'sort_order': 3},
            {'category': 'workorder_type', 'code': 'fault', 'name': '故障', 'sort_order': 4},
            {'category': 'workorder_status', 'code': 'pending', 'name': '待处理', 'sort_order': 1},
            {'category': 'workorder_status', 'code': 'processing', 'name': '处理中', 'sort_order': 2},
            {'category': 'workorder_status', 'code': 'completed', 'name': '已完成', 'sort_order': 3},
            {'category': 'workorder_status', 'code': 'cancelled', 'name': '已取消', 'sort_order': 4},
            {'category': 'priority', 'code': 'low', 'name': '低', 'sort_order': 1},
            {'category': 'priority', 'code': 'normal', 'name': '普通', 'sort_order': 2},
            {'category': 'priority', 'code': 'high', 'name': '高', 'sort_order': 3},
            {'category': 'priority', 'code': 'urgent', 'name': '紧急', 'sort_order': 4},
            {'category': 'industry', 'code': 'government', 'name': '政府机关', 'sort_order': 1},
            {'category': 'industry', 'code': 'education', 'name': '教育', 'sort_order': 2},
            {'category': 'industry', 'code': 'medical', 'name': '医疗', 'sort_order': 3},
            {'category': 'industry', 'code': 'commercial', 'name': '商业', 'sort_order': 4},
            {'category': 'material_category', 'code': 'camera', 'name': '摄像设备', 'sort_order': 1},
            {'category': 'material_category', 'code': 'network', 'name': '网络设备', 'sort_order': 2},
            {'category': 'material_category', 'code': 'storage', 'name': '存储设备', 'sort_order': 3},
            {'category': 'material_category', 'code': 'cable', 'name': '线材', 'sort_order': 4},
            {'category': 'material_category', 'code': 'accessory', 'name': '配件', 'sort_order': 5},
        ]

        for d in dict_data:
            existing = Dict.query.filter_by(category=d['category'], code=d['code']).first()
            if not existing:
                dict_item = Dict(**d)
                db.session.add(dict_item)

        db.session.commit()
        print(f'已创建 {len(dict_data)} 条字典数据')

        print('示例数据创建完成！')


if __name__ == '__main__':
    init_sample_data()
