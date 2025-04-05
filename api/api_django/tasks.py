import json
import logging
from celery import shared_task  # Импортируем shared_task непосредственно из celery
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

from kafka.consumers import get_messages_from_kafka
from .models import Order, Product, Category

logger = logging.getLogger(__name__)

@shared_task
def send_order_confirmation_email(order_id):
    """
    Отправляет письмо с подтверждением заказа
    """
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f'Подтверждение заказа #{order.id}'
        message = f'''
        Здравствуйте, {order.user.username}!
        
        Ваш заказ #{order.id} успешно оформлен.
        
        Сумма заказа: {order.total_price} руб.
        
        Спасибо за покупку!
        '''
        
        recipient_list = [order.user.email]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False
        )
        
        return f'Email sent to {order.user.email}'
    except Exception as e:
        logger.error(f'Error sending email: {e}')
        return f'Error sending email: {e}'

@shared_task
def update_cache_periodically():
    """
    Периодически обновляет кэш продуктов, категорий и заказов
    """
    try:
        # Обновление кэша продуктов
        products = list(Product.objects.values())
        cache.set('products', products, timeout=600)
        
        # Обновление кэша категорий
        categories = list(Category.objects.values())
        cache.set('categories', categories, timeout=600)
        
        # Обновление кэша заказов
        orders = list(Order.objects.values())
        cache.set('orders', orders, timeout=600)
        
        return 'Cache updated successfully'
    except Exception as e:
        logger.error(f'Error updating cache: {e}')
        return f'Error updating cache: {e}'
    
@shared_task
def process_kafka_messages(topic, num_messages=50):
    try:
        # Используем функцию get_messages_from_kafka вместо прямого использования KafkaConsumer
        from kafka.consumers import get_messages_from_kafka
        
        # Получаем сообщения
        messages = get_messages_from_kafka(topic, num_messages)
        
        if messages:
            # Обработка полученных сообщений
            # Например, сохранение в базу данных
            return f"Processed {len(messages)} messages from Kafka topic '{topic}'"
        return f"No messages found in Kafka topic '{topic}'"
    except Exception as e:
        return f"Error processing Kafka messages: {str(e)}"