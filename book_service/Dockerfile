# book_service/Dockerfile

# User Service ile aynı base imajı kullanmak tutarlılık sağlar
FROM python:3.10

WORKDIR /app

# Sistem kütüphaneleri (eğer standart imajda değilse)
# Slim imaj kullanmıyorsak genellikle gerekmez ama zarar vermez
RUN apt-get update && apt-get install -y --no-install-recommends libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Book Service için farklı bir port kullanalım (örn: 5002)
EXPOSE 5002

# Uygulamayı başlatma komutu
CMD ["flask", "run"]