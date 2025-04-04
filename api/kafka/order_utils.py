from celery import shared_task
from kafka.producers import KafkaProducer
from api.api_django.models import Order  # Измените путь импорта на правильный

@shared_task
def produce_order_message(order_id):
    """
    Celery-задача для отправки данных заказа в Kafka
    """
    # Получаем заказ из базы данных
    try:
        order = Order.objects.get(id=order_id)
        
        # Преобразуем заказ в словарь для отправки
        order_data = {
            'id': order.id,
            'user_id': order.user.id,
            'total_price': float(order.total_price),
            'created_at': order.pub_date.isoformat() if hasattr(order, 'pub_date') else None,
            'products': [
                {
                    'product_id': order_product.product.id,
                    'name': order_product.product.name,
                    'quantity': order_product.quantity,
                    'price': float(order_product.product.price),
                }
                for order_product in order.orderproduct_set.all()
            ],
        }
        
        # Отправляем сообщение в Kafka
        producer = KafkaProducer()
        return producer.produce_message(topic='orders', message_data=order_data)
    except Order.DoesNotExist:
        return False
    except Exception as e:
        return False