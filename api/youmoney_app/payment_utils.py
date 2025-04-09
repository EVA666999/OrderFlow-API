import uuid
import requests
from yoomoney import Client, Quickpay
from django.conf import settings
from .models import Payment

import logging

logger = logging.getLogger(__name__)

def create_payment(order):
    """
    Создание платежа через ЮMoney API
    """
    try:
        # Параметры для создания платежа в ЮMoney (обратите внимание: поле 'secret' убрано)
        payload = {
            'amount': float(order.total_price),
            'order_id': str(order.id),
            'description': f'Оплата заказа #{order.id}',
            'return_url': settings.YOOMONEY_RETURN_URL,
            'client_id': settings.YOOMONEY_CLIENT_ID,
            'notification_url': "http://localhost/payments/yoomoney-notify/"
        }
        
        # Отправка запроса в ЮMoney
        response = requests.post(
            'https://yoomoney.ru/api/create-payment', 
            json=payload
        )
        
        if response.status_code == 200:
            payment_data = response.json()
            
            # Создаем объект платежа в базе данных
            payment = Payment.objects.create(
                order=order,
                payment_id=payment_data['payment_id'],
                amount=order.total_price,
                status=Payment.PENDING
            )
            
            return payment_data['payment_url'], payment
        else:
            logger.error(f"Ошибка создания платежа: {response.text}")
            raise Exception("Не удалось создать платеж")
    
    except Exception as e:
        logger.error(f"Ошибка в create_payment: {str(e)}")
        raise

def check_payment_status(payment_id):
    """
    Проверка статуса платежа через ЮMoney
    """
    try:
        # Находим платеж в базе данных
        payment = Payment.objects.get(payment_id=payment_id)
        order = payment.order
        
        url = "https://yoomoney.ru/api/operation-history"
        
        headers = {
            'Authorization': f'Bearer {settings.YOOMONEY_TOKEN}'
        }
        params = {
            'label': payment_id,
            'records': 1
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            operations = response.json().get('operations', [])
            
            if operations:
                operation = operations[0]
                
                # Проверяем сумму и статус операции
                if (float(operation['amount']) == float(payment.amount) and 
                    operation['status'] == 'success'):
                    
                    payment.status = Payment.SUCCEEDED
                    payment.save()
                    
                    # Обновляем статус заказа, замените на логику вашей модели
                    order.status = 'succeeded'
                    order.save()
                    
                    return True
        return False
    
    except Payment.DoesNotExist:
        logger.error(f"Платеж {payment_id} не найден")
        return False
    except Exception as e:
        logger.error(f"Ошибка в check_payment_status: {str(e)}")
        return False