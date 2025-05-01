# loan_service/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

db = SQLAlchemy()

def create_app(config_object=None):
    """Application factory pattern for Loan Service"""
    app = Flask(__name__)
    CORS(app)

    # Yapılandırma (Aynı DB)
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("UYARI: LOAN_SERVICE - DATABASE_URL ortam değişkeni bulunamadı.")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Diğer servislerin adreslerini ortam değişkenlerinden al
    app.config['USER_SERVICE_URL'] = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001') # Default localhost for local dev
    app.config['BOOK_SERVICE_URL'] = os.environ.get('BOOK_SERVICE_URL', 'http://localhost:5002') # Default localhost for local dev
    print(f"USER_SERVICE_URL set to: {app.config['USER_SERVICE_URL']}")
    print(f"BOOK_SERVICE_URL set to: {app.config['BOOK_SERVICE_URL']}")


    db.init_app(app)

    with app.app_context():
        from . import models # Loan modelini import et
        db.create_all() # 'loans' tablosunu oluşturacak
        print("LOAN_SERVICE: Veritabanı bağlantısı kuruldu ve modeller tanındı.")

    from .api import bp as api_bp
    # Tüm loan endpointleri /loans altında olacak
    app.register_blueprint(api_bp, url_prefix='/loans')

    @app.route('/health')
    def health_check():
        return {"service": "Loan Service", "status": "OK"}, 200

    return app