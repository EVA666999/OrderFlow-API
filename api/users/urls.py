from django.urls import path
from rest_framework import routers
from . import views
from users.views import YandexCallbackView
from .views import UpdateUserRoleView, UsersmeViewSet, UsersViewSet

users = routers.DefaultRouter()

users.register("users", UsersViewSet, basename="users")
users.register("me", UsersmeViewSet, basename="me")

urlpatterns = [
    path(
        "update_user/<int:pk>/", UpdateUserRoleView.as_view(), name="update-user-role"),
    path("callback/yandex/", YandexCallbackView.as_view(), name="yandex_callback"),
]

urlpatterns += users.urls
