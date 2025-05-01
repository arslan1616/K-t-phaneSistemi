# notification_service/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

db = SQLAlchemy()

def create_app(config_object=None):
    """Application factory pattern for Notification Service"""
    app = Flask(__name__)
    CORS(app)

    # Yapılandırma (Aynı DB)
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("UYARI: NOTIFICATION_SERVICE - DATABASE_URL ortam değişkeni bulunamadı.")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # User service URL'si (opsiyonel, şimdilik kullanmayacağız)
    # app.config['USER_SERVICE_URL'] = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')

    db.init_app(app)

    with app.app_context():
        from . import models # NotificationLog modelini import et
        db.create_all() # 'notification_logs' tablosunu oluşturacak
        print("NOTIFICATION_SERVICE: Veritabanı bağlantısı kuruldu ve modeller tanındı.")

    from .api import bp as api_bp
    # Tüm notification endpointleri /notifications altında olacak
    app.register_blueprint(api_bp, url_prefix='/notifications')

    @app.route('/health')
    def health_check():
        return {"service": "Notification Service", "status": "OK"}, 200

    return app