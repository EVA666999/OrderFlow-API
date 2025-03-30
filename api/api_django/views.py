import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Discount, Order, Product, ProductReview
from .permissions import (IsAdminOrCustomer, IsAdminOrEmployee,
                          IsAdminOrSupplier)
from .serializers import (CategorySerializer, DiscountSerializer,
                          OrderSerializer, ProductReviewSerializer,
                          ProductSerializer)

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    ordering_fields = ["pub_date", "total_price"]

    def list(self, request, *args, **kwargs):
        """Кэшируем список Заказов"""
        orders = cache.get("orders")
        if not orders:
            print("Кэш пуст, загружаем данные из базы.")
            orders = list(Order.objects.values())
            cache.set("orders", orders, timeout=600)
        else:
            print("Данные загружены из кэша.")
        return Response(orders)

    def perform_create(self, serializer):
        """
        Создаем заказ и отправляем данные через WebSocket.
        """

        # Сохраняем заказ, передавая промокод в контекст
        order = serializer.save(user=self.request.user)
        # send_order_confirmation_email(order)

        # Получаем канал
        channel_layer = get_channel_layer()

        # Подготовим данные о заказе
        order_details = {
            "order_id": order.id,
            "user": order.user.username,
            "total_price": float(order.total_price),
            "products": [
                {
                    "product__id": order_product.product.id,
                    "product__name": order_product.product.name,
                    "product__quantity": order_product.quantity,
                    "product__price": float(order_product.product.price),
                }
                for order_product in order.orderproduct_set.all()
            ],
        }

        # Отправляем данные через WebSocket
        async_to_sync(channel_layer.group_send)(  # Отправка через WebSocket
            "orders_group",  # Название группы
            {
                "type": "send_order_details",  # Тип события для consumer
                "order_details": order_details,
            },
        )

        order_cache = {
            "id": order.id,
            "user": order.user.username,
            "total_price": float(order.total_price),
            "products": [
                {
                    "product__id": order_product.product.id,
                    "product__name": order_product.product.name,
                    "quantity": order_product.quantity,
                    "product__price": float(order_product.product.price),
                }
                for order_product in order.orderproduct_set.all()
            ],
        }

        orders = cache.get("orders") or []
        print(f"Текущее содержимое кэша orders: {orders}")

        orders.append(order_cache)
        cache.set("orders", orders, timeout=600)

    def get_queryset(self):
        """
        Получаем заказы текущего пользователя.
        """
        return self.queryset.filter(user=self.request.user)

    def get_permissions(self):
        """
        Устанавливаем разрешения для разных действий.
        """
        if self.action == "create":
            return [IsAdminOrCustomer()]
        return super().get_permissions()

    def get_serializer_context(self):
        """
        Добавляем промокод в контекст для сериализатора.
        """
        context = super().get_serializer_context()
        context["discount"] = self.request.data.get("discount", None)
        return context


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    filter_backends = (filters.SearchFilter,)
    search_fields = ["name", "category__name"]
    ordering_fields = ["price", "pub_date"]
    ordering = ["price"]

    def list(self, request, *args, **kwargs):
        """Кэшируем список продуктов"""
        products = cache.get("products")
        if not products:
            products = list(Product.objects.values())
            cache.set("products", products, timeout=600)
        return Response(products)

    def perform_create(self, serializer):
        product = serializer.save()

        channel_layer = get_channel_layer()

        product_details = {
            "product_id": product.id,
            "category": product.category.name,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
        }

        async_to_sync(channel_layer.group_send)(
            "product_group",
            {
                "type": "send_product_details",
                "product_details": product_details,
            },
        )
        product_cache = {
            "product_id": product.id,
            "category": product.category.name,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
        }

        products = cache.get("products") or []
        print(f"Текущее содержимое кэша products: {products}")

        products.append(product_cache)
        cache.set("products", products, timeout=600)  # кэшируем данные за 10 мин

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAdminOrSupplier()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminOrSupplier()]
        return super().get_permissions()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        """Кэшируем список категорий"""
        categories = cache.get("categories")
        if not categories:
            categories = list(Category.objects.values())
            cache.set("categories", categories, timeout=600)
        return Response(categories)

    def perform_create(self, serializer):
        category = serializer.save()
        channel_layer = get_channel_layer()
        category_details = {"category_id": category.id, "name": category.name}

        async_to_sync(channel_layer.group_send)(
            "category_group",
            {
                "type": "send_category_details",
                "category_details": category_details,
            },
        )

    def get_permissions(self):
        """
        Определяем разрешения в зависимости от действия.
        """
        if self.action == "list" or self.action == "retrieve":
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAdminOrEmployee()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminOrEmployee()]
        return super().get_permissions()


class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAdminOrCustomer]

    def perform_create(self, serializer):
        review = serializer.save()
        channel_layer = get_channel_layer()

        review_details = {
            "review_id": review.id,
            "comment": review.comment,
            "rating": review.rating,
            "product": review.product.name,
        }

        async_to_sync(channel_layer.group_send)(
            "review_group",
            {
                "type": "send_review_details",
                "review_details": review_details,
            },
        )

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user)


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminOrEmployee]
