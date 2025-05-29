# Mikro Servis Tabanlı Kütüphane Yönetim Sistemi

Bu proje, "Yazılım Tasarım Desenleri " kapsamında geliştirilmiş, **SOLID prensiplerini** temel alan, **mikro servis mimarisiyle** tasarlanmış bir Kütüphane Yönetim Sistemi uygulamasıdır. Sistem, Docker ve Docker Compose kullanılarak platformdan bağımsız bir şekilde çalıştırılabilmektedir.

## Projenin Amacı

*   SOLID prensiplerini uygulayarak yüksek kohezyonlu ve düşük bağımlılıklı modüler bir yazılım tasarımı gerçekleştirmek.
*   Mikro servis mimarisinin temellerini anlamak ve uygulamak.
*   Servisler arası iletişimi RESTful API'lar üzerinden sağlamak.
*   Tüm sistemi Docker konteynerleri ile paketleyip Docker Compose ile kolayca yönetmek.
*   Basit bir veritabanı (PostgreSQL) entegrasyonu gerçekleştirmek.

## Özellikler ve Modüller

Sistem aşağıdaki temel modülleri (mikro servisleri) içerir:

1.  **Kullanıcı Yönetimi (User Service - Port: 5001):**
    *   Kullanıcı kaydı (`POST /users/register`)
    *   Kullanıcı girişi (`POST /users/login`)
    *   Kullanıcıları listeleme (`GET /users`)
    *   Kullanıcı doğrulama (diğer servisler için) (`GET /users/validate/{id}`)
2.  **Kitap Kataloğu (Book Service - Port: 5002):**
    *   Yeni kitap ekleme (`POST /books`)
    *   Kitapları listeleme ve arama (`GET /books`)
    *   Kitap detaylarını getirme (`GET /books/{id}`)
    *   Kitap bilgilerini güncelleme (`PUT /books/{id}`)
    *   Kitap stok/müsaitlik kontrolü ve güncellemesi (diğer servisler için) (`GET /books/{id}/availability`, `PUT /books/{id}/decrement`, `PUT /books/{id}/increment`)
3.  **Ödünç Alma Sistemi (Loan Service - Port: 5003):**
    *   Kitap ödünç alma (`POST /loans`)
    *   Kitap iade etme (`PUT /loans/{loan_id}/return`)
    *   Kullanıcının ödünçlerini listeleme (`GET /loans/user/{id}`)
    *   Kitabın ödünçlerini listeleme (`GET /loans/book/{id}`)
    *   Gecikmiş ödünçleri listeleme (`GET /loans/overdue`)
4.  **Bildirim Sistemi (Notification Service - Port: 5004):**
    *   Bildirim gönderme isteğini kabul etme ve loglama (simülasyon) (`POST /notifications`)
5.  **Veritabanı (PostgreSQL - Port: 5432):**
    *   Tüm servisler tarafından kullanılan merkezi PostgreSQL veritabanı.
6.  **Basit Frontend Arayüzü:**
    *   Temel işlemleri (kayıt, giriş, kitap ekleme/listeleme, ödünç alma/iade) gerçekleştirmek için basit bir HTML/JavaScript arayüzü.

## Kullanılan Teknolojiler

*   **Backend:**
    *   Programlama Dili: Python 3.10
    *   Web Framework: Flask
    *   Veritabanı ORM: SQLAlchemy (Flask-SQLAlchemy ile)
    *   Veritabanı Sürücüsü: Psycopg2
    *   Şifre Hashleme: bcrypt
    *   HTTP İstekleri: requests
    *   CORS Yönetimi: Flask-Cors
*   **Veritabanı:** PostgreSQL 15
*   **Konteynerleştirme ve Orkestrasyon:**
    *   Docker
    *   Docker Compose
*   **Frontend:**
    *   HTML5
    *   CSS3
    *   JavaScript (Vanilla JS, Fetch API)

## Gereksinimler

Bu projeyi çalıştırmak için sisteminizde aşağıdaki yazılımların kurulu olması gerekmektedir:

