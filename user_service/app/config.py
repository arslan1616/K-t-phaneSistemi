# user_service/app/config.py
import os

class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bir_gizli_anahtar') # Flask session vb. için
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Diğer genel ayarlar

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db') # Lokal dev için sqlite

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # Prod için env'den alınmalı
    # Diğer production ayarları (örn: logging)

# Kullanılacak config'i belirle (genellikle ortam değişkenine göre)
# config_by_name = dict(
#     dev=DevelopmentConfig,
#     prod=ProductionConfig
# )
# key = os.environ.get("FLASK_ENV", "dev")
# ACTIVE_CONFIG = config_by_name[key]