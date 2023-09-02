from django import forms


class PaymentActionForm(forms.Form):
    ACTION_CHOICES = [
        ('confirm', 'Подтвердить платеж'),
        ('cancel', 'Отменить платеж'),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES, label='Выберите действие')
    payment_id = forms.IntegerField(label='ID платежа')
