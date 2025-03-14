from rest_framework.test import APITestCase
from rest_framework import status

class AuthTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователя, который будет использоваться для запроса токена
        self.user_employee = {
            "email": "user@e22xamp222l21e.com",
            "username": "str2221222ing",
            "role": "employee",
            "password": "strin222g22212344",
            "first_name": "dajfa",
            "last_name": "gfjiosjog",
            "phone": "4132324521",
            "salary": "1000"

            }
        self.user_customer = {
            "email": "user@2e222xamp222l21e.com",
            "username": "str22222222ing",
            "role": "customer",
            "password": "strin222g222212344",
            "phone_number": "31414142",
            "address": "string",
            "contact_name": "string",
            "company_name": "string",
            "country": "string"
            }
        # Создаем пользователя для получения токена
        self.client.post('/auth/users/', self.user_employee, format='json')
        self.client.post('/auth/users/', self.user_customer, format='json')

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

    def test_get_jwt_token(self):
        """Проверка получения JWT токена"""
        # Этот тест можно оставить пустым, так как логика получения токена уже включена в setUp()

        # Просто проверим, что токен был сохранен
        self.assertIsNotNone(self.token_employee)
        self.assertIsNotNone(self.token_customer)

    def test_protected_endpoints_for_customers(self):
        """Тестируем защищённые эндпоинты (категории и другие)"""
        # Используем полученный токен для доступа к защищенному ресурсу
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_customer)

        # Проверяем доступ к эндпоинту заказов
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем доступ к эндпоинту продуктов
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем доступ к эндпоинту категорий
        response = self.client.get('/api/category/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

         # Проверяем доступ к эндпоинту отзывов
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

