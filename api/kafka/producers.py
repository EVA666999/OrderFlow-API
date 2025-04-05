"""Простой Producer для отправки сообщений в Kafka"""

import json
import logging
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)


def send_message_to_kafka(topic, data):
    try:
        # Логируем хост и параметры
        logger.info(f"Kafka Bootstrap Servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        print(f"Kafka Bootstrap Servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        
        producer = Producer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'django-producer',
            'retries': 3,
            'retry.backoff.ms': 300,
            'acks': 'all'
        })
        
        message = json.dumps(data).encode('utf-8')
        producer.produce(topic, message)
        producer.flush(timeout=10)
        
        logger.info(f"Message sent to topic {topic}")
        return True
    except Exception as e:
        logger.error(f"Kafka send error: {e}", exc_info=True)
        print(f"Kafka send error: {e}")
        return False