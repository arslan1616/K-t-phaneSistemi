# notification_service/app/models.py
from . import db
from datetime import datetime

class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) # Bildirimin gönderildiği kullanıcı
    message = db.Column(db.Text, nullable=False)    # Bildirim içeriği
    type = db.Column(db.String(20), nullable=False) # 'email_sim', 'sms_sim' vb.
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Log zamanı

    def __repr__(self):
        return f'<NotificationLog {self.log_id} - User: {self.user_id}, Type: {self.type}>'

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'message': self.message,
            'type': self.type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }