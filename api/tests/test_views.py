import pytest
from api_django.models import Category, Discount, Order, Product, ProductReview
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient


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
    client.post("/auth/users/", user, format="json")
    return user, client


@pytest.fixture
def user_supplier():
    """Создание пользователя supplier."""
    user = {
        "email": "test_supplier@gmail.com",
        "username": "str223222222ing",
        "role": "supplier",
        "password": "strin23222g222212344",
        "name": "str3ing",
        "contact_name": "stri3ng",
        "contact_phone": "33131313131",
        "address": "string",
    }
    client = APIClient()
    client.post("/auth/users/", user, format="json")
    return user, client


@pytest.fixture
def user_customer():
    """Создание пользователя customer."""
    user = {
        "email": "test_customer@gmail.com",
        "username": "strumornggh",
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
def get_token_for_user(user_employee, user_customer, user_supplier):
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

    response = client.post(
        "/auth/jwt/create/",
        {"email": user_supplier[0]["email"], "password": user_supplier[0]["password"]},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    token_supplier = response.data["access"]

    return token_employee, token_customer, token_supplier, client


@pytest.mark.django_db
def test_get_jwt_token(get_token_for_user):
    """Проверка получения JWT токена."""
    token_employee, token_customer, token_supplier, client = get_token_for_user

    assert token_employee is not None
    assert token_customer is not None
    assert token_supplier is not None


@pytest.mark.django_db
def test_create_category_as_employee(get_token_for_user):
    """Тестируем создание категории для сотрудника"""
    token_employee, token_customer, token_supplier, client = get_token_for_user

    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    category_data = {"name": "category2"}
    response = client.post("/api/category/", category_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    category_id = response.data["id"]

    assert Category.objects.filter(id=category_id).exists() is True


@pytest.mark.django_db
def test_patch_category_as_employee(get_token_for_user):
    """Тестируем обновление категории для сотрудника"""
    token_employee, token_customer, token_supplier, client = get_token_for_user

    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    category_data = {"name": "category2"}
    create_response = client.post("/api/category/", category_data, format="json")

    assert create_response.status_code == status.HTTP_201_CREATED
    category_id = create_response.data["id"]

    update_data = {"name": "category31"}
    patch_response = client.patch(
        f"/api/category/{category_id}/", update_data, format="json"
    )

    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["name"] == "category31"


@pytest.mark.django_db
def test_delete_category_as_employee(get_token_for_user):
    """Тестируем удаление категории для сотрудника"""
    token_employee, token_customer, token_supplier, client = get_token_for_user

    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    category_data = {"name": "category2"}
    create_response = client.post("/api/category/", category_data, format="json")

    assert create_response.status_code == status.HTTP_201_CREATED
    category_id = create_response.data["id"]

    delete_response = client.delete(f"/api/category/{category_id}/")

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    assert Category.objects.filter(id=category_id).count() == 0
    assert Category.objects.filter(id=category_id).exists() is False


@pytest.fixture
def category(client, get_token_for_user):
    """Создаём категорию для теста"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)
    category_data = {"name": "category3"}
    response = client.post("/api/category/", category_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    return response.data["name"]


@pytest.mark.django_db
def test_create_product_as_supplier(get_token_for_user, category):
    """Тестируем создание продукта для поставщика"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)

    with open("tests/images/test_image.jpg", "rb") as img:
        image = SimpleUploadedFile(
            "test_image.jpg", img.read(), content_type="image/jpeg"
        )
    with open("tests/videos/test_video.mp4", "rb") as video:
        video = SimpleUploadedFile(
            "test_video.mp4", video.read(), content_type="video/mp4"
        )

    product_data = {
        "category": category,
        "name": "product1",
        "price": 100.99,
        "stock": 1000,
        "image": image,
        "video": video,
    }
    response = client.post("/api/products/", product_data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.data["id"]

    assert Product.objects.filter(id=product_id).exists() is True


@pytest.mark.django_db
def test_patch_product_as_supplier(get_token_for_user, category):
    """Тестируем обновление продукта для поставщика"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)

    with open("tests/images/test_image.jpg", "rb") as img:
        image = SimpleUploadedFile(
            "test_image.jpg", img.read(), content_type="image/jpeg"
        )
    with open("tests/videos/test_video.mp4", "rb") as video:
        video = SimpleUploadedFile(
            "test_video.mp4", video.read(), content_type="video/mp4"
        )

    product_data = {
        "category": category,
        "name": "product1",
        "price": 100.99,
        "stock": 1000,
        "image": image,
        "video": video,
    }
    create_response = client.post("/api/products/", product_data, format="multipart")

    assert create_response.status_code == status.HTTP_201_CREATED
    product_id = create_response.data["id"]

    update_data = {"name": "updated_product", "price": 199.99}
    patch_response = client.patch(
        f"/api/products/{product_id}/", update_data, format="json"
    )

    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["name"] == "updated_product"
    assert float(patch_response.data["price"]) == 199.99


@pytest.mark.django_db
def test_delete_product_as_supplier(get_token_for_user, category):
    """Тестируем удаление продукта для поставщика"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)

    with open("tests/images/test_image.jpg", "rb") as img:
        image = SimpleUploadedFile(
            "test_image.jpg", img.read(), content_type="image/jpeg"
        )
    with open("tests/videos/test_video.mp4", "rb") as video:
        video = SimpleUploadedFile(
            "test_video.mp4", video.read(), content_type="video/mp4"
        )

    product_data = {
        "category": category,
        "name": "product1",
        "price": 100.99,
        "stock": 1000,
        "image": image,
        "video": video,
    }
    create_response = client.post("/api/products/", product_data, format="multipart")

    assert create_response.status_code == status.HTTP_201_CREATED
    product_id = create_response.data["id"]

    delete_response = client.delete(f"/api/products/{product_id}/")

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    assert Product.objects.filter(id=product_id).count() == 0
    assert Product.objects.filter(id=product_id).exists() is False


@pytest.fixture
def product1(client, get_token_for_user, category):
    """Создаём категорию для теста"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)
    category_data = {"category": category, "name": "apple", "price": 13, "stock": 1111}
    response = client.post("/api/products/", category_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    return response.data["name"]


@pytest.fixture
def product2(client, get_token_for_user, category):
    """Создаём категорию для теста"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)
    category_data = {"category": category, "name": "banana", "price": 13, "stock": 1111}
    response = client.post("/api/products/", category_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    return response.data["name"]


@pytest.fixture
def discount(client, get_token_for_user):
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)
    discount_data = {
        "code": "dcafjgaf2312ffva",
        "discount_percentage": 10,
        "valid_from": "2025.01.01",
        "valid_to": "2026.12.31",
    }
    response = client.post("/api/discounts/", discount_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    return response.data["code"]


@pytest.mark.django_db
def test_create_order_as_customer(get_token_for_user, product1, product2, discount):
    """Тестируем создание заказа с применением скидки"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    product_data = {
        "products": [
            {"product": product1, "quantity": 1},
            {"product": product2, "quantity": 1},
        ],
        "discount": discount,
    }
    response = client.post("/api/orders/", product_data, format="json")
    order_id = response.data["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["products_data"][0]["product__name"] == product1
    assert response.data["products_data"][1]["product__name"] == product2
    assert response.data["discount"] == discount
    assert float(response.data["total_price"]) == 23.4

    assert Order.objects.filter(id=order_id).exists() is True


@pytest.mark.django_db
def test_patch_order_as_customer(get_token_for_user, product1, product2, discount):
    """Тестируем обновление заказа (PATCH) с изменением количества продуктов"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    product_data = {
        "products": [
            {"product": product1, "quantity": 1},
            {"product": product2, "quantity": 1},
        ],
        "discount": discount,
    }
    create_response = client.post("/api/orders/", product_data, format="json")
    order_id = create_response.data["id"]

    update_data = {
        "products": [
            {"product": product1, "quantity": 2},
            {"product": product2, "quantity": 3},
        ],
        "discount": discount,
    }
    patch_response = client.patch(
        f"/api/orders/{order_id}/", update_data, format="json"
    )

    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["products_data"][0]["product__name"] == product1
    assert patch_response.data["products_data"][1]["product__name"] == product2
    assert patch_response.data["products_data"][0]["quantity"] == 2
    assert patch_response.data["products_data"][1]["quantity"] == 3
    assert float(patch_response.data["total_price"]) == 58.5


@pytest.mark.django_db
def test_delete_order_as_customer(get_token_for_user, product1, product2, discount):
    """Тестируем удаление заказа"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    product_data = {
        "products": [
            {"product": product1, "quantity": 1},
            {"product": product2, "quantity": 1},
        ],
        "discount": discount,
    }
    create_response = client.post("/api/orders/", product_data, format="json")
    order_id = create_response.data["id"]

    # Удаляем заказ
    delete_response = client.delete(f"/api/orders/{order_id}/")

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Проверяем, что заказ был удалён
    assert Order.objects.filter(id=order_id).count() == 0
    assert Order.objects.filter(id=order_id).exists() is False


@pytest.mark.django_db
def test_create_review_as_customer(get_token_for_user, product1):
    """Тестируем создание отзыва"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    review_data = {"product": product1, "rating": 5, "comment": "Good product"}
    response = client.post("/api/reviews/", review_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["product"] == product1
    assert response.data["rating"] == 5
    assert response.data["comment"] == "Good product"

    review_id = response.data["id"]
    assert ProductReview.objects.filter(id=review_id).exists() is True


@pytest.mark.django_db
def test_patch_review_as_customer(get_token_for_user, product1):
    """Тестируем обновление отзыва (PATCH)"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    review_data = {"product": product1, "rating": 5, "comment": "Good product"}
    create_response = client.post("/api/reviews/", review_data, format="json")
    review_id = create_response.data["id"]

    # Патчим отзыв с новым рейтингом
    update_data = {"product": product1, "rating": 4, "comment": "Good product"}
    patch_response = client.patch(
        f"/api/reviews/{review_id}/", update_data, format="json"
    )

    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["product"] == product1
    assert patch_response.data["rating"] == 4
    assert patch_response.data["comment"] == "Good product"


@pytest.mark.django_db
def test_delete_review_as_customer(get_token_for_user, product1):
    """Тестируем удаление отзыва"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    review_data = {"product": product1, "rating": 5, "comment": "Good product"}
    create_response = client.post("/api/reviews/", review_data, format="json")
    review_id = create_response.data["id"]

    delete_response = client.delete(f"/api/reviews/{review_id}/")

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    assert ProductReview.objects.filter(id=review_id).count() == 0
    assert ProductReview.objects.filter(id=review_id).exists() is False


@pytest.mark.django_db
def test_create_discount_as_employee(get_token_for_user):
    """Тестируем создание скидки"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    discount_data = {
        "code": "code1234",
        "discount_percentage": 20,
        "valid_from": "2025.01.01",
        "valid_to": "2026.01.01",
    }
    response = client.post("/api/discounts/", discount_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["code"] == "code1234"
    assert response.data["discount_percentage"] == 20
    assert response.data["valid_from"] == "2025-01-01"
    assert response.data["valid_to"] == "2026-01-01"

    discount_id = response.data["id"]
    assert Discount.objects.filter(id=discount_id).exists() is True


@pytest.mark.django_db
def test_patch_discount_as_employee(get_token_for_user):
    """Тестируем обновление скидки (PATCH)"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    discount_data = {
        "code": "code1234",
        "discount_percentage": 20,
        "valid_from": "2025.01.01",
        "valid_to": "2026.01.01",
    }
    create_response = client.post("/api/discounts/", discount_data, format="json")
    discount_id = create_response.data["id"]

    update_data = {
        "code": "update_code",
        "discount_percentage": 15,
        "valid_from": "2025.01.01",
        "valid_to": "2026.01.01",
    }
    patch_response = client.patch(
        f"/api/discounts/{discount_id}/", update_data, format="json"
    )

    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["code"] == "update_code"
    assert patch_response.data["discount_percentage"] == 15
    assert patch_response.data["valid_from"] == "2025-01-01"
    assert patch_response.data["valid_to"] == "2026-01-01"


@pytest.mark.django_db
def test_delete_discount_as_employee(get_token_for_user):
    """Тестируем удаление скидки"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    discount_data = {
        "code": "code1234",
        "discount_percentage": 20,
        "valid_from": "2025.01.01",
        "valid_to": "2026.01.01",
    }
    create_response = client.post("/api/discounts/", discount_data, format="json")
    discount_id = create_response.data["id"]

    delete_response = client.delete(f"/api/discounts/{discount_id}/")

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    assert Discount.objects.filter(id=discount_id).count() == 0
    assert Discount.objects.filter(id=discount_id).exists() is False
