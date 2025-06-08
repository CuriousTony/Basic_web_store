from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from orders.forms import OrderCreateForm
from orders.models import Order

User = get_user_model()


class OrderCreateFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='testuser',
            password='pass',
            phone='+71234567890'
        )
        now = timezone.now()
        self.valid_date = (now + timedelta(hours=2, minutes=10))
        self.base_order_data = {
            'delivery_type': Order.DELIVERY_CHOICES[0][0],
            'delivery_address': 'СПб, Невский проспект, 10',
            'delivery_date': self.valid_date.strftime('%Y-%m-%d %H:%M'),
        }

    def test_data_for_authenticated_user(self):
        form = OrderCreateForm(user=self.user)
        self.assertEqual(form.fields['recipient_name'].initial, self.user.name)
        self.assertEqual(form.fields['recipient_phone'].initial, self.user.phone)
        self.assertEqual(form.fields['recipient_address'].initial, self.user.address)

    def test_delivery_city_check(self):
        data = self.base_order_data.copy()
        data['delivery_address'] = 'Москва, Арбат, 1'
        form = OrderCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_address', form.errors)
        self.assertIn('Санкт-Петербурга', form.errors['delivery_address'][0])

    def test_delivery_date_in_the_past(self):
        data = self.base_order_data.copy()
        data['delivery_date'] = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
        form = OrderCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)
        self.assertIn('не может быть в прошлом', form.errors['delivery_date'][0])

    def test_delivery_date_too_late(self):
        data = self.base_order_data.copy()
        data['delivery_date'] = (timezone.now() + timedelta(weeks=3)).strftime('%Y-%m-%d %H:%M')
        form = OrderCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)
        self.assertIn('не может быть позже', form.errors['delivery_date'][0])

    def test_delivery_time_too_early(self):
        now = timezone.now()
        delivery_date = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
        data = self.base_order_data.copy()
        data['delivery_date'] = delivery_date.strftime('%Y-%m-%d %H:%M')
        form = OrderCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)
        self.assertIn('не раньше 09:00', form.errors['delivery_date'][0])

    def test_delivery_time_too_late(self):
        now = timezone.now()
        delivery_date = (now + timedelta(days=1)).replace(hour=22, minute=0, second=0, microsecond=0)
        data = self.base_order_data.copy()
        data['delivery_date'] = delivery_date.strftime('%Y-%m-%d %H:%M')
        form = OrderCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)
        self.assertIn('не позже 21:00', form.errors['delivery_date'][0])

    def test_delivery_time_less_than_2_hours(self):
        now = timezone.now()
        delivery_date = now + timedelta(minutes=90)
        delivery_date = delivery_date.replace(second=0, microsecond=0)
        data = self.base_order_data.copy()
        data['delivery_date'] = delivery_date.strftime('%Y-%m-%d %H:%M')
        form = OrderCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)
        self.assertIn('не раньше, чем через 2 часа', form.errors['delivery_date'][0])

    def test_recipient_fields(self):
        data = self.base_order_data.copy()
        data.update({
            'is_recipient_me': False,
            'recipient_name': '',
            'recipient_phone': '',
            'recipient_address': ''
        })
        form = OrderCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('recipient_name', form.errors)
        self.assertIn('recipient_phone', form.errors)
        # recipient_address подставляется из delivery_address и проходит city check

    def test_recipient_city_check(self):
        data = self.base_order_data.copy()
        data.update({
            'is_recipient_me': False,
            'recipient_name': 'Друг',
            'recipient_phone': '999',
            'recipient_address': 'Москва, Пушкина'
        })
        form = OrderCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('recipient_address', form.errors)
        self.assertIn('Доставка только по Санкт-Петербургу', form.errors['recipient_address'][0])

    def test_success_order_form_valid(self):
        data = self.base_order_data.copy()
        data['is_recipient_me'] = True
        form = OrderCreateForm(data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_success_order_form_valid_recipient(self):
        data = self.base_order_data.copy()
        data.update({
            'is_recipient_me': False,
            'recipient_name': 'Петя',
            'recipient_phone': '+78121231212',
            'recipient_address': 'СПб, Литейный, 1'
        })
        form = OrderCreateForm(data)
        self.assertTrue(form.is_valid(), form.errors)
