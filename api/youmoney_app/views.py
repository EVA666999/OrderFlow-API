import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import redirect, render
from .payment_utils import create_payment, check_payment_status
from .models import Payment
from .serializers import PaymentSerializer
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import filters, viewsets
from api_django.models import Order
import hashlib
from api_django.permissions import IsAdminOrCustomer
import hmac



logger = logging.getLogger(__name__)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    # permission_classes = [IsAdminOrCustomer]
    
    def get_queryset(self):
        """
        Возвращает платежи с фильтрацией по пользователю
        """
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)
    
    @action(detail=False, methods=['POST'])
    def create_payment(self, request):
        """
        Создание нового платежа для заказа
        """
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({'error': 'Необходимо указать ID заказа'}, status=400)
        
        try:
            # Проверка доступа к заказу
            if request.user.is_staff:
                order = Order.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id, user=request.user)
            
            # Проверка существующего платежа
            existing_payment = Payment.objects.filter(
                order=order, 
                status=Payment.PENDING
            ).first()
            
            if existing_payment:
                return Response({
                    'payment_url': f"https://yoomoney.ru/checkout/payments/v2/contract?orderId={existing_payment.payment_id}",
                    'payment_id': existing_payment.payment_id
                })
            
            # Создание нового платежа
            payment_url, payment = create_payment(order)
            
            return Response({
                'payment_url': payment_url,
                'payment_id': payment.payment_id
            })
        
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=404)
        except Exception as e:
            logger.error(f"Ошибка создания платежа: {str(e)}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['GET'])
    def check_payment(self, request):
        """
        Проверка статуса платежа
        """
        payment_id = request.query_params.get('payment_id')
        
        if not payment_id:
            return Response({'error': 'Не указан ID платежа'}, status=400)
        
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            
            # Проверка прав доступа
            if not request.user.is_staff and payment.order.user != request.user:
                return Response({'error': 'Нет доступа к этому платежу'}, status=403)
            
            # Проверка статуса платежа
            is_paid = check_payment_status(payment_id)
            
            # Подготовка ответа
            return Response({
                'order_id': payment.order.id,
                'payment_id': payment.payment_id,
                'status': payment.status,
                'is_paid': is_paid,
                'amount': float(payment.amount)
            })
        
        except Payment.DoesNotExist:
            return Response({'error': 'Платеж не найден'}, status=404)
        except Exception as e:
            logger.error(f"Ошибка проверки платежа: {str(e)}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['POST'])
    def update_payment_status(self, request):
        """
        Принудительное обновление статуса платежа
        """
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response({'error': 'Не указан ID платежа'}, status=400)
        
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            
            # Проверка прав доступа
            if not request.user.is_staff and payment.order.user != request.user:
                return Response({'error': 'Нет доступа к этому платежу'}, status=403)
            
            # Принудительная проверка статуса
            is_paid = check_payment_status(payment_id)
            
            return Response({
                'order_id': payment.order.id,
                'payment_id': payment.payment_id,
                'status': payment.status,
                'is_paid': is_paid,
                'amount': float(payment.amount)
            })
        
        except Payment.DoesNotExist:
            return Response({'error': 'Платеж не найден'}, status=404)
        except Exception as e:
            logger.error(f"Ошибка обновления статуса платежа: {str(e)}")
            return Response({'error': str(e)}, status=500)
        
from rest_framework.views import APIView
import hashlib

class YooMoneyNotificationView(APIView):
    permission_classes = []  # Публичный доступ
    
    def post(self, request):
        """
        Обработчик уведомлений от ЮMoney.
        В боевом режиме этот метод будет вызываться системой ЮMoney
        """
        notification_type = request.data.get('notification_type')
        operation_id = request.data.get('operation_id')
        amount = request.data.get('amount')
        currency = request.data.get('currency')
        datetime_value = request.data.get('datetime')
        sender = request.data.get('sender')
        codepro = request.data.get('codepro')
        label = request.data.get('label')  # Это наш payment_id
        sha1_hash = request.data.get('sha1_hash')
        
        # Проверка подписи
        check_str = f'{notification_type}&{operation_id}&{amount}&{currency}&{datetime_value}&{sender}&{codepro}&{settings.YOOMONEY_SECRET}&{label}'
        check_hash = hashlib.sha1(check_str.encode()).hexdigest()
        
        if sha1_hash and check_hash != sha1_hash:
            return Response({'error': 'Неверная подпись'}, status=400)
        
        # Обработка платежа
        try:
            payment = Payment.objects.get(payment_id=label)
            
            # Проверяем сумму платежа
            if float(amount) >= float(payment.amount):
                payment.status = Payment.SUCCEEDED
                payment.save()
                
                # Обновляем заказ
                order = payment.order
                # Здесь логика обновления заказа
                
                # Отправляем уведомление через WebSocket
                channel_layer = get_channel_layer()
                payment_details = {
                    'payment_id': payment.payment_id,
                    'order_id': order.id,
                    'status': payment.status,
                    'amount': float(payment.amount)
                }
                
                async_to_sync(channel_layer.group_send)(
                    "orders_group",
                    {
                        "type": "send_payment_details",
                        "payment_details": payment_details,
                    },
                )
                
                return Response({'status': 'ok'})
            else:
                return Response({'error': 'Неверная сумма платежа'}, status=400)
                
        except Payment.DoesNotExist:
            return Response({'error': 'Платеж не найден'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        

def payment_success(request):
    """
    Обработчик успешного платежа
    """
    # Можно добавить логику обработки успешного платежа
    return render(request, 'payment_success.html')