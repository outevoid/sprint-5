import pytest
import requests


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000"


def test_ping_endpoint(base_url):
    response = requests.get(f"{base_url}/ping")
    assert response.status_code == 200
    assert "cache" in response.json()
    assert "database" in response.json()
    assert "cache_access_time" in response.json()
    assert "database_access_time" in response.json()


def test_register_user(base_url):

    user_data = {"username": "test_user", "password": "test_password"}

    response = requests.post(f"{base_url}/register", json=user_data)

    assert response.status_code == 200

    assert response.json()["message"] == "User registered successfully"


def test_login_for_access_token(base_url):

    login_data = {"username": "test_user", "password": "test_password"}

    response = requests.post(f"{base_url}/token", data=login_data)

    assert response.status_code == 200

    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
