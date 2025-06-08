from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Recipient, PhoneValidator
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()


class TestUserModel(TestCase):
    def test_user_creation(self):
        user = User.objects.create(
            name='tester',
            phone='+79991112233',
            email='test123@mail.ru',
            password='testpass123',
            address='Санкт-Петербург, Тестировочный пер, 12'
        )
        self.assertEqual(user.name, 'tester')
        self.assertEqual(user.phone, '+79991112233')
        self.assertEqual(user.email, 'test123@mail.ru')
        self.assertEqual(user.password, 'testpass123')
        self.assertEqual(user.address, 'Санкт-Петербург, Тестировочный пер, 12')
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_user_creation_no_params(self):
        # пробуем создать юзера без номера телефона
        with self.assertRaises(ValueError):
            User.objects.create_user(
                name='tester',
                phone='',
                password='test123'
            )
        # теперь без имени
        with self.assertRaises(ValueError):
            User.objects.create_user(
                name='',
                phone='+79991112233',
                password='test321'
            )

    def test_superuser_creation(self):
        admin_user = User.objects.create_superuser(
            name='superuser',
            phone='+79992223344',
            password='super123'
        )
        self.assertEqual(admin_user.name, 'superuser')
        self.assertEqual(admin_user.phone, '+79992223344')
        self.assertTrue(admin_user.check_password('super123'))
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)

    def test_phone_validation(self):
        validator = PhoneValidator()
        valid_numbers = ['+79991112233', '78882223344', '86665554433']
        for number in valid_numbers:
            validator(number)

        invalid_numbers = ['5554422', 'abc', '99955@6']
        for number in invalid_numbers:
            with self.assertRaises(ValidationError):
                validator(number)

    def test_phone_is_unique(self):
        User.objects.create(
            name='user1',
            phone='+79999999999',
            password='test123'
        )
        with self.assertRaises(IntegrityError):
            User.objects.create(
                name='user2',
                phone='+79999999999',
                password='test321'
            )

    def test_user_str_method(self):
        user = User.objects.create(
            name='tester',
            phone='+79991112233',
            password='test123'
        )
        self.assertEqual(str(user), 'tester (+79991112233)')


class TestRecipientModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name='main_user',
            phone='+79991112233',
            password='testpass'
        )

    def test_recipient_creation(self):
        recipient = Recipient.objects.create(
            user=self.user,
            name='recipient_user',
            phone='+71117778899'
        )
        self.assertEqual(recipient.name, 'recipient_user')
        self.assertEqual(recipient.phone, '+71117778899')
        self.assertEqual(recipient.user, self.user)
        self.assertIsNotNone(recipient.created_at)

    def test_recipient_user_relation(self):
        recipient1 = Recipient.objects.create(
            user=self.user,
            name='Recipient1',
            phone='+79991111111'
        )
        recipient2 = Recipient.objects.create(
            user=self.user,
            name='Recipient2',
            phone='+79992222222'
        )
        self.assertEqual(self.user.recipients.count(), 2)
        self.assertIn(recipient1, self.user.recipients.all())
        self.assertIn(recipient2, self.user.recipients.all())

    def test_recipient_phone_validation(self):
        recipient = Recipient.objects.create(
            user=self.user,
            name='recipient_invalid',
            phone='999asd'
        )
        with self.assertRaises(ValidationError):
            recipient.full_clean()

    def test_recipient_str_method(self):
        recipient = Recipient.objects.create(
            user=self.user,
            name='recipient_vasya',
            phone='+79994445566'
        )
        self.assertEqual(str(recipient), f'{recipient.id}, recipient_vasya (+79994445566)')

    def test_cascade_delete(self):
        # тестируем каскадное удаление получателя при удалении юзера
        Recipient.objects.create(
            user=self.user,
            name='recipient',
            phone='+79998887766'
        )
        self.assertEqual(Recipient.objects.count(), 1)
        self.user.delete()
        self.assertEqual(Recipient.objects.count(), 0)
