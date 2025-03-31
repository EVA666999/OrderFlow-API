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
def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Токен будет действителен 24 часа
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

# Представление для завершения авторизации через Яндекс
@psa('social:complete')
def yandex_oauth_complete(request, backend):
    try:
        # Получаем пользователя, который авторизовался через Яндекс
        user = request.backend.do_auth(request.GET.get('code'))

        # Генерируем JWT токен
        token = generate_jwt_token(user)

        # Возвращаем JWT токен в ответе
        return JsonResponse({'token': token})
    except AuthException as e:
        return JsonResponse({'error': str(e)}, status=400)