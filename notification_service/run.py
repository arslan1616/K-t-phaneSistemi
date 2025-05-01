# notification_service/run.py
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Ortam değişkeninden veya varsayılan porttan oku (5004)
    port = int(os.environ.get('FLASK_RUN_PORT', 5004))
    app.run(host='0.0.0.0', port=port, debug=True)