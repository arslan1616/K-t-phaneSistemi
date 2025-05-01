# notification_service/app/service.py
from datetime import datetime
from . import db
from .models import NotificationLog
from .repository import NotificationRepository
# User service'i çağırmayacağımız için requests'e gerek yok

class NotificationService:
    def __init__(self):
        self.repository = NotificationRepository()

    def send_notification(self, user_id: int, message: str, notification_type: str):
        """
        Bildirim gönderme işlemini simüle eder (konsola yazdırır)
        ve veritabanına log kaydı oluşturur.
        """
        # 1. Simülasyon: Bildirimi konsola yazdır
        print("--- SENDING NOTIFICATION (SIMULATION) ---")
        print(f"Timestamp: {datetime.utcnow()}")
        print(f"To User ID: {user_id}")
        print(f"Type: {notification_type}")
        print(f"Message: {message}")
        print("----------------------------------------")

        # (Opsiyonel: Burada gerçek e-posta/SMS gönderme kodu olabilirdi)
        # (Opsiyonel: User Service'i çağırıp email/tel no alınıp loga eklenebilirdi)

        # 2. Loglama: Veritabanına kaydet
        log_entry = NotificationLog(
            user_id=user_id,
            message=message,
            type=notification_type
            # timestamp otomatik atanacak
        )

        try:
            added_log = self.repository.add_log(log_entry)
            db.session.commit()
            print(f"Notification logged to DB with log_id: {added_log.log_id}")
            return added_log # Başarı durumunda log nesnesini döndür
        except Exception as e:
            db.session.rollback()
            print(f"Bildirim loglanırken hata oluştu: {e}")
            # Bu, işlemin başarısız olduğu anlamına gelir, API'ye hata döndürülmeli
            raise RuntimeError("Bildirim loglanırken bir veritabanı hatası oluştu.")