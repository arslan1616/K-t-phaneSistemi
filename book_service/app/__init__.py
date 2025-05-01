# book_service/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

# SQLAlchemy extension'ını başlat
# DİKKAT: User Service'deki ile aynı db nesnesini kullanmıyoruz.
# Her servis kendi Flask app instance'ı ve kendi DB session yönetimine sahip olmalı,
# ancak aynı veritabanına bağlanabilirler.
# Daha merkezi bir DB yönetimi için common bir library oluşturulabilir ama şimdilik ayrı tutalım.
db = SQLAlchemy()

def create_app(config_object=None):
    """Application factory pattern for Book Service"""
    app = Flask(__name__)
    CORS(app)
    # Yapılandırmayı ayarla (User Service ile aynı DB'ye bağlanacak)
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("UYARI: BOOK_SERVICE - DATABASE_URL ortam değişkeni bulunamadı.")
        # Geliştirme için fallback veya hata
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Geçici
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extension'ları app'e bağla
    db.init_app(app)

    # Modelleri import et ve tabloları oluştur (eğer yoksa)
    with app.app_context():
        from . import models # Book modelini import et
        # User Service zaten 'users' tablosunu oluşturdu.
        # Book Service 'books' tablosunu oluşturacak.
        db.create_all()
        print("BOOK_SERVICE: Veritabanı bağlantısı kuruldu ve modeller tanındı.")

    # API Blueprints'lerini kaydet
    from .api import bp as api_bp
    # Tüm book endpointleri /books altında olacak
    app.register_blueprint(api_bp, url_prefix='/books')

    @app.route('/health')
    def health_check():
        return {"service": "Book Service", "status": "OK"}, 200

    return app