from rest_framework import routers
from .views import OrderViewSet, ProductViewSet, CategoryViewSet

api = routers.DefaultRouter()
api.register('orders', OrderViewSet, basename='orders')
api.register('products', ProductViewSet, basename='prioducts')
api.register('category', CategoryViewSet, basename='categoty')