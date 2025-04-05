"""Простой Producer для отправки сообщений в Kafka"""

import json
import logging
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)


def send_message_to_kafka(topic, data):
    """
    Простая функция для отправки сообщения в Kafka
    
    Args:
        topic: Имя топика
        data: Словарь с данными для отправки
    
    Returns:
        bool: Успешно ли отправлено сообщение
    """
    try:
        # Создаем Producer
        producer = Producer({'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS})
        
        # Сериализуем данные в JSON
        message = json.dumps(data).encode('utf-8')
        
        # Отправляем сообщение
        producer.produce(topic, message)
        producer.flush()
        
        logger.info(f"Сообщение отправлено в топик {topic}")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return False