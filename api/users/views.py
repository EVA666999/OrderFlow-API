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
from datetime import datetime, timedelta

from social_django.utils import load_strategy
from social_core.exceptions import AuthException
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from social_django.utils import psa
from django.conf import settings
from django.http import JsonResponse
import jwt
from django.conf import settings

# Создаем JWT токен
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

YANDEX_CLIENT_ID = settings.SOCIAL_AUTH_YANDEX_OAUTH2_KEY
YANDEX_CLIENT_SECRET = settings.SOCIAL_AUTH_YANDEX_OAUTH2_SECRET
YANDEX_REDIRECT_URI = settings.SOCIAL_AUTH_YANDEX_OAUTH2_REDIRECT_URI


class YandexLoginView(APIView):
    """Перенаправляем пользователя на страницу авторизации Яндекса"""
    def get(self, request):
        yandex_auth_url = (
            f"https://oauth.yandex.ru/authorize?"
            f"response_type=code&client_id={YANDEX_CLIENT_ID}&redirect_uri={YANDEX_REDIRECT_URI}"
        )
        return redirect(yandex_auth_url)


class YandexAuthCallbackView(APIView):
    """Получаем токен, создаём пользователя и выдаём JWT"""
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return JsonResponse({"error": "Authorization code not provided"}, status=400)

        # Получаем access_token у Яндекса
        token_url = "https://oauth.yandex.ru/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": YANDEX_CLIENT_ID,
            "client_secret": YANDEX_CLIENT_SECRET,
        }
        response = requests.post(token_url, data=data)
        token_data = response.json()

        if "access_token" not in token_data:
            return JsonResponse({"error": "Failed to obtain access token"}, status=400)

        access_token = token_data["access_token"]

        # Получаем данные пользователя
        user_info_url = "https://login.yandex.ru/info"
        headers = {"Authorization": f"OAuth {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info = user_info_response.json()

        if "id" not in user_info:
            return JsonResponse({"error": "Failed to obtain user info"}, status=400)

        # Создаём пользователя или находим существующего
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=user_info["id"],
            defaults={
                "email": user_info.get("default_email", ""),
                "first_name": user_info.get("first_name", ""),
                "last_name": user_info.get("last_name", ""),
            },
        )

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        })
