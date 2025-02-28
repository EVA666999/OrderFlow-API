from rest_framework import serializers

from .models import Category, Order, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    total_price = serializers.SerializerMethodField()  # Считаем цену через метод
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_total_price(self, obj):
        return sum(product.price for product in obj.products.all())

    def create(self, validated_data):
        products_data = validated_data.pop('products', [])
        
        order = Order.objects.create(**validated_data)
        order.products.set(products_data)
        
        order.total_price = self.get_total_price(order)
        order.save()
        
        return order

    def update(self, instance, validated_data):
        products_data = validated_data.pop('products', [])
        
        instance = super().update(instance, validated_data)
        
        instance.products.set(products_data)
        
        instance.total_price = self.get_total_price(instance)
        instance.save()
        
        return instance



class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = '__all__'
##author = serializers.SlugRelatedField(slug_field="username",read_only=True)