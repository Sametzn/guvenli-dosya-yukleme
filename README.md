# 🛡️ Güvenli Dosya Yükleme Servisi (Django + REST)

Bu proje, kullanıcıların dosya yükleyebildiği fakat **güvenlik odaklı** kurallar ile korunan bir backend servisidir.  
Temel amaç, **dosya boyutu**, **kullanıcı kotası**, **MIME tipi** ve **VirusTotal taraması** gibi kontrolleri entegre ederek güvenli bir dosya saklama altyapısı sunmaktır.

> Backend: **Django + Django REST Framework**  
> Auth: **JWT (SimpleJWT)**  
> Deploy: **Render + Docker (opsiyonel)**  
> CI: **GitHub Actions + pytest**

---

## 📑 İçindekiler

- [Özellikler](#-özellikler)
- [Teknolojiler](#-teknolojiler)
- [Mimari Özeti](#-mimari-özeti)
- [Kurulum](#-kurulum)
  - [1. Depoyu Klonla](#1-depoyu-klonla)
  - [2. Sanal Ortam](#2-sanal-ortam)
  - [3. Bağımlılıkların Kurulması](#3-bağımlılıkların-kurulması)
  - [4. Ortam Değişkenleri](#4-ortam-değişkenleri-env)
  - [5. Migrasyonlar](#5-migrasyonlar)
  - [6. Süper Kullanıcı](#6-süper-kullanıcı)
  - [7. Sunucuyu Çalıştır](#7-sunucuyu-çalıştır)
- [API Uç Noktaları](#-api-uç-noktaları)
  - [/api/login/](#post-apilogin)
  - [/api/upload/](#post-apiupload)
  - [/api/list_files/](#get-apilist_files)
  - [/api/user_stats/](#get-apiuser_stats)
- [Güvenlik Kuralları](#-güvenlik-kuralları)
- [Testler](#-testler)
- [Docker ile Çalıştırma](#-docker-ile-çalıştırma)
- [Render Üzerinde Deploy](#-render-üzerinde-deploy)
- [CI/CD (GitHub Actions)](#-cicd-github-actions)
- [Geliştirici Notları](#-geliştirici-notları)

---

## 🔐 Özellikler

- JWT ile **kimlik doğrulama**
- Kullanıcı bazlı **disk kotası** (UserQuota modeli)
- Maksimum dosya boyutu sınırı (**10MB**)
- **MIME tipi kontrolü**:
  - Hem **izin verilen whitelist**
  - Hem de **yasaklanan executable blackliste**
- Dosya içeriğinden **python-magic** ile gerçek MIME tespiti
- **VirusTotal API** ile dosya tarama
  - Zararlı dosyalar engellenir
  - Tüm sonuçlar **VirusLog** tablosuna kaydedilir
- Yüklenen dosyalar **UploadedFile** modelinde loglanır
- Temel istatistik endpoint’i (**toplam kullanım, kalan kota** vb.)
- Otomatik testler (pytest + pytest-django)
- CI pipeline (GitHub Actions)
- Render üzerinde çalışabilecek şekilde ready to deploy

---

## 🧰 Teknolojiler

- **Python 3.13**
- **Django 5.2.8**
- **Django REST Framework 3.16.1**
- **djangorestframework-simplejwt** (JWT auth)
- **django-cors-headers**
- **python-magic** (MIME tespiti)
- **requests** (VirusTotal entegrasyonu için)
- **pytest + pytest-django**
- Deploy:
  - **Render.com** (gunicorn ile)
  - İsteğe bağlı: **Docker**

---

## 🧱 Mimari Özeti

### Modeller

- **UserQuota**
  - `user` (OneToOne → User)
  - `max_storage` (varsayılan: belirlediğin limit)
  - `used_storage`
- **UploadedFile**
  - `user`
  - `file` (FileField - `media/user_files/<username>/...`)
  - `original_name`
  - `stored_name`
  - `size`
  - `mime`
  - `created_at`
- **VirusLog**
  - `user`
  - `action` (örn: `UPLOAD_OK`, `UPLOAD_INFECTED`)
  - `filename`
  - `sha256`
  - `detected` (bool)
  - `result_detail` (VirusTotal sonucu)

### Önemli Modüller

- `upload/views.py`
  - `upload_file` → Dosya upload + tüm güvenlik kontrolleri
- `upload/utils.py`
  - `scan_file_with_virustotal(path)` → VirusTotal API entegrasyonu
- `core/settings.py`
  - CORS, REST, JWT, STATIC/MEDIA ayarları
  - `.env` desteği (python-dotenv ile)
- `upload/tests/` 
  - Upload & auth için birim testleri

---

## ⚙ Kurulum

### 1. Depoyu Klonla

```bash
git clone https://github.com/Sametzn/guvenli-dosya-yukleme.git
cd guvenli-dosya-yukleme

2. Sanal Ortam
python -m venv venv
source venv/bin/activate  # Linux / Mac
# ya da
venv\Scripts\activate     # Windows


3. Bağımlılıkların Kurulması
pip install -r requirements.txt

4. Ortam Değişkenleri (.env)
SECRET_KEY=buraya-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# VirusTotal için
VIRUSTOTAL_API_KEY=buraya-virustotal-api-key

# (İstersen) DB ayarları - varsayılan SQLite
# DATABASE_URL=sqlite:///db.sqlite3
