"""Простой Consumer для получения сообщений из Kafka"""

import json
import logging
from confluent_kafka import Consumer
from django.conf import settings

logger = logging.getLogger(__name__)

def get_messages_from_kafka(topic, max_messages=10):
    try:
        # Улучшенная настройка Consumer
        consumer = Consumer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'django_consumer',
            'auto.offset.reset': 'earliest',
            # Добавляем дополнительные параметры для надежности
            'enable.auto.commit': False,  # Ручное подтверждение обработки сообщений
            'auto.offset.reset': 'earliest',  # Начинаем с самых ранних сообщений
            'max.poll.interval.ms': 300000,  # Увеличиваем время ожидания
            'session.timeout.ms': 45000  # Увеличиваем время сессии
        })
        
        # Подписываемся на топик
        consumer.subscribe([topic])
        
        messages = []
        while len(messages) < max_messages:
            msg = consumer.poll(timeout=5.0)
            if msg is None:
                break  # Если сообщений больше нет
            
            if msg.error():
                logger.error(f"Ошибка получения сообщения: {msg.error()}")
                continue
                
            try:
                value = json.loads(msg.value().decode('utf-8'))
                messages.append(value)
                # Подтверждаем обработку сообщения
                consumer.commit(msg)
            except Exception as e:
                logger.error(f"Ошибка разбора сообщения: {e}")
        
        consumer.close()
        return messages
        
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений из Kafka: {e}", exc_info=True)
        return []