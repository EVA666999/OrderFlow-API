from rest_framework import serializers

from .models import Category, Order, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # Включаем только необходимые поля


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    total_price = serializers.SerializerMethodField()  # Считаем цену через метод
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_total_price(self, obj):
        # Считаем total_price, суммируя цены всех продуктов в заказе
        return sum(product.price for product in obj.products.all())

    def create(self, validated_data):
        # Получаем список продуктов из запроса
        products_data = validated_data.pop('products', [])
        
        # Создаем заказ без продуктов
        order = Order.objects.create(**validated_data)

        # Добавляем продукты в заказ после того как заказ сохранен и имеет id
        order.products.set(products_data)  # Используем set для установки множества продуктов
        
        # Считаем total_price
        order.total_price = self.get_total_price(order)
        order.save()
        
        return order

    def update(self, instance, validated_data):
        products_data = validated_data.pop('products', [])
        
        # Обновляем заказ и устанавливаем новые данные
        instance = super().update(instance, validated_data)
        
        # Обновляем продукты в заказе
        instance.products.set(products_data)
        
        # Пересчитываем total_price
        instance.total_price = self.get_total_price(instance)
        instance.save()
        
        return instance



class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # показываем ID категории

    class Meta:
        model = Product
        fields = '__all__'
##author = serializers.SlugRelatedField(slug_field="username",read_only=True)