*   **Docker:** [Docker Kurulumu](https://docs.docker.com/get-docker/)
*   **Docker Compose:** Genellikle Docker Desktop ile birlikte gelir. Docker Compose V2 (`docker compose` komutu) kullanılması tavsiye edilir.

## Kurulum ve Çalıştırma

1.  **Projeyi Klonlayın:**
    ```bash
    git clone <repository_url> # Eğer bir git repo'su varsa
    cd <proje_klasoru_adi>
    ```
    Veya proje dosyalarını bir klasöre indirin/kopyalayın.

2.  **Docker Servislerini Başlatın:**
    Projenin ana dizininde (içinde `docker-compose.yml` dosyasının bulunduğu klasör) bir terminal veya komut istemcisi açın ve aşağıdaki komutu çalıştırın:
    ```bash
    docker compose up --build
    ```
    *   `--build` parametresi, ilk çalıştırmada veya kodda değişiklik yapıldığında imajların oluşturulmasını sağlar.
    *   Bu komut, tüm servisler (veritabanı dahil) için Docker imajlarını oluşturacak (veya indirecek) ve konteynerleri başlatacaktır.
    *   Başlangıçta veritabanının hazır olması beklendiği için ilk başlatma biraz zaman alabilir. Terminalde tüm servislerin loglarını görebilirsiniz.

3.  **Uygulamanın Hazır Olmasını Bekleyin:**
    Terminal loglarında tüm servislerin (özellikle `user_service`, `book_service`, `loan_service`, `notification_service`) hata vermeden "Running on http://..." mesajını gösterdiğini ve veritabanının "database system is ready to accept connections" dediğini görün.

## Arayüze Erişim

Backend servisleri çalışır durumdayken, basit frontend arayüzüne erişmek için:

1.  **Yöntem 1 (Doğrudan Dosya):**
    *   Proje klasöründeki `frontend` dizinine gidin.
    *   `index.html` dosyasına çift tıklayarak varsayılan web tarayıcınızda açın. (Adres `file:///...` şeklinde olacaktır).

2.  **Yöntem 2 (Python HTTP Sunucusu - Tavsiye Edilen):**
    *   Bir terminal açın.
    *   `frontend` klasörünün içine gidin: `cd frontend`
    *   Şu komutu çalıştırın: `python -m http.server 8000` (veya başka bir port, örn: `8081`)
    *   Web tarayıcınızı açın ve `http://localhost:8000` (veya seçtiğiniz port) adresine gidin.

Artık arayüz üzerinden kullanıcı kaydı, kitap ekleme, ödünç alma gibi işlemleri yapabilirsiniz.

## API Erişimi (Postman vb. ile)

Servislerin API'larına doğrudan istek atmak için (örneğin Postman ile):

*   **User Service:** `http://localhost:5001`
*   **Book Service:** `http://localhost:5002`
*   **Loan Service:** `http://localhost:5003`
*   **Notification Service:** `http://localhost:5004`

(İlgili endpointler için servislerin `app/api.py` dosyalarına bakılabilir.)

## Proje Yapısı
``` bash
kütüphane_sistem/
├── docker-compose.yml # Docker Compose yapılandırması
├── user_service/ # Kullanıcı Yönetimi Servisi
│ ├── Dockerfile
│ ├── requirements.txt
│ ├── app/ # Flask uygulama kodu
│ └── run.py # Flask başlatıcı
├── book_service/ # Kitap Kataloğu Servisi
│ ├── ...
├── loan_service/ # Ödünç Alma Servisi
│ ├── ...
├── notification_service/ # Bildirim Servisi
│ ├── ...
├── frontend/ # Basit HTML/JS Arayüzü
│ ├── index.html
│ └── script.js
├── CODING_RULES.md # Kodlama standartları
├── PROJECT_TRACKING.md # Proje ilerleme takibi
├── PRD.txt # Proje gereksinimleri (Ödev tanımı)
├── RFC.txt # Teknik tasarım dokümanı
└── README.md # Bu dosya
```

## Kapatma

Uygulamayı durdurmak için `docker compose up` komutunun çalıştığı terminalde `Ctrl+C` tuşlarına basın. Konteynerları ve oluşturulan ağı kaldırmak için (veritabanı verileri hariç):

```bash
docker compose down
```

Veritabanı verilerini de içeren volumeları kaldırmak için:
```bash
docker compose down --volumes
```

(DİKKAT: Bu komut tüm veritabanı verilerini siler!)
