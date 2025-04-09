import uuid
from yoomoney import Client, Quickpay
from django.conf import settings
from .models import Payment

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def create_payment(order):
    """
    Создание платежа через ЮMoney API
    """
    try:
        # Параметры для создания платежа в ЮMoney
        payload = {
            'amount': float(order.total_price),
            'order_id': str(order.id),
            'description': f'Оплата заказа #{order.id}',
            'return_url': settings.YOOMONEY_RETURN_URL,
            'client_id': settings.YOOMONEY_CLIENT_ID,
            'notification_url': "http://localhost/payments/yoomoney-notify/"
    }
        print(f"Order ID: {order.id}")
        print(f"Total Price: {order.total_price}")
        print(f"Account: {settings.YOOMONEY_ACCOUNT}")
        
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
        logger.error(f"Полная ошибка: {e}", exc_info=True)
        raise

def check_payment_status(payment_id):
    """
    Проверка статуса платежа через ЮMoney API
    """
    try:
        # Параметры для проверки статуса платежа
        payload = {
            'payment_id': payment_id,
            'client_id': settings.YOOMONEY_CLIENT_ID,
        }
        
        # Запрос к API ЮMoney для проверки статуса
        response = requests.get(
            'https://yoomoney.ru/api/payment-status', 
            params=payload
        )
        
        if response.status_code == 200:
            payment_status = response.json()
            
            # Обновляем статус платежа в базе данных
            try:
                payment = Payment.objects.get(payment_id=payment_id)
                
                if payment_status['status'] == 'succeeded':
                    payment.status = Payment.SUCCEEDED
                    payment.save()
                    
                    # Обновляем статус заказа
                    order = payment.order
                    order.status = 'paid'  # Предполагаемый статус заказа
                    order.save()
                    
                    return True
                elif payment_status['status'] == 'canceled':
                    payment.status = Payment.CANCELED
                    payment.save()
                    
                    return False
            except Payment.DoesNotExist:
                logger.error(f"Платеж {payment_id} не найден")
                return False
        
        return False
    
    except Exception as e:
        logger.error(f"Ошибка в check_payment_status: {str(e)}")
        return False