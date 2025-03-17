from django.urls import re_path

from .consumers import (CategoryConsumer, OrderConsumer, ProductConsumer,
                        ReviewConsumer)

websocket_urlpatterns = [
    re_path(r"ws/orders/$", OrderConsumer.as_asgi()),
    re_path(r"ws/categories/$", CategoryConsumer.as_asgi()),
    re_path(r"ws/products/$", ProductConsumer.as_asgi()),
    re_path(r"ws/reviews/$", ReviewConsumer.as_asgi()),
]
