# loan_service/run.py
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Ortam değişkeninden veya varsayılan porttan oku (5003)
    port = int(os.environ.get('FLASK_RUN_PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)