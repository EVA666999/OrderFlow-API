from decimal import Decimal

from rest_framework import serializers

from .models import (Category, Discount, Order, OrderProduct, Product,
                     ProductReview)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    # comment = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="name"
    )

    class Meta:
        model = Product
        fields = ("id", "category", "name", "price", "stock", "video", "image")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["price"] = float(instance.price)
        representation["stock"] = float(instance.stock)
        return representation


class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(), slug_field="name"
    )
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = OrderProduct
        fields = ("product", "quantity")


class DiscountSerializer(serializers.ModelSerializer):
    valid_from = serializers.DateField(input_formats=["%Y.%m.%d"])
    valid_to = serializers.DateField(input_formats=["%Y.%m.%d"])

    class Meta:
        model = Discount
        fields = [
            "id",
            "code",
            "discount_percentage",
            "valid_from",
            "valid_to",
            "is_active",
        ]


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
        fields = (
            "id",
            "user",
            "total_price",
            "products",
            "products_data",
            "discount",
            "discount_amount",
        )

    def get_products_data(self, obj):
        products_data = list(
            OrderProduct.objects.filter(order=obj).values(
                "product__id", "product__name", "quantity", "product__price"
            )
        )
        # Приводим поле product__price к float, чтобы JSON смог его сериализовать
        for product in products_data:
            product["product__price"] = float(product["product__price"])
        return products_data


    def get_discount_amount(self, obj):
        """
        Метод для вычисления скидки на основе промокода.
        Возвращает скидку в виде процента или сообщение о проблемах с промокодом.
        """
        discount_code = self.context.get("discount")  # Получаем промокод из контекста

        if discount_code:
            discount_obj = Discount.objects.filter(
                code=discount_code
            ).first()  # Ищем по коду
            if discount_obj and discount_obj.is_active:
                return f"Скидка: {discount_obj.discount_percentage}%"  # Возвращаем скидку как строку
            else:
                return "Промокод не активен или не существует."  # Текстовое сообщение при неактивном промокоде
        return "Промокод не передан или не найден."  # Если промокод не передан

    def create(self, validated_data):
        products_data = validated_data.pop("products", [])
        discount_obj = validated_data.pop("discount", None)

        order = Order.objects.create(user=validated_data["user"])
        total_price = Decimal(0)

        for product_data in products_data:
            product = product_data["product"]
            quantity = product_data["quantity"]

            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Недостаточно {product.name} на складе!"
                )

            product.stock -= quantity
            product.save()

            OrderProduct.objects.create(order=order, product=product, quantity=quantity)
            total_price += Decimal(product.price) * Decimal(quantity)  #ок

        # Проверяем скидку
        discount_percentage = discount_obj.discount_percentage if discount_obj else 0
        discount_amount = (total_price * Decimal(discount_percentage)) / Decimal(100)
        total_price -= discount_amount

        order.total_price = float(total_price)
        order.discount = discount_obj
        order.save()

        return order

    def update(self, instance, validated_data):
        # Извлекаем данные продуктов, если они есть
        products_data = validated_data.pop("products", [])
        discount_obj = validated_data.pop("discount", None)

        # Получаем заказ по ID
        order = instance

        total_price = Decimal("0.00")  # Начинаем с нулевой суммы

        for product in products_data:
            product_instance = product.get("product")
            quantity = product.get("quantity")

            if quantity > product_instance.stock:
                raise serializers.ValidationError(
                    f"Недостаточно {product_instance.name} на складе!"
                )

            # Обновляем количество товара на складе
            product_instance.stock -= quantity
            product_instance.save()

            # Обновляем или создаем связь товара с заказом
            OrderProduct.objects.update_or_create(
                order=order, product=product_instance, defaults={"quantity": quantity}
            )
            total_price += Decimal(product_instance.price) * Decimal(quantity)

        # Обновляем итоговую цену заказа
        if discount_obj:
            discount_percentage = discount_obj.discount_percentage
        else:
            discount_percentage = 0

        discount_amount = (total_price * Decimal(discount_percentage)) / Decimal(100)
        total_price -= discount_amount

        order.total_price = float(total_price)
        order.discount = discount_obj  # Применяем скидку к заказу
        order.save()

        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["total_price"] = float(instance.total_price)
        representation["discount"] = self.context.get("discount")
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
        data["customer"] = instance.customer.username
        return data
