import json
import logging
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        self.producer_config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'django_producer'
        }
        self.producer = Producer(self.producer_config)

    def delivery_report(self, err, msg):
        """ Отчет о доставке сообщения """
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def produce_message(self, topic, message_data):
        """
        Отправляет сообщение в указанный топик Kafka
        
        Args:
            topic (str): Название топика Kafka
            message_data (dict): Данные для отправки в формате словаря
        """
        try:
            # Конвертируем сообщение в JSON-строку
            message_json = json.dumps(message_data).encode('utf-8')
            
            # Отправляем сообщение
            self.producer.produce(
                topic=topic,
                value=message_json,
                callback=self.delivery_report
            )
            
            # Запускаем обработку очереди сообщений
            self.producer.poll(0)
            
            # Дожидаемся отправки всех сообщений
            self.producer.flush()
            
            return True
        except Exception as e:
            logger.error(f'Error producing message to Kafka: {e}')
            return False