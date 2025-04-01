from django.urls import path
from rest_framework import routers
from . import views

from .views import UpdateUserRoleView, UsersmeViewSet, UsersViewSet

users = routers.DefaultRouter()

users.register("users", UsersViewSet, basename="users")
users.register("me", UsersmeViewSet, basename="me")

urlpatterns = [
    path(
        "update_user/<int:pk>/", UpdateUserRoleView.as_view(), name="update-user-role"
    ),
    path('auth/complete/yandex-oauth2/', views.yandex_oauth_complete, name='yandex_oauth_complete'),
]

urlpatterns += users.urls
