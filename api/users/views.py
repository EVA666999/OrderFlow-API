from rest_framework import viewsets
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

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
