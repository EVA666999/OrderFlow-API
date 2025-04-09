import uuid
from yoomoney import Client, Quickpay
from django.conf import settings
from .models import Payment

def create_payment(order):
    """
    Создает платеж в YooMoney и возвращает URL для перенаправления
    """
    payment_id = str(uuid.uuid4())
    
    payment = Payment.objects.create(
        order=order,
        payment_id=payment_id,
        amount=order.total_price,
        status=Payment.PENDING
    )
    
    # API-ориентированный подход для redirect URL
    return_url = f"{settings.YOOMONEY_REDIRECT_URL}?label={payment_id}"
    
    quickpay = Quickpay(
        receiver=settings.YOOMONEY_ACCOUNT,
        quickpay_form="shop",
        targets=f"Оплата заказа №{order.id}",
        paymentType="SB",
        sum=float(order.total_price),
        label=payment_id,
        successURL=return_url
    )
    
    return quickpay.redirected_url, payment