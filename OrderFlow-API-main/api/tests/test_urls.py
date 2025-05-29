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
        "email": "user@e22xamp222l21e.com",
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
def user_customer():
    """Создание пользователя customer."""
    user = {
        "email": "user@2e222xamp222l21e.com",
        "username": "str22222222ing",
        "role": "customer",
        "password": "strin222g222212344",
        "phone_number": "31414142",
        "address": "string",
        "contact_name": "string",
        "company_name": "string",
        "country": "string",
    }
    client = APIClient()
    response = client.post("/auth/users/", user, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    return user, client


@pytest.fixture
def get_token_for_user(user_employee, user_customer):
    """Получаем JWT токен для обоих пользователей."""
    client = APIClient()

    response = client.post(
        "/auth/jwt/create/",
        {"email": user_employee[0]["email"], "password": user_employee[0]["password"]},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    token_employee = response.json()["access"]

    response = client.post(
        "/auth/jwt/create/",
        {"email": user_customer[0]["email"], "password": user_customer[0]["password"]},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    token_customer = response.json()["access"]

    return token_employee, token_customer, client


@pytest.mark.django_db
def test_get_jwt_token(get_token_for_user):
    """Проверка получения JWT токена."""
    token_employee, token_customer, _ = get_token_for_user

    assert token_employee is not None
    assert token_customer is not None


@pytest.mark.django_db
def test_protected_endpoints_for_customers(get_token_for_user):
    """Тестируем защищённые эндпоинты для customers и employees."""
    token_employee, token_customer, client = get_token_for_user

    # Тестируем эндпоинты для customer
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    customer_endpoints = [
        "/api/orders/",
        "/api/products/",
        "/api/category/",
        "/api/reviews/",
        "/auth/users/",
        "/users/me/",
        "/users/users/",
    ]

    for endpoint in customer_endpoints:
        response = client.get(endpoint)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ], f"Ошибка на {endpoint}"

    # Тестируем эндпоинты для employee
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    employee_endpoints = [
        "/api/discounts/",
        "/api/orders/",
        "/api/products/",
        "/api/category/",
        "/api/reviews/",
        "/auth/users/",
        "/users/me/",
        "/users/users/",
    ]

    for endpoint in employee_endpoints:
        response = client.get(endpoint)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ], f"Ошибка на {endpoint}"


@pytest.mark.django_db
def test_public_endpoints():
    """Тестируем публичные эндпоинты."""
    client = APIClient()

    public_endpoints = [
        "/api/products/",
        "/api/category/",
        "/auth/jwt/create/",
        "/auth/users/",
    ]

    for endpoint in public_endpoints:
        response = client.get(endpoint)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ], f"Ошибка на {endpoint}"


@pytest.mark.django_db
def test_invalid_endpoints():
    """Тестируем несуществующие эндпоинты."""
    client = APIClient()

    invalid_endpoints = [
        "/api/invalid/",
        "/invalid/",
        "/api/products/invalid/",
    ]

    for endpoint in invalid_endpoints:
        response = client.get(endpoint)
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_401_UNAUTHORIZED,
        ], f"Ошибка на {endpoint}"
