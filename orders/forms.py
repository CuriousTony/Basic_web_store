from django import forms
from .models import Order
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class OrderCreateForm(forms.ModelForm):
    DELIVERY_CHOICES = Order.DELIVERY_CHOICES
    is_recipient_me = forms.BooleanField(
        initial=True,
        required=False,
        label='Получатель, это я',
        widget=forms.CheckboxInput(attrs={'id': 'id_is_recipient_me'})
    )
    recipient_name = forms.CharField(
        label='Имя получателя',
        required=False
    )
    recipient_phone = forms.CharField(
        label='Телефон получателя',
        required=False
    )
    recipient_address = forms.CharField(
        label='Адрес доставки получателя',
        required=False
    )

    delivery_date = forms.DateTimeField(
        input_formats=['%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Order
        fields = [
            'delivery_type',
            'delivery_address',
            'delivery_date',
        ]
        widgets = {
            'delivery_type': forms.RadioSelect(attrs={'class': 'delivery-radio'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields['recipient_name'].initial = user.name
            self.fields['recipient_phone'].initial = user.phone
            self.fields['recipient_address'].initial = user.address

    def clean_delivery_address(self):
        """Проверка адреса на наличие допустимых значений."""
        delivery_address = self.cleaned_data.get('delivery_address')
        allowed_keyword = ['санкт-петербург', 'спб', 'с-пб']
        if delivery_address and not any(keyword in delivery_address.lower() for keyword in allowed_keyword):
            raise forms.ValidationError('На сегодняшний день доставка только в пределах города Санкт-Петербурга.')
        return delivery_address

    def clean_delivery_date(self):
        """Проверка даты и времени доставки."""
        delivery_date = self.cleaned_data.get('delivery_date')
        if not delivery_date:
            raise forms.ValidationError('Пожалуйста, укажите дату и время доставки.')
        if timezone.is_naive(delivery_date):
            delivery_date = timezone.make_aware(delivery_date, timezone.get_current_timezone())

        now = timezone.now()
        min_delivery_time = now + timedelta(hours=2)
        max_delivery_time = now + timedelta(weeks=2)

        if delivery_date < now:
            raise forms.ValidationError('Дата доставки не может быть в прошлом.')
        if delivery_date > max_delivery_time:
            raise forms.ValidationError('Дата доставки не может быть позже, чем через 2 недели.')

        if not (9 <= delivery_date.hour <= 21):
            if delivery_date.hour < 9:
                raise forms.ValidationError('Время доставки должно быть не раньше 09:00.')
            else:
                raise forms.ValidationError('Время доставки должно быть не позже 21:00.')

        if delivery_date < min_delivery_time:
            raise forms.ValidationError('Время доставки должно быть не раньше, чем через 2 часа.')

        return delivery_date

    def clean(self):
        cleaned_data = super().clean()
        is_recipient_me = cleaned_data.get('is_recipient_me', True)

        if not is_recipient_me:
            if not cleaned_data.get('recipient_name'):
                self.add_error('recipient_name', 'Обязательное поле')
            if not cleaned_data.get('recipient_phone'):
                self.add_error('recipient_phone', 'Обязательное поле')
            if not cleaned_data.get('recipient_address'):
                cleaned_data['recipient_address'] = cleaned_data.get('delivery_address')

            # ВАЛИДАЦИЯ адреса для нового поля
        if cleaned_data.get('recipient_address'):
            allowed_keyword = ['санкт-петербург', 'спб', 'с-пб']
            address = cleaned_data['recipient_address'].lower()
            if not any(kw in address for kw in allowed_keyword):
                self.add_error('recipient_address',
                               'Доставка только по Санкт-Петербургу, начните адрес с "СПб,".')

        return cleaned_data
