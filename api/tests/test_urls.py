import pytest
from rest_framework import status
from rest_framework.test import APIClient


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
    client.post("/auth/users/", user, format="json")
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
    client.post("/auth/users/", user, format="json")
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
    token_employee = response.data["access"]

    response = client.post(
        "/auth/jwt/create/",
        {"email": user_customer[0]["email"], "password": user_customer[0]["password"]},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    token_customer = response.data["access"]

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

    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    endpoints = [
        "/api/orders/",
        "/api/products/",
        "/api/category/",
        "/api/reviews/",
        "/auth/users/",
        "/users/me/",
        "/users/users/",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ], f"Ошибка на {endpoint}"

    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    employee_endpoints = ["/api/discounts/"]

    for endpoint in employee_endpoints:
        response = client.get(endpoint)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ], f"Ошибка на {endpoint}"
