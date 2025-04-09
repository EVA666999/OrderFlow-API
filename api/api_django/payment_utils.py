import uuid
from yoomoney import Client, Quickpay
from django.conf import settings
from .models import Payment

def create_payment(order):
    """
    Создает платеж в YooMoney и возвращает URL для перенаправления
    """
    # Генерируем уникальный идентификатор платежа
    payment_id = str(uuid.uuid4())
    
    # Создаем запись о платеже в базе данных
    payment = Payment.objects.create(
        order=order,
        payment_id=payment_id,
        amount=order.total_price,
        status=Payment.PENDING
    )
    
    # Формируем URL для возврата
    return_url = settings.YOOMONEY_REDIRECT_URL
    
    # Создаем платеж в YooMoney
    quickpay = Quickpay(
        receiver=settings.YOOMONEY_ACCOUNT,
        quickpay_form="shop",
        targets=f"Оплата заказа №{order.id}",
        paymentType="SB",
        sum=float(order.total_price),
        label=payment_id,
        successURL=return_url
    )
    
    # Возвращаем URL для оплаты и сам объект платежа
    return quickpay.redirected_url, payment

def check_payment_status(payment_id):
    """
    Проверяет статус платежа по его идентификатору
    """
    try:
        client = Client(settings.YOOMONEY_TOKEN)
        history = client.operation_history(label=payment_id)
        
        for operation in history.operations:
            if operation.label == payment_id:
                payment = Payment.objects.get(payment_id=payment_id)
                
                if operation.status == "success":
                    payment.status = Payment.SUCCEEDED
                    payment.save()
                    return True
                elif operation.status == "canceled":
                    payment.status = Payment.CANCELED
                    payment.save()
        
        return False
    except Exception as e:
        print(f"Error checking payment status: {e}")
        return False