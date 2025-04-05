"""Простой Producer для отправки сообщений в Kafka"""

import json
import logging
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)


def send_message_to_kafka(topic, data):
    try:
        # Создаем Producer с дополнительной конфигурацией
        producer = Producer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'django-producer',
            # Добавляем конфигурацию для надежности
            'retries': 3,
            'retry.backoff.ms': 300,
            'acks': 'all'  # Настройка с максимальным подтверждением
        })
        
        # Используем callback для подтверждения отправки сообщения
        def delivery_report(err, msg):
            if err is not None:
                logger.error(f'Ошибка доставки сообщения: {err}')
            else:
                logger.info(f'Сообщение доставлено в топик {msg.topic()} [{msg.partition()}]')
        
        # Сериализуем данные и отправляем сообщение
        message = json.dumps(data).encode('utf-8')
        producer.produce(topic, message, callback=delivery_report)
        
        # Гарантируем отправку сообщений
        producer.flush(timeout=10)
        
        return True
    except Exception as e:
        logger.error(f"Полная ошибка отправки в Kafka: {e}", exc_info=True)
        return False