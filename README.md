# XX视频监控项目运营管理平台

基于Flask和Vue.js的企业级视频监控项目运营管理平台，提供工单管理、项目管理、点位管理、物资管理和统计报表等核心功能。

## 功能特性

### 1. 项目点位工单进度实时查询和管理
- 工单创建、编辑、删除
- 多维度工单筛选（状态、类型、优先级、项目）
- 工单状态实时更新和进度跟踪
- 工单处理日志记录

### 2. 项目售后点位资料信息管理
- 项目信息维护（基本信息、客户、合同）
- 点位台账管理（设备型号、IP地址、位置）
- 点位地图展示
- 设备档案和维保记录

### 3. 项目非集采物资管理
- 物资台账管理
- 入库/出库操作
- 库存实时查询
- 低库存预警

### 4. 项目运营数据统计报表
- 工单统计（状态分布、完成率）
- 项目统计（健康度、分布情况）
- 物资消耗统计
- 工程师绩效统计
- Excel报表导出

## 技术栈

### 后端
- **框架**: Flask 2.3
- **ORM**: Flask-SQLAlchemy
- **数据库**: MySQL 8.0
- **认证**: Flask-JWT-Extended
- **缓存**: Redis

### 前端
- **框架**: Vue.js 3 (CDN)
- **样式**: CSS3 (自定义)
- **图表**: 原生CSS图表

## 快速开始

### 1. 环境要求
- Python 3.8+
- MySQL 8.0+
- Redis (可选)

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库
修改 `.env` 文件中的数据库连接配置：
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/video_monitor?charset=utf8mb4
```

创建数据库：
```sql
CREATE DATABASE video_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 初始化数据库
```bash
python run.py
```

首次运行会自动创建数据库表和默认用户。

### 5. 初始化示例数据（可选）
```bash
python init_data.py
```

### 6. 运行应用
```bash
python run.py
```

访问 `http://localhost:5000`

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 系统管理员 |
| zhangsan | 123456 | 工程师 |

## 项目结构

```
/workspace/
├── app/
│   ├── __init__.py          # Flask应用工厂
│   ├── config.py            # 配置文件
│   ├── models/               # 数据模型
│   │   ├── user.py          # 用户模型
│   │   ├── project.py       # 项目模型
│   │   ├── point.py         # 点位模型
│   │   ├── workorder.py      # 工单模型
│   │   ├── material.py       # 物资模型
│   │   └── dict.py          # 数据字典
│   └── api/                  # API接口
│       ├── auth.py          # 认证接口
│       ├── workorder.py     # 工单接口
│       ├── project.py       # 项目接口
│       ├── point.py         # 点位接口
│       ├── material.py       # 物资接口
│       └── report.py         # 报表接口
├── static/
│   ├── css/
│   │   └── app.css          # 应用样式
│   └── js/
│       └── app.js           # 前端逻辑
├── templates/
│   └── index.html           # 主页面
├── migrations/              # 数据库迁移
├── run.py                   # 应用入口
├── init_data.py            # 示例数据初始化
├── requirements.txt        # Python依赖
└── .env                    # 环境变量配置
```

## API接口

### 认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/current-user` - 获取当前用户

### 工单管理
- `GET /api/workorders` - 获取工单列表
- `POST /api/workorders` - 创建工单
- `GET /api/workorders/{id}` - 获取工单详情
- `PUT /api/workorders/{id}` - 更新工单
- `PUT /api/workorders/{id}/status` - 更新工单状态

### 项目管理
- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取项目详情
- `PUT /api/projects/{id}` - 更新项目

### 点位管理
- `GET /api/points` - 获取点位列表
- `POST /api/points` - 创建点位
- `GET /api/points/{id}` - 获取点位详情
- `PUT /api/points/{id}` - 更新点位

### 物资管理
- `GET /api/materials` - 获取物资列表
- `POST /api/materials` - 创建物资
- `POST /api/materials/inbound` - 物资入库
- `POST /api/materials/outbound` - 物资出库
- `GET /api/materials/inventory` - 库存查询

### 统计报表
- `GET /api/reports/dashboard` - 仪表盘数据
- `GET /api/reports/workorder-stats` - 工单统计
- `GET /api/reports/project-stats` - 项目统计
- `GET /api/reports/material-stats` - 物资统计
- `GET /api/reports/export` - 导出报表

## 扩展功能

### 添加新用户
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"username": "newuser", "password": "123456", "nickname": "新用户"}'
```

### 导出工单报表
访问 `http://localhost:5000/api/reports/export?format=xlsx`

## 注意事项

1. 首次使用请修改默认管理员密码
2. 生产环境请修改 `.env` 中的密钥配置
3. 建议使用Redis缓存提升性能
4. 定期备份数据库

## License

MIT License
