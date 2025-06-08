from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from users.models import User, Recipient
from catalog.models import Bouquet
from orders.models import Order, OrderItem
import datetime


class RecipientModelTest(TestCase):
    def test_create_recipient(self):
        """Тест создания получателя, привязанного к пользователю"""
        user = User.objects.create_user(
            name='recipient_user',
            phone='+71234567890'
        )

        recipient = Recipient.objects.create(
            user=user,
            name='Иван Иванов',
            phone='+79998887766'
        )

        self.assertEqual(recipient.user, user)
        self.assertEqual(recipient.phone, '+79998887766')
        self.assertEqual(recipient.name, 'Иван Иванов')

        # Проверка, что получатель не создаётся без пользователя
        with self.assertRaises(IntegrityError):
            Recipient.objects.create(
                name='Без пользователя',
                phone='+71112223344'
            ).full_clean()


class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем пользователя
        cls.user = User.objects.create_user(
            name='testuser',
            phone='+71234567890'
        )

        # Создаем получателя ТОЛЬКО для одного из тестов
        cls.recipient = Recipient.objects.create(
            user=cls.user,
            name='Получатель Тестовый',
            phone='+79998887766'
        )

        # Создаем букет
        cls.bouquet = Bouquet.objects.create(
            name='Тестовый Букет',
            consists='Розы, Хризантемы',
            price=2500,
            cost_price=1200,
            pic1='test_bouquet.jpg'
        )

        # Корректная дата доставки (на 3 часа позже текущего времени)
        cls.valid_delivery_date = timezone.now() + datetime.timedelta(hours=3)

    def test_create_order_without_recipient(self):
        """Тест создания заказа без указания получателя (пользователь заказывает себе)"""
        order = Order.objects.create(
            user=self.user,
            delivery_address='ул. Пользовательская, 1',
            delivery_date=self.valid_delivery_date,
            total_price=2500,
            delivery_type='delivery'
        )

        self.assertEqual(order.status, 'prepaid')
        self.assertIsNone(order.recipient)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.delivery_address, 'ул. Пользовательская, 1')
        self.assertEqual(str(order), f"Заказ #{order.id} - {self.user.phone}")

    def test_create_order_with_recipient(self):
        """Тест создания заказа с указанием другого получателя"""
        order = Order.objects.create(
            user=self.user,
            recipient=self.recipient,
            delivery_address='ул. Получательская, 2',
            delivery_date=self.valid_delivery_date,
            total_price=5000,
            delivery_type='delivery'
        )

        self.assertEqual(order.recipient, self.recipient)
        self.assertEqual(order.delivery_address, 'ул. Получательская, 2')
        self.assertEqual(str(order), f"Заказ #{order.id} - {self.recipient.phone}")

    def test_recipient_requires_user(self):
        """Тест, что получатель не может быть создан без привязки к пользователю"""
        with self.assertRaises(ValidationError):
            recipient = Recipient(
                name='Тестовый Получатель',
                phone='+71112223344'
            )
            recipient.full_clean()  # Должен вызвать ошибку валидации

    def test_order_string_representation(self):
        """Тест строкового представления заказа в разных сценариях"""
        # Заказ только с заказчиком (User)
        order1 = Order.objects.create(
            user=self.user,
            delivery_address='адрес1',
            delivery_date=self.valid_delivery_date,
            total_price=1000
        )
        self.assertEqual(str(order1), f"Заказ #{order1.id} - {self.user.phone}")

        # Заказ с заказчиком (User) и получателем (Recipient)
        order2 = Order.objects.create(
            user=self.user,
            recipient=self.recipient,
            delivery_address='адрес2',
            delivery_date=self.valid_delivery_date,
            total_price=2000
        )
        self.assertEqual(str(order2), f"Заказ #{order2.id} - {self.recipient.phone}")

        # Попытка создать заказ с заказчиком без указания телефона
        with self.assertRaises(ValueError):
            user_no_phone = User.objects.create_user(name='nophone', phone='')
            order3 = Order.objects.create(
                user=user_no_phone,
                delivery_address='адрес3',
                delivery_date=self.valid_delivery_date,
                total_price=3000
            ).full_clean()


class OrderItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            name='orderitem_user',
            phone='+79996549871'
        )
        cls.order = Order.objects.create(
            user=cls.user,
            delivery_address='ул. Товарная, 5',
            delivery_date=timezone.now() + datetime.timedelta(hours=4),
            total_price=0
        )
        cls.bouquet = Bouquet.objects.create(
            name='Букет для Позиции',
            consists='Тюльпаны',
            price=1500,
            cost_price=700,
            pic1='item_bouquet.jpg'
        )

    def test_order_item_creation(self):
        """Тест создания позиции заказа"""
        item = OrderItem.objects.create(
            order=self.order,
            bouquet=self.bouquet,
            quantity=2,
            price=self.bouquet.price
        )

        self.assertEqual(item.order, self.order)
        self.assertEqual(item.bouquet, self.bouquet)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, 1500)
        self.assertEqual(item.total_price, 3000)
        self.assertEqual(str(item), "Букет для Позиции × 2")

    def test_order_item_with_different_price(self):
        """Тест позиции заказа с ценой, отличной от текущей цены букета"""
        item = OrderItem.objects.create(
            order=self.order,
            bouquet=self.bouquet,
            quantity=3,
            price=1200  # Цена со скидкой
        )

        self.assertEqual(item.price, 1200)
        self.assertEqual(item.total_price, 3600)

        # Проверяем, что цена букета не изменилась
        self.bouquet.refresh_from_db()
        self.assertEqual(self.bouquet.price, 1500)
