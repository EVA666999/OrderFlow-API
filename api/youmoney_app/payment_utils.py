import uuid
import logging
from yoomoney import Client, Quickpay
from django.conf import settings
from .models import Payment

import logging

logger = logging.getLogger('payments')

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
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        order = payment.order

        client = Client(settings.YOOMONEY_TOKEN)
        history = client.operation_history(label=payment_id)

        # Добавляем логирование всех операций
        if history.operations:
            for op in history.operations:
                logger.debug(f"Операция: label={op.label}, статус={op.status}, сумма={op.amount}")
        else:
            logger.info("Операций не найдено в истории")

        if history.operations:
            operation = history.operations[0]
            # Если API возвращает, например, 'succeeded' вместо 'success', можно отладить это тут:
            logger.info(f"Проверяем статус операции: {operation.status}")

            if operation.status == 'success':
                if float(operation.amount) >= float(payment.amount):
                    payment.status = Payment.SUCCEEDED
                    payment.save()
                    order.status = 'paid'
                    order.save()
                    return True

        return False
    except Payment.DoesNotExist:
        logger.error(f"Платеж {payment_id} не найден")
        return False
    except Exception as e:
        logger.error(f"Ошибка в check_payment_status: {str(e)}")
        return False
    
