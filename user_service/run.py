# user_service/run.py
import os
from app import create_app

# Ortam değişkenlerinden veya varsayılan config'den uygulama ayarlarını yükle
# Şu an için basit tutuyoruz, config.py kullanılabilir
app = create_app()

if __name__ == '__main__':
    # Dockerfile'da CMD ile yönetildiği için host ve port burada tekrar belirtilmeyebilir,
    # ama lokal çalıştırma için kalabilir. Ortam değişkenleri önceliklidir.
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) # Debug=True geliştirme için