import uuid
import logging
from yoomoney import Client, Quickpay
from django.conf import settings
from .models import Payment

logger = logging.getLogger(__name__)

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
    Проверка статуса платежа через ЮMoney API
    """
    try:
        # Находим платеж в базе данных
        payment = Payment.objects.get(payment_id=payment_id)
        order = payment.order
        
        # Создаем клиент ЮMoney для запроса истории операций
        client = Client(settings.YOOMONEY_TOKEN)
        
        # Получаем историю операций с фильтром по метке (label)
        history = client.operation_history(label=payment_id)
        
        # Проверяем, есть ли операции для данного платежа
        if history.operations:
            # Берем последнюю операцию (обычно она одна для данного label)
            operation = history.operations[0]
            
            # Проверяем статус операции
            if operation.status == 'success':
                # Проверяем сумму операции (с учетом возможной конвертации)
                if float(operation.amount) >= float(payment.amount):
                    # Обновляем статус платежа
                    payment.status = Payment.SUCCEEDED
                    payment.save()
                    
                    # Обновляем статус заказа
                    order.status = 'paid'  # Замените на реальный статус вашей модели Order
                    order.save()
                    
                    return True
        
        # Если платеж не найден или статус не success
        return False
    
    except Payment.DoesNotExist:
        logger.error(f"Платеж {payment_id} не найден")
        return False
    except Exception as e:
        logger.error(f"Ошибка в check_payment_status: {str(e)}")
        return False