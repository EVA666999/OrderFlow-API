import logging
from confluent_kafka.admin import AdminClient, NewTopic
from django.conf import settings

logger = logging.getLogger(__name__)

def create_kafka_topics(topics, num_partitions=1, replication_factor=1):
    """
    Создает темы в Kafka, если они не существуют
    
    Args:
        topics (list): Список имен тем для создания
        num_partitions (int): Количество партиций для каждой темы
        replication_factor (int): Фактор репликации
        
    Returns:
        dict: Результаты создания тем
    """
    try:
        admin_client = AdminClient({'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS})
        
        # Получаем список существующих тем
        metadata = admin_client.list_topics(timeout=10)
        existing_topics = metadata.topics
        
        # Создаем новые темы
        new_topics = []
        for topic in topics:
            if topic not in existing_topics:
                new_topics.append(NewTopic(
                    topic,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor
                ))
        
        if not new_topics:
            logger.info("All topics already exist.")
            return {"status": "OK", "message": "All topics already exist."}
        
        # Создаем темы
        result = admin_client.create_topics(new_topics)
        
        # Формируем результат
        response = {"status": "OK", "results": {}}
        for topic, future in result.items():
            try:
                future.result()  # Ждем завершения операции
                response["results"][topic] = "Created"
                logger.info(f"Topic {topic} created successfully.")
            except Exception as e:
                response["results"][topic] = f"Error: {str(e)}"
                logger.error(f"Failed to create topic {topic}: {e}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error creating Kafka topics: {e}")
        return {"status": "ERROR", "message": str(e)}

def get_kafka_topic_info(topics=None):
    """
    Получает информацию о темах Kafka
    
    Args:
        topics (list, optional): Список тем для получения информации
                                Если None, возвращает информацию о всех темах
        
    Returns:
        dict: Информация о темах
    """
    try:
        admin_client = AdminClient({'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS})
        
        # Получаем метаданные
        metadata = admin_client.list_topics(timeout=10)
        
        # Если topics не указан, берем все темы
        if topics is None:
            topics = metadata.topics.keys()
        
        # Формируем результат
        result = {}
        for topic in topics:
            if topic in metadata.topics:
                topic_metadata = metadata.topics[topic]
                
                # Получаем информацию о партициях
                partitions = {}
                for partition_id, partition in topic_metadata.partitions.items():
                    partitions[partition_id] = {
                        "leader": partition.leader,
                        "replicas": partition.replicas,
                        "isrs": partition.isrs,
                    }
                
                result[topic] = {
                    "partitions": partitions,
                    "partition_count": len(partitions),
                }
            else:
                result[topic] = {"error": "Topic does not exist"}
        
        return {"status": "OK", "topics": result}
    
    except Exception as e:
        logger.error(f"Error getting Kafka topic info: {e}")
        return {"status": "ERROR", "message": str(e)}