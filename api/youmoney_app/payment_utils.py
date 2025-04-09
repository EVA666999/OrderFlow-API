import json
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
    """
    Проверка статуса платежа через YooMoney API
    """
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        order = payment.order

        client = Client(settings.YOOMONEY_TOKEN)
        history = client.operation_history(label=payment_id)

        # Логируем тип и содержимое history для отладки
        logger.debug("Тип history: %s", type(history))
        logger.debug("Содержимое history: %s", history)

        # Если history не является словарем, пытаемся привести его к dict
        if not isinstance(history, dict):
            try:
                # Приводим к строке и пробуем распарсить JSON
                history = json.loads(str(history))
            except Exception as ex:
                logger.error(f"Не удалось преобразовать историю в dict: {ex}. История: {history}")
                return False

        # Предполагаем, что history теперь словарь с ключом "operations"
        operations = history.get("operations", [])
        if operations:
            for op in operations:
                logger.debug(f"Операция: label={op.get('label')}, статус={op.get('status')}, сумма={op.get('amount')}")
            operation = operations[0]
            logger.info(f"Проверяем статус операции: {operation.get('status')}")
            print(f"Проверяем статус операции: {operation.get('status')}")

            if operation.get('status') in ['success', 'succeeded']:
                if float(operation.get('amount')) >= float(payment.amount):
                    payment.status = Payment.SUCCEEDED
                    payment.save()
                    order.status = 'paid'
                    order.save()
                    return True
        else:
            logger.info("Операций не найдено в истории")

        return False

    except Payment.DoesNotExist:
        logger.error(f"Платеж {payment_id} не найден")
        return False
    except Exception as e:
        logger.error(f"Ошибка в check_payment_status: {str(e)}")
        return False
    
