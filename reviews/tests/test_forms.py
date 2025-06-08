from django.test import TestCase
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from reviews.forms import ReviewForm
from orders.models import Order, OrderItem
from catalog.models import Bouquet

User = get_user_model()


class TestReviewForm(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name='tester',
            phone='+79991112233'
        )
        self.order = Order.objects.create(
            user=self.user,
            delivery_type='delivery',
            delivery_date=timezone.now() + datetime.timedelta(hours=3),
            total_price=1000,
            status='completed'
        )
        self.bouquet = Bouquet.objects.create(
            name='Magic_flowers',
            price=1000,
            cost_price=700
        )
        self.order_item=OrderItem.objects.create(
            order=self.order,
            bouquet=self.bouquet,
            quantity=1,
            price=1000
        )

    def test_review_creation(self):
        # теструем штатное создание формы со всеми данными
        form = ReviewForm(data={'rating': '4','text': 'Everythings perfect'},
                          bouquet=self.bouquet, order=self.order)
        self.assertTrue(form.is_valid(), form.errors)

    def test_review_creation_without_order_or_bouquet(self):
        # форма ожидает обязательные аргументы bouquet и order
        form = ReviewForm(data={'rating': '5', 'text': 'Все прекрасно!'})
        self.assertFalse(form.is_valid(), form.errors)
        assert 'Недостаточно данных для проверки заказа.' in form.non_field_errors()

    def test_review_creation_with_bouquet_only(self):
        # пробуем создать отзыв, передавая только букет
        form = ReviewForm(data={'rating': '5','text': 'Все отлично'},
                          bouquet=self.bouquet)
        self.assertFalse(form.is_valid(), form.errors)
        assert 'Недостаточно данных для проверки заказа.' in form.non_field_errors()
