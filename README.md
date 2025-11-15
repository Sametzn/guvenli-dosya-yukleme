🛡️ Güvenli Dosya Yükleme Sistemi

(Django REST + VirusTotal + MIME Doğrulama + Kota Yönetimi)

Bu proje, kullanıcıların dosya yükleyebildiği fakat yüklenen dosyaların güvenlik testlerinden geçmeden sisteme kabul edilmediği profesyonel bir backend servisidir.
Amaç; siber güvenlik, dosya doğrulama ve tehdit tespiti odaklı güvenli bir dosya yönetim altyapısı sunmaktır.

📘 İçindekiler

1️⃣ Özellikler

2️⃣ Mimarî Yapı

3️⃣ Kullanılan Teknolojiler

4️⃣ Kurulum & Çalıştırma

5️⃣ API Uç Noktaları

6️⃣ Güvenlik Mekanizmaları

7️⃣ Test Altyapısı (pytest)

8️⃣ Docker Desteği

9️⃣ Render Deploy

🔟 CI/CD – GitHub Actions

1️⃣1️⃣ Geliştirici Notları

1️⃣ Özellikler
✔ Güvenli Dosya Yükleme

Dosya boyutu kontrolü (max 10 MB)

MIME tipi doğrulama (whitelist + blacklist)

python-magic ile gerçek içerik analizi

✔ Virüs Tespiti (VirusTotal API)

Dosya temp olarak kaydedilir

VirusTotal üzerinden taranır

Sonuç loglanır

Zararlı dosyalar engellenir

✔ Kullanıcı Kota Yönetimi

Her kullanıcının depolama sınırı var

Kota dolduğunda yükleme engellenir

Kullanıcı depolama istatistikleri API üzerinden alınabilir

✔ Loglama Sistemi

Tüm işlemler VirusLog tablosuna kaydedilir

Kim yükledi?

Dosya adı?

Temiz/Virüslü?

SHA256?

Detaylı sonuç?

✔ JWT Kimlik Doğrulama (SimpleJWT)

Login → Token üretme

Token ile dosya yükleme izni

2️⃣ Mimarî Yapı
guvenli-dosya-yukleme/
├── core/                → Django çekirdek ayarları
├── upload/              → Dosya yükleme uygulaması
│   ├── models.py        → UploadedFile, VirusLog, UserQuota
│   ├── views.py         → upload_file(), list_files(), stats
│   ├── utils.py         → VirusTotal entegrasyonu
│   ├── tests/           → pytest dosyaları
│   └── serializers.py
├── requirements.txt
├── Dockerfile
└── .github/workflows/ci.yml

3️⃣ Kullanılan Teknolojiler
Backend

Django 5.2.8

Django REST Framework

SimpleJWT

django-cors-headers

python-magic

requests

Test

pytest

pytest-django

Dağıtım

Render

Docker (opsiyonel)

GitHub Actions

4️⃣ Kurulum & Çalıştırma
1. Projeyi klonla
git clone https://github.com/Sametzn/guvenli-dosya-yukleme.git
cd guvenli-dosya-yukleme

2. Sanal ortam kur
python -m venv venv
venv\Scripts\activate

3. Gereksinimler
pip install -r requirements.txt

4. .env oluştur
SECRET_KEY=xxx
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
VIRUSTOTAL_API_KEY=xxx

5. Migrasyonlar
python manage.py migrate

6. Süper kullanıcı
python manage.py createsuperuser

7. Çalıştır
python manage.py runserver

5️⃣ API Uç Noktaları
🔐 Auth
Yöntem	URL	Açıklama
POST	/api/login/	JWT Login
📤 Dosya Yükleme
URL	Açıklama
POST /api/upload/	Dosya yükleme + güvenlik kontrolleri
📄 Dosya Listesi
URL	Açıklama
GET /api/list_files/	Kullanıcının yüklediği dosyalar
📊 Kullanıcı Kota Bilgisi
URL	Açıklama
GET /api/user_stats/	Depolama durumu
6️⃣ Güvenlik Mekanizmaları
✔ Dosya Boyutu Kontrolü

Max 10 MB

✔ MIME Tipi Kontrolü
Whitelist:

pdf

jpeg

png

x-empty

text/plain

docx

Blacklist:

exe

dosexec

portable executable

✔ Gerçek İçerik Analizi (python-magic)

application/x-msdownload gibi tehlikeli içerikler reddedilir.

✔ VirusTotal Tarama

Temp’e kaydedilir

VirusTotal ID → sonuç

Virüslüyse yükleme engellenir

✔ Loglama

Her işlem VirusLog tablosuna yazılır.

7️⃣ Test Altyapısı (pytest)

Testleri çalıştır:

pytest -v


Kapsanan testler:

test_login_success

test_login_fail

test_no_file

test_file_too_big

test_quota_block

test_mime_block

test_infected_file_block

test_clean_file_upload

test_magic_error

test_unauthorized_upload

8️⃣ Docker Desteği
Docker Image oluştur:
docker build -t guvenli-backend .

Çalıştır:
docker run -p 8000:8000 guvenli-backend

9️⃣ Render Deploy
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn core.wsgi:application --bind 0.0.0.0:8000

Environment Variables:

SECRET_KEY

DEBUG=False

ALLOWED_HOSTS

VIRUSTOTAL_API_KEY

Backend artık internet üzerinde canlı çalışır.

🔟 CI/CD – GitHub Actions

.github/workflows/ci.yml otomatik çalışır.

Pipeline’da neler olur?

Python kurulumu

Dependencies

Django ayarları

pytest (otomatik)

Build kontrol

Her push ve pull request'te otomatik çalışır.
