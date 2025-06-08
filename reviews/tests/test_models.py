from datetime import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from catalog.models import Bouquet
from orders.models import Order
from reviews.models import Review
from django.utils import timezone
import datetime

User = get_user_model()


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='testuser',
            password='password',
            phone='1234567890'
        )
        self.bouquet = Bouquet.objects.create(
            name='Розы',
            price=1000,
            cost_price=700
        )
        self.order = Order.objects.create(
            user=self.user,
            delivery_type='delivery',
            delivery_date=timezone.now() + datetime.timedelta(hours=3),
            total_price=5000,
            status='completed'
        )

    def test_create_review(self):
        review = Review.objects.create(
            order=self.order,
            user=self.user,
            bouquet=self.bouquet,
            rating=5,
            text='Очень понравилось!'
        )
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, 'Очень понравилось!')
        self.assertFalse(review.is_approved)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.bouquet, self.bouquet)
        self.assertEqual(review.order, self.order)

    def test_rating_validators(self):
        review = Review(
            order=self.order,
            user=self.user,
            bouquet=self.bouquet,
            rating=0,  # некорректное значение
            text='Плохо'
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

        review.rating = 6  # тоже некорректно
        with self.assertRaises(ValidationError):
            review.full_clean()

        review.rating = 3  # корректно
        try:
            review.full_clean()
        except ValidationError:
            self.fail("Review with rating=3 should be valid")

    def test_unique_together_constraint(self):
        Review.objects.create(
            order=self.order,
            user=self.user,
            bouquet=self.bouquet,
            rating=4,
            text='Хорошо'
        )
        # Попытка создать второй отзыв тем же user и bouquet -- должно быть исключение
        review2 = Review(
            order=self.order,
            user=self.user,
            bouquet=self.bouquet,
            rating=5,
            text='Ещё лучше'
        )
        with self.assertRaises(ValidationError):
            review2.full_clean()

    def test_str_method(self):
        review = Review.objects.create(
            order=self.order,
            user=self.user,
            bouquet=self.bouquet,
            rating=4,
            text='Все отлично!'
        )
        expected = f"Отзыв {self.user.phone} на {self.bouquet.name}"
        self.assertEqual(str(review), expected)
