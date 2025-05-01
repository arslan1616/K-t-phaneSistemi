# notification_service/app/api.py
from flask import Blueprint, request, jsonify
from .service import NotificationService
from . import db # Rollback için (gerekirse)

bp = Blueprint('api', __name__)
notification_service = NotificationService() # Basit DI

@bp.route('', methods=['POST']) # /notifications adresine POST
def handle_notification_request():
    data = request.get_json()
    if not data or 'user_id' not in data or 'message' not in data or 'type' not in data:
        return jsonify({"error": "Eksik bilgi: user_id, message ve type gereklidir."}), 400

    user_id = data['user_id']
    message = data['message']
    notification_type = data['type'] # örn: 'email_sim', 'loan_reminder_sms_sim'

    try:
        # user_id integer olmalı
        user_id = int(user_id)
        log_result = notification_service.send_notification(user_id, message, notification_type)
        # Başarılı simülasyon ve loglama
        # 202 Accepted genellikle asenkron veya hemen sonuç dönmeyen işlemler için kullanılır,
        # burada simülasyon olduğu için uygun olabilir. Ya da 201 Created da kullanılabilir.
        return jsonify({"message": "Bildirim isteği alındı ve loglandı.", "log_id": log_result.log_id}), 202

    except ValueError: # int(user_id) hatası
        return jsonify({"error": "Geçersiz user_id formatı."}), 400
    except RuntimeError as e: # Service'den gelen DB hatası
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Bilinmeyen hata (handle_notification_request): {e}")
        return jsonify({"error": "Beklenmeyen bir sunucu hatası oluştu."}), 500