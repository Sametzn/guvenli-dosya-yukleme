import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_login_success():
    client = APIClient()
    user = User.objects.create_user(username="testuser", password="1234")

    response = client.post("/api/login/", {
        "username": "testuser",
        "password": "1234"
    })

    assert response.status_code == 200
    assert "token" in response.data


@pytest.mark.django_db
def test_login_fail():
    client = APIClient()

    response = client.post("/api/login/", {
        "username": "wrong",
        "password": "wrong"
    })

    assert response.status_code == 401
