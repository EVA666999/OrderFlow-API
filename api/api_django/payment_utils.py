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

import time

def check_payment_status(payment_id):
    """
    Проверяет статус платежа по его идентификатору с несколькими попытками
    """
    try:
        client = Client(settings.YOOMONEY_TOKEN)

        # Делаем до 3 попыток получить операции по метке
        operations = None
        for i in range(3):
            operations = client.operation_history(label=payment_id)
            if operations.operations:
                break
            print(f"Попытка {i+1}: операций нет, жду 2 секунды...")
            time.sleep(2)

        if not operations or not operations.operations:
            print("Операции не найдены вообще.")
            return False

        for operation in operations.operations:
            print(f"Найдена операция: label={operation.label}, status={operation.status}")
            if operation.label == payment_id:
                payment = Payment.objects.get(payment_id=payment_id)

                if operation.status == "success":
                    payment.status = Payment.SUCCEEDED
                    payment.save()
                    return True
                elif operation.status in ["canceled", "refused"]:
                    payment.status = Payment.CANCELED
                    payment.save()
                    return False

        print("Операция с нужным label не найдена.")
        return False

    except Payment.DoesNotExist:
        print(f"Платёж с ID {payment_id} не найден в базе.")
        return False
    except Exception as e:
        print(f"Ошибка при проверке статуса платежа: {e}")
        return False