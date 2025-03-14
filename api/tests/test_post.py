from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

class AuthTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователя, который будет использоваться для запроса токена
        self.user_employee = {
            "email": "user@e222xamp222l21e.com",
            "username": "str22221222ing",
            "role": "employee",
            "password": "strin2222g22212344",
            "first_name": "daj2fa",
            "last_name": "gfji2osjog",
            "phone": "4132324521",
            "salary": "1000"

            }
        self.user_supplier = {
            "email": "user@e32222xamp222l21e.com",
            "username": "str223222222ing",
            "role": "supplier",
            "password": "strin23222g222212344",
            "name": "str3ing",
            "contact_name": "stri3ng",
            "contact_phone": "33131313131",
            "address": "string"
            }
        self.user_customer = {
            "email": "user@2e2322xamp222l21e.com",
            "username": "str222322222ing",
            "role": "customer",
            "password": "strin3222g222212344",
            "phone_number": "314134142",
            "address": "string",
            "contact_name": "string",
            "company_name": "string",
            "country": "string"
            }
        # Создаем пользователя для получения токена
        self.client.post('/auth/users/', self.user_employee, format='json')
        self.client.post('/auth/users/', self.user_customer, format='json')
        self.client.post('/auth/users/', self.user_supplier, format='json')

        # Получаем токен
        response = self.client.post(
            '/auth/jwt/create/', 
            {
                "email": self.user_employee["email"],
                "password": self.user_employee["password"]
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.token_employee = response.data['access']

        response = self.client.post(
            '/auth/jwt/create/', 
            {
                "email": self.user_customer["email"],
                "password": self.user_customer["password"]
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.token_customer = response.data['access']

        response = self.client.post(
            '/auth/jwt/create/', 
            {
                "email": self.user_supplier["email"],
                "password": self.user_supplier["password"]
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.token_supplier = response.data['access']

        # получает id категории
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_employee)
        order_data = {"name": "category1"}
        response = self.client.post('/api/category/', order_data, format='json')
        self.category_id = response.data['id']
        #Создаём продукт
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_supplier)
        order_data = {
            "category": self.category_id,
            "name": "apple",
            "price": 100.00,
            "stock": 1000,
        }
        response = self.client.post('/api/products/', order_data, format='json')
        self.product_name1 = response.data['name']
        # 2-рой продукт для теста списка
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_supplier)
        order_data = {
            "category": self.category_id,
            "name": "apple1",
            "price": 100.00,
            "stock": 1000,
        }
        response = self.client.post('/api/products/', order_data, format='json')
        self.product_name2 = response.data['name']
        # Создаём промокод на скидку
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_employee)
        data = {
            "code": "code444",
            "discount_percentage": 34,
            "valid_from": "2025.01.01",
            "valid_to": "2026.01.01"
        }
        response = self.client.post('/api/discounts/', data, format='json')
        self.discount_code = response.data['code']

    def test_get_jwt_token(self):
        """Проверка получения JWT токенов"""
        self.assertIsNotNone(self.token_employee)
        self.assertIsNotNone(self.token_customer)
        self.assertIsNotNone(self.token_supplier)



    def test_create_category_as_employee(self):
        """Тестируем создание категории для сотрудника"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_employee)

        order_data = {
            "name": "category2"
        }
        response = self.client.post('/api/category/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    
    def test_create_product_as_supplier(self):
        """Тестируем создание продукта для поставщика"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_supplier)
        with open('tests/images/test_image.jpg', 'rb') as img:
            image = SimpleUploadedFile("test_image.jpg", img.read(), content_type="image/jpeg")
        with open('tests/videos/test_video.mp4', 'rb') as video:
            video = SimpleUploadedFile("test_video.mp4", video.read(), content_type="video/mp4")

        order_data = {
            "category": self.category_id,
            "name": "product1",
            "price": 100.00,
            "stock": 1000,
            "image": image,
            "video": video
        }
        response = self.client.post('/api/products/', order_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_order_as_customer(self):
        """Тестируем создание заказа для покупателя"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_customer)
        order_data = {
            "products": [
                {
                    "product": self.product_name1,
                    "quantity": 1
                },
                {
                    "product": self.product_name2,
                    "quantity": 2
                }
            ],
            "discount": self.discount_code,
        }
        response = self.client.post('/api/orders/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_review_order_as_customer(self):
        """Тестируем оценку заказа для покупателя"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_customer)
        order_data = {
            "product": self.product_name1,
            "rating": 5,
            "comment": "Good product"
        }
        response = self.client.post('/api/reviews/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_discount_order_as_employee(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_employee)
        data = {
            "code": "code4444",
            "discount_percentage": 34,
            "valid_from": "2025.01.01",
            "valid_to": "2026.01.01"
        }
        response = self.client.post('/api/discounts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)