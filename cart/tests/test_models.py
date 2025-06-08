from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model
from cart.models import Cart, CartItem
from catalog.models import Bouquet

User = get_user_model()


# Тесты для модели Cart
class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone='+79991234567',
            name='tester',
            password='testpass'
        )

        # Корзина, созданная сигналом при создании user
        self.user_cart = Cart.objects.get(user=self.user)
        self.anon_cart = Cart.objects.create(session_key='test_session_key')
        self.bouquet1 = Bouquet.objects.create(
            name='Роза красная',
            price=1000
        )
        self.bouquet2 = Bouquet.objects.create(
            name='Тюльпан',
            price=500
        )

    def test_cart_creation(self):
        """Тестирование создания корзин"""
        self.assertEqual(Cart.objects.count(), 2)
        self.assertEqual(self.user_cart.user, self.user)
        self.assertEqual(self.anon_cart.session_key, 'test_session_key')

    def test_unique_constraint(self):
        """Тест валидации уникальности"""
        from django.core.exceptions import ValidationError

        # Проверка дублирования session_key
        with self.assertRaises(ValidationError):
            cart = Cart(session_key='test_session_key')
            cart.full_clean()

        # Проверка дублирования user
        with self.assertRaises(ValidationError):
            cart = Cart(user=self.user)
            cart.full_clean()

        # Проверка валидных случаев
        try:
            Cart(session_key='new_key').full_clean()
            Cart().full_clean()
        except ValidationError:
            self.fail("Валидация не должна падать для валидных данных")

    def test_str_representation(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.user_cart), 'Корзина (+79991234567)')
        self.assertEqual(str(self.anon_cart), 'Корзина (test_session_key)')

    def test_total_price_empty_cart(self):
        """Тест стоимости пустой корзины"""
        self.assertEqual(self.user_cart.total_price, 0)

    def test_add_item_method(self):
        """Тест добавления товара в корзину"""
        # Добавляем первый товар
        item = self.user_cart.add_item(self.bouquet1, 2)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, 1000)

        # Добавляем тот же товар еще раз
        item = self.user_cart.add_item(self.bouquet1, 3)
        self.assertEqual(item.quantity, 5)  # Должно суммироваться

        # Добавляем другой товар
        self.user_cart.add_item(self.bouquet2, 1)
        self.assertEqual(self.user_cart.items.count(), 2)

    def test_total_price_calculation(self):
        """Тест расчета общей стоимости"""
        self.user_cart.add_item(self.bouquet1, 2)  # 2 * 1000 = 2000
        self.user_cart.add_item(self.bouquet2, 3)  # 3 * 500 = 1500
        self.assertEqual(self.user_cart.total_price, 3500)

    def test_merge_carts(self):
        """Тест объединения корзин"""
        # Создаем нового пользователя и его корзину (автоматически через сигнал)
        new_user = User.objects.create_user(phone='+79998887766', name='tester', password='test')
        user_cart = new_user.carts.first()

        # Создаем корзину для сессии
        session_cart = Cart.objects.create(session_key='merge_test')
        session_cart.add_item(self.bouquet1, 1)
        session_cart.add_item(self.bouquet2, 2)

        # Добавляем товары в пользовательскую корзину
        user_cart.add_item(self.bouquet1, 3)

        # Объединяем корзины
        user_cart.merge_carts(session_cart)

        # Проверяем результаты
        self.assertEqual(user_cart.items.count(), 2)

        item1 = user_cart.items.get(bouquet=self.bouquet1)
        self.assertEqual(item1.quantity, 4)  # 3 + 1

        item2 = user_cart.items.get(bouquet=self.bouquet2)
        self.assertEqual(item2.quantity, 2)

        # Проверяем удаление старой корзины
        with self.assertRaises(Cart.DoesNotExist):
            Cart.objects.get(session_key='merge_test')


# Тесты для модели CartItem
class CartItemModelTest(CartModelTest):
    def setUp(self):
        super().setUp()

        self.cart_item1 = CartItem.objects.create(
            cart=self.user_cart,
            bouquet=self.bouquet1,
            quantity=2,
            price=1000
        )
        self.cart_item2 = CartItem.objects.create(
            cart=self.anon_cart,
            bouquet=self.bouquet2,
            quantity=3,
            price=500
        )

    def test_cart_item_creation(self):
        """Тест создания элемента корзины"""
        self.assertEqual(CartItem.objects.count(), 2)
        self.assertEqual(self.cart_item1.cart, self.user_cart)
        self.assertEqual(self.cart_item1.bouquet, self.bouquet1)
        self.assertEqual(self.cart_item1.quantity, 2)

    def test_string_representation(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.cart_item1), 'Роза красная × 2')
        self.assertEqual(str(self.cart_item2), 'Тюльпан × 3')

    def test_item_total_property(self):
        """Тест вычисления общей стоимости позиции"""
        self.assertEqual(self.cart_item1.item_total, 2000)
        self.assertEqual(self.cart_item2.item_total, 1500)

    def test_auto_price_on_save(self):
        """Тест автоматического заполнения цены из букета при сохранении"""
        # Используем новую корзину и новый букет чтобы избежать конфликта уникальности
        new_cart = Cart.objects.create(session_key='new_session')
        new_bouquet = Bouquet.objects.create(name='Новый букет', price=700)

        new_item = CartItem(
            cart=new_cart,
            bouquet=new_bouquet,
            quantity=1
        )
        new_item.save()
        self.assertEqual(new_item.price, new_bouquet.price)

    def test_unique_together_constraint(self):
        """Тест ограничения уникальности (корзина + букет)"""
        with self.assertRaises(IntegrityError):
            # Пытаемся создать дубликат существующего элемента
            CartItem.objects.create(
                cart=self.user_cart,
                bouquet=self.bouquet1,
                quantity=5,
                price=1000
            )

    def test_quantity_update_affects_total(self):
        """Тест изменения общей стоимости при обновлении количества"""
        self.cart_item1.quantity = 5
        self.cart_item1.save()
        self.assertEqual(self.cart_item1.item_total, 5000)

    def test_anonymous_cart_item(self):
        """Тест работы с анонимной корзиной"""
        item = CartItem.objects.create(
            cart=self.anon_cart,
            bouquet=self.bouquet1,
            quantity=1
        )
        self.assertEqual(item.cart, self.anon_cart)
        self.assertIsNone(item.cart.user)

    def test_add_item_method(self):
        """Тест добавления товара в корзину"""
        # Для чистоты теста используем новую корзину
        new_cart = Cart.objects.create(session_key='new_cart')

        item = new_cart.add_item(self.bouquet1)
        self.assertEqual(item.quantity, 1)

        item = new_cart.add_item(self.bouquet1)
        self.assertEqual(item.quantity, 2)

    def test_total_price_calculation(self):
        """Тест расчета общей стоимости"""
        new_cart = Cart.objects.create(session_key='new_cart')
        new_cart.add_item(self.bouquet1, quantity=2)
        new_cart.add_item(self.bouquet2, quantity=3)

        # 2*1000 + 3*500 = 2000 + 1500 = 3500
        self.assertEqual(new_cart.total_price, 3500)

    def test_total_price_empty_cart(self):
        """Тест стоимости пустой корзины"""
        new_cart = Cart.objects.create(session_key='empty_cart')
        self.assertEqual(new_cart.total_price, 0)
