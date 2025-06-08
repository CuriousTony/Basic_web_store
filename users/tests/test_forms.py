from django.test import TestCase
from django.contrib.auth import get_user_model
from users.forms import CustomUserCreationForm, CustomLoginForm

User = get_user_model()


class CustomUserCreationFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'tester',
            'phone': '+79991112233',
            'password1': 'Test_pass_2025!',
            'password2': 'Test_pass_2025!',
        }

        User.objects.create_user(
            name='Existing User',
            phone='+79998887766',
            password='ExistingPass123!'
        )

    def test_form_valid(self):
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.phone, '+79991112233')
        self.assertEqual(user.name, 'tester')

    def test_phone_is_unique(self):

        data = self.valid_data.copy()
        data['phone'] = '+79998887766'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
        self.assertEqual(
            form.errors['phone'][0],
            'User with this Номер телефона already exists.'
        )

    def test_phone_format_validation(self):
        invalid_phones = [
            '89991234567',
            '+7999123456',
            '+799912345678',
            'abc',
        ]

        for phone in invalid_phones:
            with self.subTest(phone=phone):
                data = self.valid_data.copy()
                data['phone'] = phone
                form = CustomUserCreationForm(data=data)
                self.assertFalse(form.is_valid())
                self.assertIn('phone', form.errors)

    def test_password_invalid(self):
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass123!'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertEqual(
            form.errors['password2'][0],
            'The two password fields didn’t match.'
        )


class CustomLoginFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='tester',
            phone='+79991112233',
            password='Test_pass_2025!'
        )
        self.valid_data = {
            'username': '+79991112233',
            'password': 'Test_pass_2025!'
        }

    def test_loginform_valid(self):
        form = CustomLoginForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        """Проверка неверных учетных данных"""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'wrong_password'
        form = CustomLoginForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(
            form.errors['__all__'][0],
            'Please enter a correct Номер телефона and'
            ' password. Note that both fields may be case-sensitive.'
        )
