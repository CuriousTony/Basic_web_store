from django.test import TestCase
from django.urls import reverse
from catalog.models import Bouquet
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from reviews.views import reviews


class MainViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестовое изображение
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )

        # Создаем тестовые данные
        cls.bouquet1 = Bouquet.objects.create(
            name="Букет Нежность",
            price=3500,
            cost_price=2500,
            is_bestseller=True,
            pic1=test_image
        )
        cls.bouquet2 = Bouquet.objects.create(
            name="Королевский букет",
            price=6500,
            cost_price=5000,
            is_bestseller=True,
            pic1=test_image
        )
        cls.bouquet3 = Bouquet.objects.create(
            name="Летнее настроение",
            price=4200,
            cost_price=3100,
            is_bestseller=False,
            pic1=test_image
        )
        # Еще 3 бестселлера для проверки лимита
        for i in range(3, 6):
            Bouquet.objects.create(
                name=f"Бестселлер {i}",
                price=3000 + i * 100,
                is_bestseller=True,
                pic1=test_image
            )

    def test_home_view_status_code(self):
        """Проверка доступности главной страницы"""
        response = self.client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        """Проверка использования правильного шаблона"""
        response = self.client.get(reverse('main:home'))
        self.assertTemplateUsed(response, 'main/home.html')

    def test_home_view_context(self):
        """Проверка контекста главной страницы"""
        response = self.client.get(reverse('main:home'))

        # Проверяем передачу всех букетов
        self.assertIn('bouquets', response.context)
        self.assertEqual(len(response.context['bouquets']), 6)

        # Проверяем передачу бестселлеров (не более 4)
        self.assertIn('bestsellers', response.context)
        self.assertEqual(len(response.context['bestsellers']), 4)

        # Проверяем что в бестселлерах только помеченные
        for bouquet in response.context['bestsellers']:
            self.assertTrue(bouquet.is_bestseller)

    def test_about_view_status_code(self):
        """Проверка доступности страницы 'О нас'"""
        response = self.client.get(reverse('main:about'))
        self.assertEqual(response.status_code, 200)

    def test_about_view_template(self):
        """Проверка шаблона страницы 'О нас'"""
        response = self.client.get(reverse('main:about'))
        self.assertTemplateUsed(response, 'main/about.html')

    def test_payment_view_status_code(self):
        """Проверка доступности страницы оплаты"""
        response = self.client.get(reverse('main:payment'))
        self.assertEqual(response.status_code, 200)

    def test_payment_view_template(self):
        """Проверка шаблона страницы оплаты"""
        response = self.client.get(reverse('main:payment'))
        self.assertTemplateUsed(response, 'main/payment.html')

    def test_home_content(self):
        response = self.client.get(reverse('main:home'))
        self.assertContains(response, "Букет Нежность")
        self.assertContains(response, "Королевский букет")
        self.assertNotContains(response, "Несуществующий букет")
