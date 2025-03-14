from django.contrib.auth import get_user_model
from django.forms import ValidationError
from rest_framework import serializers
from decimal import Decimal

from .models import Category, Order, OrderProduct, Product, ProductReview, Discount, PurchaseHistory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    # comment = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ("id", "category", "name", "price", "stock", "video", 'image')

    # def get_comment(self, obj):
    #     reviews = ProductReview.objects.filter(product=obj)
    #     if reviews.exists():
    #         return [review.comment for review in reviews]
    #     else:
    #         return f"Количество коментариев {len(reviews)}"


class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(), slug_field="name"
    )
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = OrderProduct
        fields = ("product", "quantity")

class DiscountSerializer(serializers.ModelSerializer):
    valid_from = serializers.DateField(input_formats=['%Y.%m.%d'])
    valid_to = serializers.DateField(input_formats=['%Y.%m.%d'])
    class Meta:
        model = Discount
        fields = ['code', 'discount_percentage', 'valid_from', 'valid_to', 'is_active']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    products = OrderProductSerializer(many=True, write_only=True)  # Для записи
    products_data = serializers.SerializerMethodField()  # Для чтения
    discount = serializers.SlugRelatedField(
        queryset=Discount.objects.all(), slug_field="code", required=False
    )
    discount_amount = serializers.SerializerMethodField()  # Для скидки

    class Meta:
        model = Order
        fields = ("id", "user", "total_price", "products", "products_data", "discount", "discount_amount")

    def get_products_data(self, obj):  # Исправил название метода
        return list(
            OrderProduct.objects.filter(order=obj).values(
                "product__id", "product__name", "quantity", "product__price"
            )
        )
    
    def get_discount_amount(self, obj):
        """
        Метод для вычисления скидки на основе промокода.
        Возвращает скидку в виде процента или сообщение о проблемах с промокодом.
        """
        discount_code = self.context.get('discount')  # Получаем промокод из контекста

        if discount_code:
            discount_obj = Discount.objects.filter(code=discount_code).first()  # Ищем по коду
            if discount_obj and discount_obj.is_active:
                return f"Скидка: {discount_obj.discount_percentage}%"  # Возвращаем скидку как строку
            else:
                return "Промокод не активен или не существует."  # Текстовое сообщение при неактивном промокоде
        return "Промокод не передан или не найден."  # Если промокод не передан

    def create(self, validated_data):
        products_data = validated_data.pop("products", [])  # Извлекаем продукты
        discount_code = validated_data.pop("discount", None)  # Получаем промокод
        order = Order.objects.create(user=validated_data["user"])

        total_price = Decimal(0)

        for product_data in products_data:
            product = product_data["product"]
            quantity = product_data["quantity"]

            # Проверка на наличие товара
            if product.stock < quantity:
                raise serializers.ValidationError(f"Недостаточно {product.name} на складе!")
            # elif discount_code != product.discount:
            #     raise serializers.ValidationError(f"Промокод не совпадает с ценой товара {product.name}!")

            # Уменьшаем stock
            product.stock -= quantity
            product.save()

            # Создаём связь с заказом
            OrderProduct.objects.create(order=order, product=product, quantity=quantity)

            total_price += Decimal(product.price) * Decimal(quantity)

            PurchaseHistory.objects.create(
                user=order.user,
                order=order,
                product=product,
                price=product.price,
                quantity=quantity
            )

        # Если промокод передан, проверим его
        discount_percentage = 0
        if discount_code:
            discount_obj = Discount.objects.filter(code=discount_code, is_active=True).first()
            if discount_obj:
                discount_percentage = discount_obj.discount_percentage

        discount_amount = (total_price * Decimal(discount_percentage)) / Decimal(100)
        total_price -= discount_amount

        order.total_price = total_price
        order.save()

        return order

    def to_representation(self, instance):
        """
        Переписываем метод to_representation для того, чтобы передать `discount` в контекст сериализатора
        """
        representation = super().to_representation(instance)
        representation['discount'] = self.context.get('discount')  # Передаем промокод в контекст
        return representation


class ProductReviewSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(), slug_field="name"
    )
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ProductReview
        fields = [
            "id",
            "product",
            "customer",
            "rating",
            "comment",
            "created_at",
            "sentiment",
            "video",
            "image",
        ]

    def create(self, valdate_data):
        product_name = valdate_data.get("product")
        product = Product.objects.get(name=product_name)
        valdate_data["product"] = product
        return super().create(valdate_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product_id"] = instance.product.id  # Выводим имя пользователя вместо ID
        return data
