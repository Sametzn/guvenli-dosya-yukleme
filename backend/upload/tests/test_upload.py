import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from upload.models import UserQuota

@pytest.mark.django_db
def test_quota_block():
    client = APIClient()
    user = User.objects.create_user(username="a", password="1")
    client.force_authenticate(user)



    quota, created = UserQuota.objects.get_or_create(user=user)
    quota.used_storage = 0
    quota.max_storage = 5  # 5 byte kota :)
    quota.save()

    file = SimpleUploadedFile("big.txt", b"a" * 9999)

    response = client.post("/api/upload/", {"file": file}, format="multipart")

    assert response.status_code == 403
    assert response.data["message"] == "Kota yetersiz."

@pytest.mark.django_db
def test_mime_block():
    client = APIClient()
    user = User.objects.create_user(username="x", password="1")
    client.force_authenticate(user)

    file = SimpleUploadedFile("hack.exe", b"data", content_type="application/x-msdownload")

    response = client.post("/api/upload/", {"file": file}, format="multipart")

    assert response.status_code == 400
    assert "MIME türü engellendi" in response.data["message"]



mock_infected = (True, {"malicious": 10})

@pytest.mark.django_db
@patch("upload.utils.scan_file_with_virustotal", return_value=mock_infected)
def test_infected_file_block(mock_scan):
    client = APIClient()
    user = User.objects.create_user(username="deneme", password="1234")
    client.force_authenticate(user)

    file = SimpleUploadedFile("virus.txt", b"virus", content_type="text/plain")

    response = client.post("/api/upload/", {"file": file}, format="multipart")

    assert response.status_code == 400
    assert response.data["message"] == "Dosya virüslü, yüklenmedi!"

@patch("magic.from_buffer", side_effect=Exception("MIME error"))
@pytest.mark.django_db
def test_magic_error(mock_magic):
    client = APIClient()
    user = User.objects.create_user(username="a", password="1")
    client.force_authenticate(user)

    file = SimpleUploadedFile("a.txt", b"data")

    response = client.post("/api/upload/", {"file": file}, format="multipart")
    assert response.status_code == 500
@pytest.mark.django_db
def test_no_file():
    client = APIClient()
    user = User.objects.create_user(username="a", password="1")
    client.force_authenticate(user)

    response = client.post("/api/upload/", {}, format="multipart")
    assert response.status_code == 400
    assert response.data["message"] == "Dosya seçilmedi."
@pytest.mark.django_db
def test_file_too_big():
    client = APIClient()
    user = User.objects.create_user(username="a", password="1")
    client.force_authenticate(user)

    big_data = b"0" * (11 * 1024 * 1024)
    file = SimpleUploadedFile("big.bin", big_data)

    response = client.post("/api/upload/", {"file": file}, format="multipart")
    assert response.status_code == 400
    assert "10MB" in response.data["message"]
@pytest.mark.django_db
def test_unauthorized_upload():
    client = APIClient()
    file = SimpleUploadedFile("a.txt", b"data")
    response = client.post("/api/upload/", {"file": file}, format="multipart")

    assert response.status_code == 401
mock_clean = (False, {"malicious": 0})

@patch("upload.utils.scan_file_with_virustotal", return_value=mock_clean)
@pytest.mark.django_db
def test_clean_file_upload(mock_scan):
    client = APIClient()
    user = User.objects.create_user(username="a", password="1")
    client.force_authenticate(user)

    file = SimpleUploadedFile("ok.txt", b"hello")

    response = client.post("/api/upload/", {"file": file}, format="multipart")
    assert response.status_code == 200
