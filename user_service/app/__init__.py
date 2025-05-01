# user_service/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

# SQLAlchemy extension'ını başlat ama henüz app'e bağlama
db = SQLAlchemy()

def create_app(config_object=None):
    """Application factory pattern"""
    app = Flask(__name__)
    CORS(app)

    # Yapılandırmayı ayarla
    # Önce ortam değişkeninden okumayı dene, sonra config.py'den
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        # Lokal geliştirme veya test için varsayılan ayar (opsiyonel)
        # Veya hata verilebilir: raise ValueError("DATABASE_URL ortam değişkeni ayarlanmamış.")
        # Şimdilik basit bir uyarı verelim. Docker Compose ile bu set edilecek.
        print("UYARI: DATABASE_URL ortam değişkeni bulunamadı.")
        # Geçici olarak sqlite kullanılabilir veya hata verilebilir.
        # app.config.from_object('app.config.DevelopmentConfig') # Örnek config sınıfı
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Geçici fallback
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Performans için önerilir

    # Extension'ları app'e bağla
    db.init_app(app)

    # Modelleri import et (tabloların oluşturulması için önemli)
    # SQLAlchemy'nin tabloları tanıması için modellerin import edilmesi gerekir.
    with app.app_context():
        from . import models # Modelleri import et
        # Veritabanı tablolarını oluştur (eğer yoksa)
        # Alembic gibi migration aracı kullanmak daha iyi bir pratiktir.
        # Şimdilik basitlik için db.create_all() kullanabiliriz.
        # Bu satırı ilk çalıştırmada veya model değiştiğinde aktif etmek gerekebilir.
        db.create_all()
        print("Veritabanı bağlantısı kuruldu ve modeller tanındı.") # Kontrol logu


    # API Blueprints'lerini kaydet
    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/users') # Tüm user endpointleri /users altında olacak

    @app.route('/health')
    def health_check():
        # Basit bir health check endpoint'i
        return {"status": "OK"}, 200

    return app