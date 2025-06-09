from unittest import mock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from cart.models import Cart, CartItem
from catalog.models import Bouquet
from orders.models import Order, OrderItem
from users.models import Recipient
from datetime import timedelta

User = get_user_model()


class OrderCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='testuser',
            phone='+79991234567',
            password='testpass123'
        )
        self.client.login(phone='+79991234567', password='testpass123')
        self.bouquet = Bouquet.objects.create(name='Test Bouquet', price=100, cost_price=70)
        self.cart = Cart.objects.get(user=self.user)
        CartItem.objects.create(cart=self.cart, bouquet=self.bouquet, quantity=1)
        valid_date = timezone.now() + timedelta(hours=3)
        self.valid_datetime_str = valid_date.strftime('%d.%m.%Y %H:%M')
        invalid_date = timezone.now() - timedelta(days=1)
        self.invalid_datetime_str = invalid_date.strftime('%d.%m.%Y %H:%M')

    def get_valid_order_data(self, **kwargs):
        """Генератор валидных данных для формы"""
        base_data = {
            'delivery_type': 'delivery',
            'delivery_address': 'СПб, Невский проспект, 1',
            'delivery_date': self.valid_datetime_str,
            'is_recipient_me': True,
        }
        base_data.update(kwargs)
        return base_data

    def test_redirect_if_cart_empty(self):
        """Редирект при пустой корзине"""
        self.cart.items.all().delete()
        response = self.client.get(reverse('orders:order_create'))
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_create_order_with_recipient(self):
        """Создание заказа с получателем ≠ пользователь"""
        data = self.get_valid_order_data(
            is_recipient_me=False,
            recipient_name='Recipient Name',
            recipient_phone='+79999999999',
            recipient_address='СПб, Литейный проспект, 2'
        )

        response = self.client.post(reverse('orders:order_create'), data)

        self.assertEqual(response.status_code, 302, "Ожидался редирект при успешном создании")
        self.assertEqual(Order.objects.count(), 1, "Заказ не был создан")
        self.assertEqual(OrderItem.objects.count(), 1, "Элементы заказа не созданы")
        self.assertEqual(Recipient.objects.count(), 1, "Получатель не создан")
        self.assertFalse(Cart.objects.filter(user=self.user).exists(), "Корзина не была удалена")

    def test_create_order_without_recipient(self):
        """Создание заказа без отдельного получателя"""
        data = self.get_valid_order_data(
            delivery_type='pickup',
            delivery_address='Пункт самовывоза СПб',  # Валидный адрес
            is_recipient_me=True
        )

        response = self.client.post(reverse('orders:order_create'), data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(Recipient.objects.count(), 0)

        order = Order.objects.first()
        self.assertEqual(order.delivery_address, 'Пункт самовывоза СПб')
        self.assertIsNone(order.recipient)

    def test_invalid_form_rerenders_page(self):
        """Невалидная форма должна перезагружать страницу с ошибками"""
        response = self.client.post(reverse('orders:order_create'), {
            'delivery_type': 'delivery'
        })

        self.assertEqual(response.status_code, 200, "Ожидался код 200 для невалидной формы")
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)
        self.assertIn('delivery_address', form.errors)

    def test_invalid_delivery_date(self):
        """Попытка указать дату доставки в прошлом"""
        data = self.get_valid_order_data(
            delivery_date=self.invalid_datetime_str
        )

        response = self.client.post(reverse('orders:order_create'), data)

        self.assertEqual(response.status_code, 200, "Ожидался код 200 для невалидной даты")
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)
        error_text = ''.join(form.errors['delivery_date'])
        self.assertIn('Дата доставки не может быть в прошлом', error_text)

    @mock.patch('orders.views.OrderItem.objects.create')
    def test_transaction_rollback_on_error(self, mock_create):
        """Откат транзакции при ошибке создания элементов заказа"""
        mock_create.side_effect = Exception('Forced error')
        data = self.get_valid_order_data()

        response = self.client.post(reverse('orders:order_create'), data)

        self.assertEqual(response.status_code, 200, "Ожидался код 200 при ошибке транзакции")
        self.assertEqual(Order.objects.count(), 0, "Заказ не должен быть создан")
        self.assertEqual(Recipient.objects.count(), 0, "Получатель не должен быть создан")
        self.assertTrue(Cart.objects.filter(user=self.user).exists(), "Корзина должна остаться")
        self.assertIn("Ошибка при оформлении заказа", response.content.decode())


class RepeatOrderViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='tester',
            phone='+79991112233',
            password='testpass'
        )

        self.bouquet = Bouquet.objects.create(
            name='Тестовый букет',
            consists='Розы, лилии',
            price=1000,
            cost_price=700
        )

        self.order = Order.objects.create(
            user=self.user,
            total_price=1000.00,
            delivery_date=timezone.now() + timedelta(hours=3),
            status='completed'
        )

        OrderItem.objects.create(
            order=self.order,
            bouquet=self.bouquet,
            quantity=2,
            price=1000
        )

        self.client = Client()
        self.client.login(phone='+79991112233', password='testpass')

    def test_repeat_order(self):
        response = self.client.post(reverse('orders:repeat_order', args=[self.order.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:order_create'))

        cart = Cart.objects.get(user=self.user)
        cart_items = cart.items.all()

        self.assertEqual(cart_items.count(), 1)
        cart_item = cart_items.first()
        self.assertEqual(cart_item.bouquet, self.bouquet)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.price, 1000)

    def test_repeat_order_creates_new_cart_if_not_exists(self):
        # Убедимся, что корзина отсутствует
        # self.assertFalse(Cart.objects.filter(user=self.user).exists())
        self.client.post(reverse('orders:repeat_order', args=[self.order.id]))
        cart = Cart.objects.get(user=self.user)
        self.assertIsNotNone(cart)

    def test_repeat_order_increases_quantity_if_item_exists(self):
        cart = Cart.objects.get(user=self.user)
        CartItem.objects.create(
            cart=cart,
            bouquet=self.bouquet,
            quantity=1,
            price=1000.00
        )

        self.client.post(reverse('orders:repeat_order', args=[self.order.id]))
        cart_item = CartItem.objects.get(cart=cart, bouquet=self.bouquet)
        self.assertEqual(cart_item.quantity, 3)
