import json
from celery import shared_task
import logging
from django.conf import settings
from kafka.consumers import get_messages_from_kafka
from kafka.producers import send_message_to_kafka

logger = logging.getLogger(__name__)

@shared_task
def process_kafka_messages(topic, num_messages=10):
    """
    Задача Celery для получения и обработки сообщений из Kafka
    """
    try:
        # Получаем сообщения из Kafka
        messages = get_messages_from_kafka(topic, num_messages)
        
        if messages:
            logger.info(f"Получено {len(messages)} сообщений из топика '{topic}'")
            # Здесь можно добавить код для обработки сообщений
            # Например, сохранить их в базу данных
            
            return f"Обработано {len(messages)} сообщений из топика '{topic}'"
        return f"Сообщения не найдены в топике '{topic}'"
    
    except Exception as e:
        logger.error(f"Ошибка обработки сообщений: {str(e)}")
        return f"Ошибка обработки сообщений: {str(e)}"


@shared_task
def send_message_to_kafka_task(topic, data):
    """
    Задача Celery для отправки сообщения в Kafka
    """
    try:
        success = send_message_to_kafka(topic, data)
        if success:
            return f"Сообщение успешно отправлено в топик '{topic}'"
        return f"Не удалось отправить сообщение в топик '{topic}'"
    
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {str(e)}")
        return f"Ошибка отправки сообщения: {str(e)}"


@shared_task
def send_order_to_kafka(order_id):
    """
    Задача Celery для отправки заказа в Kafka
    """
    from api_django.models import Order
    
    try:
        # Получаем заказ из БД
        order = Order.objects.get(id=order_id)
        
        # Подготавливаем данные заказа
        order_data = {
            'id': order.id,
            'user_id': order.user.id,
            'total_price': float(order.total_price),
            'created_at': order.pub_date.isoformat() if hasattr(order, 'pub_date') else None,
            'products': [
                {
                    'product_id': order_product.product.id,
                    'name': order_product.product.name,
                    'quantity': order_product.quantity,
                    'price': float(order_product.product.price),
                }
                for order_product in order.orderproduct_set.all()
            ],
        }
        
        # Отправляем в Kafka
        success = send_message_to_kafka('orders', order_data)
        
        if success:
            return f"Заказ №{order_id} отправлен в Kafka"
        return f"Ошибка отправки заказа №{order_id} в Kafka"
        
    except Order.DoesNotExist:
        return f"Заказ №{order_id} не найден"
    except Exception as e:
        logger.error(f"Ошибка отправки заказа в Kafka: {str(e)}")
        return f"Ошибка отправки заказа в Kafka: {str(e)}"