import json
import logging
from confluent_kafka import Consumer, KafkaError
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaConsumer:
    def __init__(self, topics, group_id=None):
        """
        Инициализирует Kafka Consumer
        
        Args:
            topics (list): Список топиков для подписки
            group_id (str, optional): ID группы потребителя
        """
        if group_id is None:
            group_id = settings.KAFKA_CONSUMER_GROUP_ID
            
        self.topics = topics if isinstance(topics, list) else [topics]
        
        self.consumer_config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'  # начинать с самого раннего сообщения
        }
        
        self.consumer = Consumer(self.consumer_config)
        self.consumer.subscribe(self.topics)
        
    def consume_messages(self, num_messages=1, timeout=1.0):
        """
        Получает сообщения из Kafka
        
        Args:
            num_messages (int): Количество сообщений для получения
            timeout (float): Таймаут в секундах для ожидания сообщений
            
        Returns:
            list: Список полученных сообщений
        """
        messages = []
        
        try:
            for _ in range(num_messages):
                msg = self.consumer.poll(timeout=timeout)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # Достигнут конец партиции
                        logger.info(f'Reached end of partition: {msg.topic()} [{msg.partition()}]')
                    else:
                        # Ошибка
                        logger.error(f'Error consuming message: {msg.error()}')
                else:
                    # Получено сообщение
                    try:
                        message_value = json.loads(msg.value().decode('utf-8'))
                        messages.append(message_value)
                    except Exception as e:
                        logger.error(f'Error decoding message: {e}')
            
            return messages
            
        except Exception as e:
            logger.error(f'Error consuming messages from Kafka: {e}')
            return []
        
    def close(self):
        """
        Закрывает потребителя Kafka
        """
        self.consumer.close()