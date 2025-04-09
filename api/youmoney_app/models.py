from django.db import models
from api_django.models import Order

class Payment(models.Model):
    PENDING = 'pending'
    SUCCEEDED = 'succeeded'
    CANCELED = 'canceled'
    
    STATUS_CHOICES = [
        (PENDING, 'В ожидании'),
        (SUCCEEDED, 'Успешно'),
        (CANCELED, 'Отменено'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Платеж {self.payment_id} для заказа {self.order.id}"