from django.views import View
import jwt
import requests
from rest_framework import viewsets
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from social_django.utils import load_strategy
from social_core.exceptions import AuthException
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api_django.models import User
from api_django.permissions import IsAdminOrAuthenticated
from rest_framework import status
from .models import User
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserUpdateSerializer,
    Usersermeializer,
)


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = [IsAuthenticated]


class UpdateUserRoleView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserUpdateSerializer
    permission_classes = [IsAdminOrAuthenticated]  # Только админы могут менять роли


class UsersmeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = Usersermeializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
def get_yandex_auth_url():
    client_id = 'e54a436087b2456a9893e77d01592337'  # Заменить на свой client_id, полученный от Яндекса
    redirect_uri = 'http://vasilekretsu.ru/users/callback/yandex/'  # Этот URL должен совпадать с тем, что указан в настройках приложения на Яндексе
    scope = 'email'  # Права доступа, которые ты хочешь запросить
    response_type = 'code'  # Мы будем получать код для обмена на токен

    auth_url = f"https://oauth.yandex.ru/authorize?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"

    return auth_url

    
# Функция для получения информации о пользователе из Яндекса с использованием OAuth токена
def get_user_info_from_yandex(oauth_token):
    url = 'https://login.yandex.ru/info?format=jwt'
    headers = {'Authorization': f'OAuth {oauth_token}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error response from Yandex: {response.status_code} - {response.text}")
        return None
    
    try:
        # Получаем JWT, который нужно декодировать
        data = response.json()
        print("Yandex User Info JWT:", data)
        return data
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to parse JSON response: {response.text}")
        return None

# Функция для декодирования JWT
def decode_jwt(encoded_jwt):
    try:
        # Декодируем JWT без проверки подписи
        decoded = jwt.decode(encoded_jwt, options={"verify_signature": False})
        print("Decoded JWT:", decoded)
        return decoded
    except jwt.InvalidTokenError as e:
        print(f"Error decoding JWT: {e}")
        return None
    
# Пример представления, которое будет обрабатывать callback от Яндекса
class YandexCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        # Получаем код из параметров запроса (например, в redirect_uri)
        code = request.GET.get('code', None)

        if not code:
            return Response({"error": "Authorization code not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Здесь ты должен обменять код на токен (это может быть сделано с помощью запроса к Яндексу)
        oauth_token = self.get_oauth_token(code)

        if not oauth_token:
            return Response({"error": "Failed to get OAuth token"}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем информацию о пользователе из Яндекса
        user_info = get_user_info_from_yandex(oauth_token)
        if not user_info:
            return Response({"error": "Failed to retrieve user information from Yandex"}, status=status.HTTP_400_BAD_REQUEST)

        # Декодируем JWT
        decoded_info = decode_jwt(user_info)

        return Response(decoded_info, status=status.HTTP_200_OK)
    
    def get_oauth_token(self, code):
        url = 'https://oauth.yandex.ru/token'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': 'your_client_id',
            'client_secret': 'your_client_secret',
            'redirect_uri': 'http://vasilekretsu.ru/users/callback/yandex/',  # Убедись, что redirect_uri совпадает с тем, что ты указал в Яндекс приложении
        }
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            return response.json().get('access_token')
        
        print(f"Error exchanging code for token: {response.status_code} - {response.text}")
        return None

#http://vasilekretsu.ru/users/login/yandex/