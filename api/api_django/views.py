import os
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from dotenv import load_dotenv
from rest_framework import filters, viewsets
from .send_email import send_order_confirmation_email  

from rest_framework.permissions import IsAuthenticated


from .models import Category, Order, Product, ProductReview, Discount
from .permissions import (
    IsAdminOrCustomer,
    IsAdminOrEmployee,
    IsAdminOrSupplier,
    IsCustomer,
    IsAdmin,
    IsAuthor
)
from .serializers import (
    CategorySerializer,
    OrderSerializer,
    ProductSerializer,
    ProductReviewSerializer,
    DiscountSerializer
)

# Загрузка переменных окружения из файла .env
load_dotenv()

# Проверка, загрузился ли ключ
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    ordering_fields = ["pub_date", "total_price"]

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
            "total_price": order.total_price,
            "products": [
                {
                    "name": product.product.name,
                    "price": product.product.price,
                    "quantity": product.quantity,
                }
                for product in order.orderproduct_set.all()
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
        context['discount'] = self.request.data.get('discount', None)  # Добавляем промокод в контекст
        return context

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    filter_backends = (filters.SearchFilter,)  # Подключаем фильтр для поиска
    search_fields = ["name", "category__name"]  # Указываем поля для поиска
    ordering_fields = ["price", "pub_date"]  # Поля для сортировки
    ordering = ["price"]  # По умолчанию сортируем по цене
    
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

        async_to_sync(channel_layer.group_send)(  # Отправка через WebSocket
            "product_group",  # Название группы
            {
                "type": "send_product_details",
                "product_details": product_details,
            },
        )

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [
                IsAuthenticated()
            ]  # Все аутентифицированные пользователи могут просматривать продукты
        elif self.action == "create":
            return [IsAdminOrSupplier()]  # Только поставщик может создавать продукт
        elif self.action in ["update", "partial_update", "destroy"]:
            return [
                IsAdminOrSupplier()
            ]  # Только админ или сотрудник могут редактировать продукт
        return super().get_permissions()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def perform_create(self, serializerr):
        # Для создания категории - доступ только у админа
        category = serializerr.save()
        channel_layer = get_channel_layer()
        category_details = {
            "category_id": category.id,
            "name": category.name
        }

        async_to_sync(channel_layer.group_send)(  # Отправка через WebSocket
            "category_group",  # Название группы
            {
                "type": "send_category_details",  # Тип события для consumer
                "category_details": category_details,
            },
        )

    def get_permissions(self):
        """
        Определяем разрешения в зависимости от действия.
        """
        if self.action == "list" or self.action == "retrieve":
            return [
                IsAuthenticated()
            ]  # Все аутентифицированные пользователи могут просматривать продукты
        elif self.action == "create":
            # Для создания продукта - доступ только у поставщика
            return [IsAdminOrEmployee()]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Для редактирования и удаления продуктов - либо админ, либо сотрудник
            return [IsAdminOrEmployee()]  # Если админ или сотрудник
        return super().get_permissions()


class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsCustomer]

    def perform_create(self, serializer):
        serializer.save()
    
    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user)

class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminOrEmployee]