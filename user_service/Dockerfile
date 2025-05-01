# user_service/Dockerfile

# Python base image seçimi
FROM python:3.10

# Çalışma dizinini ayarla
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libssl-dev \
    && rm -rf /var/lib/apt/lists/*
# Bağımlılıkları kopyala ve kur
# Önce requirements.txt kopyalanırsa, kod değiştiğinde tekrar tekrar install yapmaz (Docker layer caching)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
# .dockerignore dosyası kullanarak gereksiz dosyaların kopyalanmasını engellemek iyi bir pratiktir.
COPY . .

# Uygulamanın çalışacağı portu belirt
EXPOSE 5001

# Uygulamayı başlatma komutu
# run.py dosyasını çalıştıracak (Flask development server)
# Üretim ortamı için Gunicorn gibi bir WSGI server kullanılmalıdır.
CMD ["flask", "run"]