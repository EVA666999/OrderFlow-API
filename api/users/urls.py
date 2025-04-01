from django.urls import path
from rest_framework import routers
from . import views
from .views import YandexOAuthView, UpdateUserRoleView, UsersmeViewSet, UsersViewSet, YandexLoginView

users = routers.DefaultRouter()

users.register("users", UsersViewSet, basename="users")
users.register("me", UsersmeViewSet, basename="me")

urlpatterns = [
    path(
        "update_user/<int:pk>/", UpdateUserRoleView.as_view(), name="update-user-role"),
    path("yandex-login/", YandexOAuthView.as_view(), name="yandex_login"),
    path("login/yandex/", YandexLoginView.as_view(), name="yandex_login"),
]

urlpatterns += users.urls