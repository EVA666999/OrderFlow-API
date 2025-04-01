from django.urls import path
from rest_framework import routers
from . import views
from users.views import YandexLoginView, YandexCallbackView
from .views import UpdateUserRoleView, UsersmeViewSet, UsersViewSet

users = routers.DefaultRouter()

users.register("users", UsersViewSet, basename="users")
users.register("me", UsersmeViewSet, basename="me")

urlpatterns = [
    path(
        "update_user/<int:pk>/", UpdateUserRoleView.as_view(), name="update-user-role"),
    path("login/yandex/", YandexLoginView.as_view(), name="yandex_login"),
    path("callback/yandex/", YandexCallbackView.as_view(), name="yandex_callback"),
]

urlpatterns += users.urls
