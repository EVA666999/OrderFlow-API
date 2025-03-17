from django.core.mail import send_mail


def send_order_confirmation_email(order):
    """
    Функция для отправки email с подтверждением заказа.
    """
    subject = f"Подтверждение заказа №{order.id}"
    message = f"Спасибо за заказ, {order.user.username}. Ваш заказ №{order.id} успешно оформлен. Общая сумма: {order.total_price} руб."
    recipient_list = [order.user.email]
    send_mail(subject, message, "ukratitelkisok9913@inbox.ru", recipient_list)
