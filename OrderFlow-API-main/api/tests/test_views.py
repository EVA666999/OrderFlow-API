import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from api_django.models import Category, Discount, Order, Product, ProductReview


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
    """Получаем JWT токен для всех пользователей."""
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
def test_create_product_as_supplier(get_token_for_user, test_image, test_video):
    """Тестируем создание продукта для поставщика"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product_data = {
        "category": category.id,
        "name": "Test Product",
        "price": 100.99,
        "stock": 1000,
        "image": test_image,
        "video": test_video,
    }
    response = client.post("/api/products/", product_data, format="multipart")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Test Product"
    assert response.data["price"] == 100.99
    assert response.data["stock"] == 1000


@pytest.mark.django_db
def test_patch_product_as_supplier(get_token_for_user, test_image, test_video):
    """Тестируем обновление продукта для поставщика"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product_data = {
        "category": category.id,
        "name": "Test Product",
        "price": 100.99,
        "stock": 1000,
        "image": test_image,
        "video": test_video,
    }
    create_response = client.post("/api/products/", product_data, format="multipart")
    assert create_response.status_code == status.HTTP_201_CREATED
    product_id = create_response.data["id"]

    # Обновляем продукт
    update_data = {
        "name": "Updated Product",
        "price": 200.99,
        "stock": 500,
    }
    patch_response = client.patch(
        f"/api/products/{product_id}/", update_data, format="json"
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["name"] == "Updated Product"
    assert patch_response.data["price"] == 200.99
    assert patch_response.data["stock"] == 500


@pytest.mark.django_db
def test_delete_product_as_supplier(get_token_for_user, test_image, test_video):
    """Тестируем удаление продукта для поставщика"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product_data = {
        "category": category.id,
        "name": "Test Product",
        "price": 100.99,
        "stock": 1000,
        "image": test_image,
        "video": test_video,
    }
    create_response = client.post("/api/products/", product_data, format="multipart")
    assert create_response.status_code == status.HTTP_201_CREATED
    product_id = create_response.data["id"]

    # Удаляем продукт
    delete_response = client.delete(f"/api/products/{product_id}/")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Product.objects.filter(id=product_id).exists()


@pytest.fixture
def product1(client, get_token_for_user, category, test_image, test_video):
    """Создаём продукт для теста"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)
    product_data = {
        "category": category,
        "name": "product1",
        "price": 100.99,
        "stock": 1000,
        "image": test_image,
        "video": test_video,
    }
    response = client.post("/api/products/", product_data, format="multipart")
    assert response.status_code == status.HTTP_201_CREATED
    return response.data["id"]


@pytest.fixture
def product2(client, get_token_for_user, category, test_image, test_video):
    """Создаём второй продукт для теста"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_supplier)
    product_data = {
        "category": category,
        "name": "product2",
        "price": 200.99,
        "stock": 2000,
        "image": test_image,
        "video": test_video,
    }
    response = client.post("/api/products/", product_data, format="multipart")
    assert response.status_code == status.HTTP_201_CREATED
    return response.data["id"]


@pytest.fixture
def discount(client, get_token_for_user):
    """Создаём скидку для теста"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)
    discount_data = {
        "name": "discount1",
        "description": "test discount",
        "discount_percent": 10,
        "active": True,
    }
    response = client.post("/api/discounts/", discount_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    return response.data["id"]


@pytest.mark.django_db
def test_create_order_as_customer(get_token_for_user, test_image, test_video):
    """Тестируем создание заказа для клиента"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product = Product.objects.create(
        category=category,
        name="Test Product",
        price=100.99,
        stock=1000,
        image=test_image,
        video=test_video,
    )

    # Создаем заказ
    order_data = {
        "products": [{"product": product.id, "quantity": 2}],
        "shipping_address": "Test Address",
        "payment_method": "card",
    }
    response = client.post("/api/orders/", order_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["shipping_address"] == "Test Address"
    assert response.data["payment_method"] == "card"
    assert len(response.data["products"]) == 1
    assert response.data["products"][0]["product"] == product.id
    assert response.data["products"][0]["quantity"] == 2


@pytest.mark.django_db
def test_patch_order_as_customer(get_token_for_user, test_image, test_video):
    """Тестируем обновление заказа для клиента"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product = Product.objects.create(
        category=category,
        name="Test Product",
        price=100.99,
        stock=1000,
        image=test_image,
        video=test_video,
    )

    # Создаем заказ
    order_data = {
        "products": [{"product": product.id, "quantity": 2}],
        "shipping_address": "Test Address",
        "payment_method": "card",
    }
    create_response = client.post("/api/orders/", order_data, format="json")
    assert create_response.status_code == status.HTTP_201_CREATED
    order_id = create_response.data["id"]

    # Обновляем заказ
    update_data = {
        "shipping_address": "Updated Address",
        "payment_method": "cash",
    }
    patch_response = client.patch(
        f"/api/orders/{order_id}/", update_data, format="json"
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["shipping_address"] == "Updated Address"
    assert patch_response.data["payment_method"] == "cash"


@pytest.mark.django_db
def test_delete_order_as_customer(get_token_for_user, test_image, test_video):
    """Тестируем удаление заказа для клиента"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product = Product.objects.create(
        category=category,
        name="Test Product",
        price=100.99,
        stock=1000,
        image=test_image,
        video=test_video,
    )

    # Создаем заказ
    order_data = {
        "products": [{"product": product.id, "quantity": 2}],
        "shipping_address": "Test Address",
        "payment_method": "card",
    }
    create_response = client.post("/api/orders/", order_data, format="json")
    assert create_response.status_code == status.HTTP_201_CREATED
    order_id = create_response.data["id"]

    # Удаляем заказ
    delete_response = client.delete(f"/api/orders/{order_id}/")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Order.objects.filter(id=order_id).exists()


@pytest.mark.django_db
def test_create_review_as_customer(get_token_for_user, test_image, test_video):
    """Тестируем создание отзыва для клиента"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product = Product.objects.create(
        category=category,
        name="Test Product",
        price=100.99,
        stock=1000,
        image=test_image,
        video=test_video,
    )

    # Создаем отзыв
    review_data = {
        "product": product.id,
        "rating": 5,
        "comment": "Great product!",
    }
    response = client.post("/api/reviews/", review_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["rating"] == 5
    assert response.data["comment"] == "Great product!"
    assert response.data["product"] == product.id


@pytest.mark.django_db
def test_patch_review_as_customer(get_token_for_user, test_image, test_video):
    """Тестируем обновление отзыва для клиента"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product = Product.objects.create(
        category=category,
        name="Test Product",
        price=100.99,
        stock=1000,
        image=test_image,
        video=test_video,
    )

    # Создаем отзыв
    review_data = {
        "product": product.id,
        "rating": 5,
        "comment": "Great product!",
    }
    create_response = client.post("/api/reviews/", review_data, format="json")
    assert create_response.status_code == status.HTTP_201_CREATED
    review_id = create_response.data["id"]

    # Обновляем отзыв
    update_data = {
        "rating": 4,
        "comment": "Updated review",
    }
    patch_response = client.patch(
        f"/api/reviews/{review_id}/", update_data, format="json"
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["rating"] == 4
    assert patch_response.data["comment"] == "Updated review"


@pytest.mark.django_db
def test_delete_review_as_customer(get_token_for_user, test_image, test_video):
    """Тестируем удаление отзыва для клиента"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_customer)

    # Создаем категорию
    category = Category.objects.create(name="Test Category")

    # Создаем продукт
    product = Product.objects.create(
        category=category,
        name="Test Product",
        price=100.99,
        stock=1000,
        image=test_image,
        video=test_video,
    )

    # Создаем отзыв
    review_data = {
        "product": product.id,
        "rating": 5,
        "comment": "Great product!",
    }
    create_response = client.post("/api/reviews/", review_data, format="json")
    assert create_response.status_code == status.HTTP_201_CREATED
    review_id = create_response.data["id"]

    # Удаляем отзыв
    delete_response = client.delete(f"/api/reviews/{review_id}/")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not ProductReview.objects.filter(id=review_id).exists()


@pytest.mark.django_db
def test_create_discount_as_employee(get_token_for_user):
    """Тестируем создание скидки для сотрудника"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    discount_data = {
        "name": "discount1",
        "description": "test discount",
        "discount_percent": 10,
        "active": True,
    }
    response = client.post("/api/discounts/", discount_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    discount_id = response.data["id"]
    assert Discount.objects.filter(id=discount_id).exists() is True


@pytest.mark.django_db
def test_patch_discount_as_employee(get_token_for_user):
    """Тестируем обновление скидки для сотрудника"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    # Создаем скидку
    discount_data = {
        "name": "discount1",
        "description": "test discount",
        "discount_percent": 10,
        "active": True,
    }
    create_response = client.post("/api/discounts/", discount_data, format="json")
    assert create_response.status_code == status.HTTP_201_CREATED
    discount_id = create_response.data["id"]

    # Обновляем скидку
    update_data = {
        "name": "Updated Discount",
        "description": "Updated description",
        "discount_percent": 20,
        "active": False,
    }
    patch_response = client.patch(
        f"/api/discounts/{discount_id}/", update_data, format="json"
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["name"] == "Updated Discount"
    assert patch_response.data["description"] == "Updated description"
    assert patch_response.data["discount_percent"] == 20
    assert patch_response.data["active"] is False


@pytest.mark.django_db
def test_delete_discount_as_employee(get_token_for_user):
    """Тестируем удаление скидки для сотрудника"""
    token_employee, token_customer, token_supplier, client = get_token_for_user
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token_employee)

    # Создаем скидку
    discount_data = {
        "name": "discount1",
        "description": "test discount",
        "discount_percent": 10,
        "active": True,
    }
    create_response = client.post("/api/discounts/", discount_data, format="json")
    assert create_response.status_code == status.HTTP_201_CREATED
    discount_id = create_response.data["id"]

    # Удаляем скидку
    delete_response = client.delete(f"/api/discounts/{discount_id}/")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Discount.objects.filter(id=discount_id).exists()
