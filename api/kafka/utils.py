import logging
from confluent_kafka.admin import AdminClient, NewTopic
from django.conf import settings

logger = logging.getLogger(__name__)

def ensure_kafka_topics(topics=['orders'], num_partitions=1, replication_factor=1):
    """
    Создает топики в Kafka, если они не существуют
    """
    try:
        # Создаем клиент администратора
        admin_client = AdminClient({'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS})
        
        # Получаем существующие топики
        metadata = admin_client.list_topics(timeout=10)
        existing_topics = metadata.topics
        
        # Создаем только недостающие топики
        new_topics = []
        for topic in topics:
            if topic not in existing_topics:
                new_topics.append(NewTopic(
                    topic, 
                    num_partitions=num_partitions,
                    replication_factor=replication_factor
                ))
        
        # Если все топики уже существуют, просто возвращаем успех
        if not new_topics:
            logger.info("Все топики уже существуют")
            return True
        
        # Создаем недостающие топики
        result = admin_client.create_topics(new_topics)
        
        # Проверяем результат создания
        for topic, future in result.items():
            try:
                future.result()  # Ожидаем завершения
                logger.info(f"Топик {topic} успешно создан")
            except Exception as e:
                logger.error(f"Ошибка создания топика {topic}: {e}")
                return False
                
        return True
                
    except Exception as e:
        logger.error(f"Ошибка при работе с Kafka: {e}")
        return False