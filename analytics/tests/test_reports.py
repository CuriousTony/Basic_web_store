from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from analytics.reports import (
    get_revenue,
    get_profit,
    get_order_count,
    get_bouquets_sold,
    get_top_users,
    get_top_bouquets
)
from django.contrib.auth import get_user_model
from catalog.models import Bouquet
from orders.models import Order, OrderItem

User = get_user_model()


class ReportsTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.start_date = self.now - timedelta(days=7)
        self.end_date = self.now
        self.outside_date = self.now - timedelta(days=10)
        self.delivery_date = self.now + timedelta(hours=3)

        self.user1 = User.objects.create(name='user1', phone='+79111111111')
        self.user2 = User.objects.create(name='user2', phone='+79222222222')

        self.bouquet1 = Bouquet.objects.create(
            name='Розы',
            cost_price=500,
            price=1000
        )
        self.bouquet2 = Bouquet.objects.create(
            name='Тюльпаны',
            cost_price=300,
            price=700
        )

        # Создаем заказы и обновляем created_at
        self.order1 = Order.objects.create(
            user=self.user1,
            total_price=1000,
            delivery_date=self.delivery_date,
            delivery_address='Address 1'
        )
        self.order1.created_at = self.now - timedelta(days=2)
        self.order1.save()

        self.order2 = Order.objects.create(
            user=self.user2,
            total_price=1400,
            delivery_date=self.delivery_date,
            delivery_address='Address 2'
        )
        self.order2.created_at = self.now - timedelta(days=1)
        self.order2.save()

        # Заказ вне периода
        self.order3 = Order.objects.create(
            user=self.user1,
            total_price=1000,
            delivery_date=self.delivery_date,
            delivery_address='Address 3'
        )
        self.order3.created_at = self.outside_date
        self.order3.save()

        # Позиции заказов
        OrderItem.objects.create(
            order=self.order1,
            bouquet=self.bouquet1,
            quantity=1,
            price=1000
        )
        OrderItem.objects.create(
            order=self.order2,
            bouquet=self.bouquet2,
            quantity=2,
            price=700
        )

    def test_get_revenue(self):
        revenue = get_revenue(self.start_date, self.end_date)
        expected = 1000 + 1400
        self.assertEqual(revenue, expected)

    def test_get_profit(self):
        profit = get_profit(self.start_date, self.end_date)
        expected_profit = 2400 - (500*1 + 300*2)
        self.assertEqual(profit, expected_profit)

    def test_get_order_count(self):
        count = get_order_count(self.start_date, self.end_date)
        self.assertEqual(count, 2)

    def test_get_bouquets_sold(self):
        total_sold = get_bouquets_sold(self.start_date, self.end_date)
        expected = 1 + 2
        self.assertEqual(total_sold, expected)

    def test_get_top_users(self):
        top_users = get_top_users(self.start_date, self.end_date)
        self.assertEqual(len(top_users), 2)
        self.assertIn(self.user1, top_users)
        self.assertIn(self.user2, top_users)

    def test_get_top_bouquets(self):
        top_bouquets = get_top_bouquets(self.start_date, self.end_date)
        self.assertEqual(len(top_bouquets), 2)
        self.assertEqual(top_bouquets[0], self.bouquet2)
        self.assertEqual(top_bouquets[1], self.bouquet1)
