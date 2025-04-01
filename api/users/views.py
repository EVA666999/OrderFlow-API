import uuid
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
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
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
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    

class YandexOAuthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        
        token_response = self._get_oauth_token(code)
        
        user_info = self._get_user_info(token_response['access_token'])
        
        user = self._get_or_create_user(user_info)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user_id': user.id,
            'email': user.email,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'username': user.username
        })
    

    def _get_oauth_token(self, code):
        token_url = 'https://oauth.yandex.ru/token'
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': 'e54a436087b2456a9893e77d01592337',
            'client_secret': '0b75eb2e67d04c8eaa011c59ac5bb2aa',
            'redirect_uri': 'http://vasilekretsu.ru/users/callback/yandex/',
        }
        
        response = requests.post(token_url, data=token_data)
        
        # print("Token Response Status:", response.status_code)
        # print("Token Response Content:", response.text)
    
        return response.json() if response.status_code == 200 else None
    def _get_user_info(self, access_token):
        user_info_url = 'https://login.yandex.ru/info'
        headers = {'Authorization': f'OAuth {access_token}'}

        response = requests.get(user_info_url, headers=headers)
        return response.json() if response.status_code == 200 else None
    
    def _get_or_create_user(self, user_info):
        email = user_info.get('default_email')
        username = user_info.get('login')
        yandex_id = user_info.get('id')

        try:
            user = User.objects.get(yandex_oauth_id=yandex_id)
        except User.DoesNotExist:
            user = User.objects.create_user(email=email, 
                                            username=username, 
                                            password=str(uuid.uuid4()),
                                            role='user',
                                            yandex_oauth_id=yandex_id,
                                            is_active=True)
        if not user.is_active:
            user.is_active = True
            user.save()
        
        return user

class YandexLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client_id = 'e54a436087b2456a9893e77d01592337'
        redirect_uri = 'http://vasilekretsu.ru/users/callback/yandex/'

        yandex_oauth_url = (
            f"https://oauth.yandex.ru/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=login:email"
        )
        return redirect(yandex_oauth_url)
    

#http://vasilekretsu.ru/users/login/yandex/