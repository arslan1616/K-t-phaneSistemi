# user_service/app/service.py
from . import db
from .models import User
from .repository import UserRepository
# Hata yönetimi için özel exception sınıfları tanımlanabilir

class UserService:
    def __init__(self):
        # DIP için: Normalde burada IUserRepository tipinde bir dependency inject edilmeli
        # Şimdilik doğrudan somut sınıfı kullanıyoruz.
        self.repository = UserRepository()

    def register_user(self, username, email, password):
        # Doğrulama ve Kontroller
        if not username or not email or not password:
            raise ValueError("Kullanıcı adı, e-posta ve şifre boş olamaz.")
        if self.repository.get_by_username(username):
            raise ValueError(f"'{username}' kullanıcı adı zaten kullanılıyor.")
        if self.repository.get_by_email(email):
            raise ValueError(f"'{email}' e-posta adresi zaten kayıtlı.")

        # Yeni kullanıcı oluştur
        new_user = User(username=username, email=email)
        new_user.set_password(password) # Şifreyi hash'le

        # Veritabanına ekle
        try:
            added_user = self.repository.add(new_user)
            db.session.commit() # İşlem başarılıysa commit et
            return added_user
        except Exception as e:
            db.session.rollback() # Hata olursa geri al
            # Loglama yapılmalı
            print(f"Kullanıcı kaydı sırasında hata: {e}")
            raise RuntimeError("Kullanıcı kaydedilirken bir sunucu hatası oluştu.")

    def authenticate_user(self, username, password):
        user = self.repository.get_by_username(username)
        if user and user.check_password(password):
            # Başarılı giriş - İleride JWT token üretilebilir
            return user
        return None # Başarısız giriş

    def get_user_by_id(self, user_id):
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"ID:{user_id} ile kullanıcı bulunamadı.") # Veya özel NotFoundError
        return user

    def validate_user_exists(self, user_id):
        # Diğer servislerin kullanması için basit varlık kontrolü
        return self.repository.get_by_id(user_id) is not None

    def get_all_users(self):  # <-- YENİ METOD
        return self.repository.list_all()