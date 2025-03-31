from django.urls import path
from rest_framework import routers

from .views import ObtainJWTFromSessionView, UpdateUserRoleView, UsersmeViewSet, UsersViewSet, YandexAuthView

users = routers.DefaultRouter()

users.register("users", UsersViewSet, basename="users")
users.register("me", UsersmeViewSet, basename="me")

urlpatterns = [
    path(
        "update_user/<int:pk>/", UpdateUserRoleView.as_view(), name="update-user-role"
    ),
    path("auth/yandex/", YandexAuthView.as_view(), name="yandex-auth"),
    path("auth/token_from_session/", ObtainJWTFromSessionView.as_view(), name="token-from-session"),
]

urlpatterns += users.urls
