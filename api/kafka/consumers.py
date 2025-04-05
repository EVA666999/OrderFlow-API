"""Простой Consumer для получения сообщений из Kafka"""

import json
import logging
from confluent_kafka import Consumer
from django.conf import settings

logger = logging.getLogger(__name__)

def get_messages_from_kafka(topic, max_messages=10):
    """
    Простая функция для получения сообщений из Kafka
    
    Args:
        topic: Имя топика
        max_messages: Максимальное количество сообщений для получения
    
    Returns:
        list: Список полученных сообщений
    """
    try:
        # Настройка Consumer
        consumer = Consumer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'django_consumer',
            'auto.offset.reset': 'earliest'
        })
        
        # Подписываемся на топик
        consumer.subscribe([topic])
        
        # Получаем сообщения
        messages = []
        for _ in range(max_messages):
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            
            if msg.error():
                logger.error(f"Ошибка получения сообщения: {msg.error()}")
                continue
                
            # Десериализуем сообщение
            try:
                value = json.loads(msg.value().decode('utf-8'))
                messages.append(value)
            except Exception as e:
                logger.error(f"Ошибка разбора сообщения: {e}")
        
        # Закрываем consumer
        consumer.close()
        
        return messages
        
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений из Kafka: {e}")
        return []