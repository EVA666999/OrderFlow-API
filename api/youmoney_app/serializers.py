from rest_framework import serializers

from .models import Payment

from api_django.models import Order

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'payment_id', 'amount', 'currency', 'status', 'created_at']
        read_only_fields = ['payment_id', 'amount', 'currency', 'status', 'created_at']
    
    def create(self, validated_data):
        order_id = validated_data.pop('order_id')
        try:
            order = Order.objects.get(id=order_id)
            return Payment.objects.create(order=order, **validated_data)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Указанный заказ не существует")