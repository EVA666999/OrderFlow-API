from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from django.conf import settings
from api_django.urls import api
from users.urls import users
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api.urls)),
    path("users/", include(users.urls)),
    path("users/", include("users.urls")),
    path("chat/", include("aichat.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path(
        "ws_orders/", TemplateView.as_view(template_name="orders.html"), name="orders"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)