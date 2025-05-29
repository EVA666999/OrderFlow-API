# yourapp/middleware.py
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Получаем заголовок авторизации
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                # Извлекаем токен из заголовка
                token = auth_header.split(' ')[1]  # "Bearer <token>"
                
                # Декодируем токен, используя SECRET_KEY
                decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                
                # Получаем пользователя из базы данных
                user = get_user_model().objects.get(id=decoded_payload['user_id'])
                request.user = user  # Сохраняем пользователя в запросе

            except (jwt.ExpiredSignatureError, jwt.DecodeError, KeyError, get_user_model().DoesNotExist):
                # В случае ошибки валидации токена или отсутствия пользователя, возвращаем ошибку
                return JsonResponse({'error': 'Invalid or expired token'}, status=401)
                
        # Если заголовка авторизации нет, просто продолжаем выполнение
        return None
