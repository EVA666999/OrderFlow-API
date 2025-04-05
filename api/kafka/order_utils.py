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
        
        # Добавьте подробное логирование
        print(f"Preparing to send order {order_id} to Kafka")
        print(f"Order data: {order_data}")
        
        # Используем функцию отправки с логированием
        success = send_message_to_kafka('orders', order_data)
        
        print(f"Message send result: {success}")
        
        return success
    except Exception as e:
        print(f"Error in produce_order_message: {e}")
        return False