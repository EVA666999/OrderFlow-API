from django.views import View
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests

YANDEX_CLIENT_ID = settings.SOCIAL_AUTH_YANDEX_OAUTH2_KEY
YANDEX_CLIENT_SECRET = settings.SOCIAL_AUTH_YANDEX_OAUTH2_SECRET
# Исправляем URI редиректа, чтобы он соответствовал вашему обработчику
YANDEX_REDIRECT_URI = "http://vasilekretsu.ru/users/callback/yandex/"

class YandexLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        yandex_auth_url = (
            f"https://oauth.yandex.ru/authorize?"
            f"response_type=code&client_id={YANDEX_CLIENT_ID}&redirect_uri={YANDEX_REDIRECT_URI}"
        )
        return redirect(yandex_auth_url)
    

class YandexCallbackView(View):
    def get(self, request, *args, **kwargs):
        # Получаем код авторизации
        code = request.GET.get('code')

        # Отправляем запрос на обмен кода на токен
        response = requests.post(
            'https://oauth.yandex.ru/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': 'e54a436087b2456a9893e77d01592337',  # замените на ваш CLIENT_ID
                'client_secret': '0b75eb2e67d04c8eaa011c59ac5bb2aa',  # замените на ваш CLIENT_SECRET
                'redirect_uri': 'http://vasilekretsu.ru/users/callback/yandex/',  # проверьте redirect_uri
            }
        )

        # Проверка статуса ответа
        if response.status_code != 200:
            # Если ошибка, выводим ответ и статус
            print(f"Error response from Yandex: {response.status_code} - {response.text}")
            return HttpResponse("Error during OAuth2 authentication", status=500)

        try:
            # Попытка распарсить JSON ответ
            data = response.json()
            # Выводим полученные данные для отладки
            print("YANDEX RESPONSE:", data)
        except requests.exceptions.JSONDecodeError:
            # Ловим ошибку, если ответ не JSON
            print(f"Failed to parse JSON response: {response.text}")
            return HttpResponse("Failed to parse Yandex response", status=500)

        # Дальше обработка данных (например, сохранение токена или запрос к /info для получения данных пользователя)
        # Вернуть успешный ответ, если все прошло хорошо
        return HttpResponse("Yandex OAuth2 Callback success")
    
#http://vasilekretsu.ru/users/login/yandex/