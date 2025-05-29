from rest_framework import routers

from .views import (
    PaymentViewSet,
)

youmoney = routers.DefaultRouter()


youmoney.register(r"payments", PaymentViewSet, basename="payments")