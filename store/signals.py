from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from decouple import config
from rest_framework.response import Response
from django.db.models.signals import pre_save

from .models import Order

# Сигнал для создания заказа
@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        subject = 'Ваш заказ успешно создан'
        message = 'Ваш заказ был успешно создан. Номер заказа: {}'.format(instance.order_number)
        from_email = config('EMAIL_HOST_USER') # Замените на ваш адрес отправителя
        recipient_list = [instance.email]  # Это должен быть адрес электронной почты пользователя

        send_mail(subject, message, from_email, recipient_list)

@receiver(pre_save, sender=Order)
def order_data_delivery_updated(sender, instance, **kwargs):
    if instance._state.adding or instance._state.db is None:
        # Объект создается, а не обновляется
        return

    try:
        old_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    if old_order.delivery_date != instance.delivery_date:
        # Поле data_delivery было изменено
        subject = 'Изменение даты доставки'
        message = 'Дата доставки в вашем заказе была обновлена.'
        from_email =  config('EMAIL_HOST_USER')  # Замените на ваш адрес отправителя
        recipient_list = [instance.email]  # Это должен быть адрес электронной почты пользователя

        send_mail(subject, message, from_email, recipient_list)
