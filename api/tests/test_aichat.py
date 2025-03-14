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
        self.client.post('/auth/users/', self.user_employee, format='json')

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

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_employee)
        order_data = {"name": "category1"}
        response = self.client.post('/api/category/', order_data, format='json')
        self.category_id = response.data['id']

    def test_aichat(self):
        # Проверяем доступ к чату только для сотрудников
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_employee)
        data = {
            "message": "Выведи название категории и id 1"
        }
        response = self.client.post('/chat/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)