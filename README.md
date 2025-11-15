🛡️ Güvenli Dosya Yükleme Servisi (Django + REST)

Bu proje, kullanıcıların dosya yükleyebildiği fakat güvenlik odaklı kurallar ile korunan bir backend servisidir.
Temel amaç, dosya boyutu, kullanıcı kotası, MIME tipi ve VirusTotal taraması gibi kontrolleri entegre ederek güvenli bir dosya saklama altyapısı sunmaktır.

Backend: Django + Django REST Framework
Auth: JWT (SimpleJWT)
Deploy: Render + Docker (opsiyonel)
CI: GitHub Actions + pytest

📑 İçindekiler

Özellikler

Teknolojiler

Mimari Özeti

Kurulum

API Uç Noktaları

Güvenlik Kuralları

Testler

Docker ile Çalıştırma

Render Deploy

CI/CD (GitHub Actions)

Geliştirici Notları

🔐 Özellikler

JWT kimlik doğrulama

Kullanıcı bazlı disk kotası

Maksimum dosya boyutu (10 MB)

MIME tipi doğrulama (whitelist & blacklist)

python-magic ile gerçek içerik analizi

VirusTotal API ile virüs tarama

Tüm aksiyonların VirusLog tablosuna kaydı

Yüklenen dosyaların UploadedFile modelinde kayıt altına alınması

Kullanıcı depolama istatistikleri

Otomatik testler (pytest)

CI pipeline (GitHub Actions)

Render üzerinde Production-ready deploy

🧰 Teknolojiler

Python 3.13

Django 5.2.8

Django REST Framework

SimpleJWT

django-cors-headers

python-magic

pytest + pytest-django

Docker (opsiyonel)

Render Deploy

GitHub Actions

🧱 Mimari Özeti
Modeller

UserQuota

UploadedFile

VirusLog

Modüller

upload/views.py → dosya yükleme, MIME, kota, VT kontrolü

upload/utils.py → VirusTotal fonksiyonu

upload/tests/ → pytest testleri

core/settings.py → REST, JWT, CORS, ENV ayarları

⚙ Kurulum
1. Depoyu Klonla
git clone https://github.com/Sametzn/guvenli-dosya-yukleme.git
cd guvenli-dosya-yukleme

2. Sanal Ortam
python -m venv venv
venv\Scripts\activate

3. Gereksinimler
pip install -r requirements.txt

4. .env Dosyası

Kök dizine .env ekle:

SECRET_KEY=xxx
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
VIRUSTOTAL_API_KEY=xxx

5. Migrasyonlar
python manage.py migrate

6. Süper Kullanıcı
python manage.py createsuperuser

7. Çalıştır
python manage.py runserver

🌐 API Uç Noktaları
POST /api/login/

JWT login.

POST /api/upload/

Dosya yükleme.
Kontroller:

Dosya seçili mi

Kota yeterli mi

10MB sınırı

MIME whitelist / blacklist

VirusTotal scan

GET /api/list_files/

Kullanıcı dosya listesi.

GET /api/user_stats/

Kullanıcı depolama bilgileri.

🛡 Güvenlik Kuralları
1. Kullanıcı Kotası

UserQuota modeli ile takip edilir.

2. Max Dosya Boyutu

10 MB limit.

3. MIME Tipi Kontrolü

Whitelist

pdf

jpeg

png

x-empty

text/plain

docx

Blacklist

exe

dosexec

executable

portable-executable

4. VirusTotal Taraması

Dosya önce temp’e kaydedilir → taranır → temizse yüklenir.

🧪 Testler

Tüm testleri çalıştır:

pytest -v


Kapsanan testler:

test_quota_block

test_mime_block

test_infected_file_block

test_magic_error

test_no_file

test_file_too_big

test_unauthorized_upload

test_clean_file_upload

test_login_success

test_login_fail

🐳 Docker ile Çalıştırma
Docker Build
docker build -t guvenli-backend .

Çalıştır
docker run -p 8000:8000 guvenli-backend

☁ Render Deploy
Build command
pip install -r requirements.txt

Start command
gunicorn core.wsgi:application --bind 0.0.0.0:8000

Environment variables

SECRET_KEY

DEBUG=False

ALLOWED_HOSTS

VIRUSTOTAL_API_KEY

Render otomatik deploy oluşturur.

🔁 CI/CD (GitHub Actions)

.github/workflows/ci.yml içinde yer alır.

Pipeline:

Python kurulumu

Dependencies

pytest

Django settings → core.settings

Trigger:

push

pull_request
