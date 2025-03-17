from rest_framework import routers

from .views import (CategoryViewSet, DiscountViewSet, OrderViewSet,
                    ProductReviewViewSet, ProductViewSet)

api = routers.DefaultRouter()
api.register(r"orders", OrderViewSet, basename="orders")
api.register(r"products", ProductViewSet, basename="prioducts")
api.register(r"category", CategoryViewSet, basename="categoty")
api.register(r"reviews", ProductReviewViewSet, basename="product_reviews")
api.register(r"discounts", DiscountViewSet, basename="discounts")
