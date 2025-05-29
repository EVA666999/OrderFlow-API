import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings
from channels_redis.core import RedisChannelLayer


@pytest.fixture(autouse=True)
def mock_redis():
    """Мокаем Redis для тестов."""
    settings.CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
    yield
    settings.CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(settings.REDIS_HOST, int(settings.REDIS_PORT))],
            },
        },
    }


@pytest.fixture
def user_employee():
    """Создание пользователя employee."""
    user = {
        "email": "test_employee@gmail.com",
        "username": "str2221222ing",
        "role": "employee",
        "password": "strin222g22212344",
        "first_name": "dajfa",
        "last_name": "gfjiosjog",
        "phone": "4132324521",
        "salary": "1000",
    }
    client = APIClient()
    response = client.post("/auth/users/", user, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    return user, client


@pytest.fixture
def get_token_for_user(user_employee):
    """Получаем JWT токен для пользователя employee и возвращаем клиент."""
    client = APIClient()

    # Для employee
    response = client.post(
        "/auth/jwt/create/",
        {"email": user_employee[0]["email"], "password": user_employee[0]["password"]},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    token_employee = response.json()["access"]

    return token_employee, client


@pytest.mark.django_db
def test_get_jwt_token(get_token_for_user):
    """Проверка получения JWT токена."""
    token_employee, client = get_token_for_user
    assert token_employee is not None


@pytest.mark.django_db
def test_aichat(get_token_for_user):
    """Тестируем работу AI чата."""
    token_employee, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)
    
    # Тест с простым запросом
    data = {"message": "Привет"}
    response = client.post("/chat/", data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "response" in response.json()
    assert isinstance(response.json()["response"], str)
    
    # Тест с запросом о категории
    data = {"message": "Выведи название категории c id 1"}
    response = client.post("/chat/", data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "response" in response.json()
    
    # Тест с некорректным запросом
    data = {"message": ""}
    response = client.post("/chat/", data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
