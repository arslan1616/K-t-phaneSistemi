# user_service/app/api.py
from flask import Blueprint, request, jsonify
from .service import UserService
from . import db # db session yönetimi için gerekebilir

# Blueprint oluşturma
bp = Blueprint('api', __name__)

# Dependency Injection (basit versiyon)
# Her request için yeni bir instance oluşturmak yerine global instance kullanabiliriz (thread-safe olmalı)
# Veya Flask'ın g objesi ya da özel DI kütüphaneleri kullanılabilir.
user_service = UserService()

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not 'username' in data or not 'email' in data or not 'password' in data:
        return jsonify({"error": "Eksik bilgi: username, email ve password gereklidir."}), 400

    username = data['username']
    email = data['email']
    password = data['password']

    try:
        new_user = user_service.register_user(username, email, password)
        # Başarılı yanıt - Oluşturulan kaynağın ID'sini veya tüm objeyi dönebiliriz
        return jsonify(new_user.to_dict()), 201 # 201 Created
    except ValueError as e:
        # Beklenen kullanıcı hataları (örn: duplicate username)
        return jsonify({"error": str(e)}), 400 # Bad Request
    except RuntimeError as e:
        # Beklenmeyen sunucu hataları
        return jsonify({"error": str(e)}), 500 # Internal Server Error
    except Exception as e:
        # Diğer beklenmeyen hatalar (loglanmalı)
        print(f"Bilinmeyen hata: {e}")
        db.session.rollback() # Emin olmak için rollback
        return jsonify({"error": "Beklenmeyen bir sunucu hatası oluştu."}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not 'username' in data or not 'password' in data:
        return jsonify({"error": "Eksik bilgi: username ve password gereklidir."}), 400

    username = data['username']
    password = data['password']

    user = user_service.authenticate_user(username, password)

    if user:
        # Başarılı giriş - İleride buraya JWT token üretimi eklenecek
        # Şimdilik kullanıcı bilgisini dönelim
        return jsonify({"message": "Giriş başarılı", "user": user.to_dict()}), 200
    else:
        return jsonify({"error": "Geçersiz kullanıcı adı veya şifre."}), 401 # Unauthorized

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = user_service.get_user_by_id(user_id)
        return jsonify(user.to_dict()), 200
    except ValueError as e: # Veya NotFoundError
        return jsonify({"error": str(e)}), 404 # Not Found

@bp.route('/validate/<int:user_id>', methods=['GET'])
def validate_user(user_id):
    # Diğer servislerin kullanacağı basit varlık kontrol endpoint'i
    exists = user_service.validate_user_exists(user_id)
    if exists:
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False}), 404 # Not Found

@bp.route('', methods=['GET']) # /users adresine GET isteği
def list_users(): # <-- YENİ ENDPOINT
    try:
        users = user_service.get_all_users()
        # Yanıtta şifre hash'ini döndürmemek önemli! to_dict kullanıyoruz.
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        print(f"Bilinmeyen hata (list_users): {e}")
        return jsonify({"error": "Kullanıcılar listelenirken bir hata oluştu."}), 500