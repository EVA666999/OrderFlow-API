from api_django.urls import api
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from users.urls import users

security_definition = {
    "BearerAuth": openapi.Parameter(
        "Authorization",  # Параметр для заголовка
        openapi.IN_HEADER,  # Указываем, что это заголовок
        description="Bearer token для авторизации",  # Описание
        type=openapi.TYPE_STRING,  # Тип данных
    )
}

# Создаем schema_view без security в get_schema_view
schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version="v1",
        description="Документация API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(AllowAny,),  # Открытый доступ для всех
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api.urls)),
    path("users/", include(users.urls)),
    path("users/", include("users.urls")),
    path("chat/", include("aichat.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-ui"),
    path(
        "swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"
    ),
    path(
        "ws_orders/", TemplateView.as_view(template_name="orders.html"), name="orders"
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
