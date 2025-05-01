# book_service/run.py
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Ortam değişkeninden veya varsayılan porttan oku (5002)
    port = int(os.environ.get('FLASK_RUN_PORT', 5002))
    # debug=True geliştirme için
    app.run(host='0.0.0.0', port=port, debug=True)