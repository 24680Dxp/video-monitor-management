import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import redis

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
redis_client = None


def create_app(config_name=None):
    global redis_client

    app = Flask(__name__, static_folder='../static', template_folder='../templates')

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    from app.config import config
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    try:
        redis_client = redis.from_url(app.config['REDIS_URL'])
        redis_client.ping()
    except:
        redis_client = None

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'XX视频监控运营平台API服务运行正常'}

    with app.app_context():
        from app import models

    return app
