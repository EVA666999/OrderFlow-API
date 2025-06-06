from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from youmoney_app.views import YooMoneyNotificationView, PaymentViewSet

from api_django.urls import api
from users.urls import users
from youmoney_app.urls import youmoney

security_definition = {
    "BearerAuth": openapi.Parameter(
        "Authorization",
        openapi.IN_HEADER,
        description="Bearer token для авторизации",
        type=openapi.TYPE_STRING,
    )
}

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
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api.urls)),
    path("users/", include("users.urls")),
    path("users/", include(users.urls)),
    # path("", include(youmoney.urls)),
    
    # Маршруты для работы с платежами
    path('api/yoomoney/notification/', YooMoneyNotificationView.as_view(), name='yoomoney_notification'),
    
    # Маршрут для перенаправления после успешной оплат
    
    path("chat/", include("aichat.urls")),
    path("auth/", include("social_django.urls", namespace="social")),
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