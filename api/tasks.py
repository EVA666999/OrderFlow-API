import json
from celery import shared_task
import subprocess
import os
from datetime import datetime
from django.conf import settings
import logging

from kafka import KafkaConsumer

logger = logging.getLogger(__name__)

@shared_task
def backup_database():
    """
    Периодическая задача для резервного копирования базы данных
    """
    try:
        # Получаем переменные окружения из settings
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_host = settings.DATABASES['default']['HOST'] or 'localhost'
        db_port = settings.DATABASES['default']['PORT'] or '5432'
        
        # Создаем директорию для бэкапов, если её нет
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Формируем имя файла с текущей датой
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{db_name}_{timestamp}.sql')
        
        # Команда для создания дампа PostgreSQL
        command = [
            'pg_dump',
            f'--host={db_host}',
            f'--port={db_port}',
            f'--username={db_user}',
            '--format=custom',
            f'--file={backup_file}',
            db_name
        ]
        
        # Запускаем процесс
        process = subprocess.Popen(
            command,
            env=dict(os.environ, PGPASSWORD=settings.DATABASES['default']['PASSWORD']),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        # Проверяем результат
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8')
            logger.error(f"Backup failed: {error_msg}")
            return False
        
        logger.info(f"Database backup successfully created: {backup_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error during database backup: {str(e)}")
        return False
    
@shared_task
def process_kafka_messages(topic, num_messages=50):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='earliest',
            group_id='django_consumer',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        messages = []
        for _ in range(num_messages):
            msg = next(consumer, None)
            if msg is None:
                break
            messages.append(msg.value)
            
        consumer.close()
        
        if messages:
            # Обработка полученных сообщений
            # Например, сохранение в базу данных
            return f"Processed {len(messages)} messages from Kafka topic '{topic}'"
        return f"No messages found in Kafka topic '{topic}'"
    except Exception as e:
        return f"Error processing Kafka messages: {str(e)}"

@shared_task
def update_cache_periodically():
    # Ваш код для обновления кэша
    return "Cache updated successfully"