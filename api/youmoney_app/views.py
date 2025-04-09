from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import redirect
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

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrCustomer]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def success(self, request):
        """
        Обработчик успешного платежа - возвращает результат для API
        """
        payment_id = request.query_params.get('label')
        
        if not payment_id:
            return Response({'error': 'Payment ID not provided'}, status=400)
        
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            
            check_payment_status(payment_id)
            
            return Response({
                'success': True,
                'order_id': payment.order.id,
                'payment_id': payment.payment_id,
                'status': payment.status,
                'is_paid': payment.status == Payment.SUCCEEDED,
                'amount': float(payment.amount)
            })
            
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """
        Создает платеж для указанного заказа
        """
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({'error': 'Необходимо указать ID заказа order_id: '}, status=400)
        
        try:
            # Проверяем, что заказ принадлежит текущему пользователю
            if request.user.is_staff:
                order = Order.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id, user=request.user)
            
            # Проверяем, есть ли уже созданный платеж для этого заказа
            existing_payment = Payment.objects.filter(
                order=order, 
                status=Payment.PENDING
            ).first()
            
            if existing_payment:
                return Response({
                    'payment_url': f"https://yoomoney.ru/checkout/payments/v2/contract?orderId={existing_payment.payment_id}",
                    'payment_id': existing_payment.payment_id
                })
            
            # Создаем платеж
            payment_url, payment = create_payment(order)
            
            return Response({
                'payment_url': payment_url,
                'payment_id': payment.payment_id
            })
            
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def check_status(self, request):
        """
        Проверяет статус платежа
        """
        payment_id = request.query_params.get('payment_id')
        
        if not payment_id:
            return Response({'error': 'Не указан ID платежа'}, status=400)
        
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            
            # Если пользователь не админ, проверяем что платеж относится к его заказу
            if not request.user.is_staff and payment.order.user != request.user:
                return Response({'error': 'У вас нет доступа к этому платежу'}, status=403)
            
            # Проверяем статус в ЮMoney, если платеж все еще в ожидании
            if payment.status == Payment.PENDING:
                is_paid = check_payment_status(payment_id)
            else:
                is_paid = payment.status == Payment.SUCCEEDED
            
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
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def simulate_notification(self, request):
        """
        Имитирует получение уведомления от ЮMoney 
        (только для локальной разработки)
        """
        if not settings.DEBUG:
            return Response({"error": "Эта функция доступна только в режиме отладки"}, status=403)
        
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response({"error": "Необходимо указать ID платежа"}, status=400)
        
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            
            # Обновляем статус платежа
            payment.status = Payment.SUCCEEDED
            payment.save()
            
            # Обработка заказа после успешной оплаты
            order = payment.order
            # Здесь можно добавить логику изменения статуса заказа
            
            # Отправка уведомления через WebSocket
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
            
            return Response({
                "status": "success", 
                "message": "Платеж успешно обработан"
            })
            
        except Payment.DoesNotExist:
            return Response({"error": "Платеж не найден"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
        
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