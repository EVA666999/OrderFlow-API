from celery import shared_task
from kafka.producers import send_message_to_kafka
from api_django.models import Order

@shared_task
def produce_order_message(order_id):
    try:
        order = Order.objects.get(id=order_id)
        
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
        
        # Используем функцию вместо класса
        return send_message_to_kafka(topic='orders', data=order_data)
    except Order.DoesNotExist:
        return False
    except Exception as e:
        return False