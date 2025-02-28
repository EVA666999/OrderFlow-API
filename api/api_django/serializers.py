from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Order, OrderProduct, Product

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ('id', 'category', 'name', 'price')

class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = OrderProduct
        fields = ('product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    products = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ('user', 'total_price', 'products')


    def get_products(self, obj):
        return list(
            OrderProduct.objects.filter(order=obj).values(
                'product__id', 
                'product__name',
                'quantity',
                'product__price'    
            )
        )

    def create(self, validated_data):
        products_data = self.initial_data.get('products', [])
        order = Order.objects.create(user=validated_data["user"])

        total_price = 0

        for product_data in products_data:
            product = Product.objects.get(id=product_data["product"])
            quantity = product_data["quantity"]
            OrderProduct.objects.create(order=order, product=product, quantity=quantity)

            total_price += product.price * quantity

        order.total_price = total_price
        order.save()
        return order


