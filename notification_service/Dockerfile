# notification_service/Dockerfile

FROM python:3.10

WORKDIR /app

# Sistem kütüphaneleri (Gerekirse)
RUN apt-get update && apt-get install -y --no-install-recommends libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Notification Service için port 5004
EXPOSE 5004

CMD ["flask", "run"]