from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cart.models import Cart
from catalog.models import Bouquet

User = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.signup_url = reverse('users:signup')
        self.valid_data = {
            'name': 'tester',
            'phone': '+79991112233',
            'password1': 'Test_pass_2025!',
            'password2': 'Test_pass_2025!'
        }

    def test_signup_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/signup.html')
        self.assertContains(response, 'Регистрация')

    def test_signup_post_valid(self):
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertRedirects(response, reverse('main:home'))

        # проверка создания юзера
        user = User.objects.get(phone='+79991112233')
        self.assertEqual(user.name, 'tester')

        # проверка входа юзера
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        # проверка создания корзины при создании юзера
        self.assertTrue(Cart.objects.filter(user=user).exists())

    def test_signup_post_invalid(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'different_pass'
        response = self.client.post(self.signup_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('password2'))
        self.assertFalse(User.objects.filter(phone='+79991112233').exists())


class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.login_url = reverse('users:signin')
        self.user = User.objects.create_user(
            name='tester',
            phone='+79991112233',
            password='Test_pass_2025!'
        )
        self.valid_data = {
            'username': '+79991112233',
            'password': 'Test_pass_2025!'
        }

        self.bouquet = Bouquet.objects.create(
            name='Kenian_roses',
            price=1000,
            cost_price=700
        )

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/signin.html')
        self.assertContains(response, 'Вход')

    def test_login_post_valid(self):
        response = self.client.post(self.login_url, self.valid_data)
        self.assertRedirects(response, reverse('main:home'))

        # Проверяем вход пользователя
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_post_invalid(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'wrongpassword'
        response = self.client.post(self.login_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Please enter a correct Номер телефона'
                      ' and password. Note that both fields may be case-sensitive.',
                      response.context['form'].errors['__all__'])

    def test_cart_merging(self):
        # Создаем сессионную корзину и добавляем товар
        self.client.get(reverse('main:home'))
        session_cart_id = self.client.session.get('cart_id')
        session_cart = Cart.objects.get(id=session_cart_id)
        session_cart.items.create(bouquet=self.bouquet, quantity=2)

        # Выполняем вход
        self.client.post(self.login_url, self.valid_data)

        # Получаем обновленную корзину пользователя
        user_cart = Cart.objects.get(user=self.user)

        # Проверяем, что товары из сессионной корзины перенесены
        self.assertEqual(user_cart.items.count(), 1)
        cart_item = user_cart.items.first()
        self.assertEqual(cart_item.bouquet, self.bouquet)
        self.assertEqual(cart_item.quantity, 2)

        # Проверяем, что сессионная корзина удалена
        with self.assertRaises(Cart.DoesNotExist):
            Cart.objects.get(id=session_cart_id)
        self.assertNotIn('cart_id', self.client.session)
