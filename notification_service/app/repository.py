# notification_service/app/repository.py
from . import db
from .models import NotificationLog

class NotificationRepository:
    def add_log(self, log: NotificationLog) -> NotificationLog:
        """Yeni bir bildirim logunu veritabanına ekler."""
        db.session.add(log)
        # Commit service katmanında yapılacak
        return log