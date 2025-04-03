import logging
from celery import shared_task
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

import os
import datetime
import logging
import subprocess
from celery import shared_task
from django.conf import settings


from .models import Order, Product, Category
from api.kafka.producers import KafkaProducer
from api.kafka.consumers import KafkaConsumer

logger = logging.getLogger(__name__)

@shared_task
def send_order_confirmation_email(order_id):
    """
    Отправляет письмо с подтверждением заказа
    """
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f'Подтверждение заказа #{order.id}'
        message = f'''
        Здравствуйте, {order.user.username}!
        
        Ваш заказ #{order.id} успешно оформлен.
        
        Сумма заказа: {order.total_price} руб.
        
        Спасибо за покупку!
        '''
        
        recipient_list = [order.user.email]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False
        )
        
        return f'Email sent to {order.user.email}'
    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} does not exist')
        return f'Error: Order with id {order_id} does not exist'
    except Exception as e:
        logger.error(f'Error sending email: {e}')
        return f'Error sending email: {e}'

@shared_task
def produce_order_message(order_id):
    """
    Отправляет сообщение о заказе в Kafka
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Подготовка данных заказа
        order_data = {
            'order_id': order.id,
            'user_id': order.user.id,
            'username': order.user.username,
            'total_price': float(order.total_price),
            'products': [
                {
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.product.price),
                }
                for item in order.orderproduct_set.all()
            ],
        }
        
        # Инициализация продюсера
        producer = KafkaProducer()
        
        # Отправка сообщения
        result = producer.produce_message('orders', order_data)
        
        if result:
            return f'Order message for order {order_id} sent to Kafka'
        else:
            return f'Failed to send order message for order {order_id} to Kafka'
        
    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} does not exist')
        return f'Error: Order with id {order_id} does not exist'
    except Exception as e:
        logger.error(f'Error producing order message: {e}')
        return f'Error producing order message: {e}'

@shared_task
def update_cache_periodically():
    """
    Периодически обновляет кэш продуктов, категорий и заказов
    """
    try:
        # Обновление кэша продуктов
        products = list(Product.objects.values())
        cache.set('products', products, timeout=600)
        
        # Обновление кэша категорий
        categories = list(Category.objects.values())
        cache.set('categories', categories, timeout=600)
        
        # Обновление кэша заказов
        orders = list(Order.objects.values())
        cache.set('orders', orders, timeout=600)
        
        return 'Cache updated successfully'
    except Exception as e:
        logger.error(f'Error updating cache: {e}')
        return f'Error updating cache: {e}'

@shared_task
def process_kafka_messages(topic='orders', num_messages=10):
    """
    Обрабатывает сообщения из Kafka
    """
    try:
        consumer = KafkaConsumer(topic)
        messages = consumer.consume_messages(num_messages=num_messages)
        consumer.close()
        
        if messages:
            logger.info(f'Processed {len(messages)} messages from topic {topic}')
            return f'Processed {len(messages)} messages from topic {topic}'
        else:
            logger.info(f'No messages to process from topic {topic}')
            return f'No messages to process from topic {topic}'
    except Exception as e:
        logger.error(f'Error processing Kafka messages: {e}')
        return f'Error processing Kafka messages: {e}'
    
@shared_task
def backup_database():
    """
    Создает резервную копию базы данных PostgreSQL
    """
    try:
        now = datetime.datetime.now()
        date_str = now.strftime('%Y-%m-%d_%H-%M-%S')
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        # Создаем директорию для бэкапов, если её нет
        os.makedirs(backup_dir, exist_ok=True)
        
        # Имя файла бэкапа
        backup_file = os.path.join(backup_dir, f'db_backup_{date_str}.sql')
        
        # Команда для создания дампа БД
        db_name = os.environ.get('POSTGRES_DB', 'postgres')
        db_user = os.environ.get('POSTGRES_USER', 'postgres')
        db_host = os.environ.get('POSTGRES_HOST', 'db1')
        db_port = os.environ.get('POSTGRES_PORT', '5432')
        
        cmd = [
            'pg_dump',
            f'--dbname=postgresql://{db_user}@{db_host}:{db_port}/{db_name}',
            '--format=custom',
            f'--file={backup_file}'
        ]
        
        # Выполняем команду
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f'Database backup created: {backup_file}')
            return f'Database backup created successfully: {backup_file}'
        else:
            logger.error(f'Database backup failed: {result.stderr}')
            return f'Database backup failed: {result.stderr}'
    except Exception as e:
        logger.error(f'Error creating database backup: {e}')
        return f'Error creating database backup: {e}'