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


from social_django.utils import load_strategy
from social_core.exceptions import AuthException
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class YandexAuthView(APIView):
    def post(self, request):
        strategy = load_strategy(request)
        backend = "yandex-oauth2"

        try:
            user = request.backend.do_auth(request.data.get("access_token"))
            if user:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                )
        except AuthException:
            return Response({"error": "Ошибка авторизации"}, status=400)


class ObtainJWTFromSessionView(APIView):
    """
    Представление для получения JWT-токенов для аутентифицированного пользователя.
    Если пользователь успешно аутентифицирован (например, через social_django),
    то GET-запрос к этому endpoint вернет ему JWT-токены.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })