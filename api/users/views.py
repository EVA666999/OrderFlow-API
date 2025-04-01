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
from django.http import JsonResponse
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
    

class YandexCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': 'No code received from Yandex OAuth'}, status=400)
        
        token_url = "https://oauth.yandex.ru/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": YANDEX_CLIENT_ID,
            "client_secret": YANDEX_CLIENT_SECRET,
        }

        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to get access token from Yandex'}, status=500)
        token_data = response.json()
        access_token = token_data.get('access_token')

        user_info_url = f"https://api.yandex.ru/user/info?oauth_token={access_token}"
        response = requests.get(user_info_url)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to get user info from Yandex'}, status=500)
        
        user_info_url = "https://login.yandex.ru/info"
        headers = {"Authorization": f"OAuth {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code != 200:
            return Response({"error": "Failed to get user info", "details": user_info_response.json()}, status=400)

        user_info = user_info_response.json()

        # Тут можно добавить логику по созданию или поиску пользователя в базе
        return Response({"user_info": user_info, "access_token": access_token})