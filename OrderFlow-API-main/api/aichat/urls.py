from django.urls import path

from . import views

urlpatterns = [
    path("", views.chat_with_ai, name="chat_api"),
]
