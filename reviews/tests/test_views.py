import datetime
from django.conf import settings
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from orders.models import Order, OrderItem
from catalog.models import Bouquet
from reviews.models import Review
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class ReviewsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(password='testpass', name='tester', phone='+79991112233')
        self.bouquet = Bouquet.objects.create(
            name='Test Bouquet',
            price=1000,
            cost_price=700,
            pic1=SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg'),
            pic2=SimpleUploadedFile('test1.jpg', b'file_content', content_type='image/jpeg')
        )
        self.order = Order.objects.create(
            user=self.user,
            delivery_type='delivery',
            delivery_date=timezone.now() + datetime.timedelta(hours=3),
            total_price=1000,
            status='completed'
        )
        self.review = Review.objects.create(
            user=self.user,
            bouquet=self.bouquet,
            order=self.order,
            rating=5,
            text='Отлично!',
            is_approved=True
        )
        self.unapproved_review = Review.objects.create(
            user=self.user,
            bouquet=Bouquet.objects.create(
                name='Unapproved_bouquet',
                price=100,
                cost_price=70
            ),
            order=self.order,
            rating=5,
            text='Отлично!!',
            is_approved=False
        )

    def test_reviews_view_lists_only_approved(self):
        self.client.login(phone='+79991112233', password='testpass')
        url = reverse('reviews:reviews')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.review.text)
        self.assertNotContains(response, self.unapproved_review.text)

    def test_add_review_requires_login(self):
        url = reverse('reviews:add_review', args=[self.order.id, self.bouquet.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_add_review_only_completed_orders(self):
        # Ставим заказ НЕ завершённым
        self.order.status = 'pending'
        self.order.save()
        self.client.login(phone='+79991112233', password='testpass')
        url = reverse('reviews:add_review', args=[self.order.id, self.bouquet.id])
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('orders:order_details', args=[self.order.id]))
        self.assertContains(response, 'только для завершённых заказов.')

    def test_add_review_already_exists(self):
        self.client.login(phone='+79991112233', password='testpass')
        url = reverse('reviews:add_review', args=[self.order.id, self.bouquet.id])
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('orders:order_details', args=[self.order.id]))
        self.assertContains(response, 'Вы уже оставили отзыв на этот букет')

    def test_add_review_get_form(self):
        # Создаём новый заказ и букет для нового отзыва
        self.client.login(phone='+79991112233', password='testpass')
        new_bouquet = Bouquet.objects.create(name='Another', price=1000, cost_price=700)
        new_order = Order.objects.create(
            user=self.user,
            delivery_type='delivery',
            delivery_date=timezone.now() + datetime.timedelta(hours=3),
            total_price=1000,
            status='completed'
        )
        url = reverse('reviews:add_review', args=[new_order.id, new_bouquet.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_add_review_success_post(self):
        self.client.login(phone='+79991112233', password='testpass')

        # Создаем объекты
        new_bouquet = Bouquet.objects.create(
            name='Second',
            price=1000,
            cost_price=700,
            pic1=SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg'),
            pic2=SimpleUploadedFile('test2.jpg', b'file_content', content_type='image/jpeg')
        )
        new_order = Order.objects.create(
            user=self.user,
            delivery_type='delivery',
            delivery_date=timezone.now() + datetime.timedelta(hours=3),
            total_price=1000,
            status='completed'
        )
        OrderItem.objects.create(
            order=new_order,
            bouquet=new_bouquet,
            quantity=1,
            price=new_bouquet.price
        )

        url = reverse('reviews:add_review', args=[new_order.id, new_bouquet.id])
        data = {'rating': 4, 'text': 'Хорошо'}

        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('orders:order_details', args=[new_order.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Отзыв успешно сохранён!')
        session = self.client.session
        session.save()

        self.assertTrue(Review.objects.filter(
            user=self.user,
            bouquet=new_bouquet,
            order=new_order
        ).exists())

    def test_add_review_invalid_form(self):
        self.client.login(phone='+79991112233', password='testpass')
        # Новый букет и заказ
        new_bouquet = Bouquet.objects.create(name='Third', price=1000, cost_price=700)
        new_order = Order.objects.create(
            user=self.user,
            delivery_type='delivery',
            delivery_date=timezone.now() + datetime.timedelta(hours=3),
            total_price=1000,
            status='completed'
        )
        url = reverse('reviews:add_review', args=[new_order.id, new_bouquet.id])
        data = {
            'rating': '',  # Не передаём рейтинг, обязательное поле
            'text': 'Плохо',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Исправьте ошибки в форме.')
        # Отзыв не должен быть создан
        self.assertFalse(Review.objects.filter(
            user=self.user,
            bouquet=new_bouquet,
            order=new_order,
            text='Плохо'
        ).exists())
