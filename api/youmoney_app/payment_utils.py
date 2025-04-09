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

def check_payment_status(payment_id):
    """
    Проверяет статус платежа в YooMoney и обновляет его в базе данных
    Возвращает True, если платеж успешно выполнен, иначе False
    """
    try:
        # Проверяем есть ли платеж в нашей БД
        payment = Payment.objects.get(payment_id=payment_id)
        
        # Если платеж уже обработан как успешный, просто возвращаем True
        if payment.status == Payment.SUCCEEDED:
            return True
            
        # Если платеж уже обработан как отмененный, просто возвращаем False
        if payment.status == Payment.CANCELED:
            return False
            
        # Проверяем статус в YooMoney
        client = Client(settings.YOOMONEY_TOKEN)
        
        # Получаем историю операций
        operations = client.operation_history(label=payment_id)
        
        # Если операций нет, платеж еще не выполнен
        if not operations.operations:
            return False
            
        # Берем последнюю операцию с нашей меткой
        for operation in operations.operations:
            if operation.label == payment_id:
                # Проверка статуса операции
                if operation.status == 'success':
                    # Обновляем статус платежа в БД
                    payment.status = Payment.SUCCEEDED
                    payment.save()
                    
                    # Здесь можно добавить обновление статуса заказа
                    # order = payment.order
                    # order.status = ...
                    # order.save()
                    
                    return True
                elif operation.status in ['refused', 'canceled']:
                    payment.status = Payment.CANCELED
                    payment.save()
                    return False
                    
        # Если не нашли операцию со статусом success/refused/canceled, значит платеж в процессе
        return False
        
    except Payment.DoesNotExist:
        # Если платеж не найден в нашей БД
        return False
    except Exception as e:
        # В случае ошибки при обращении к API YooMoney или других проблем
        # Логируем ошибку и считаем платеж неуспешным
        print(f"Ошибка при проверке статуса платежа: {str(e)}")
        return False