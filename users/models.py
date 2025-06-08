from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


class PhoneValidator(RegexValidator):
    regex = r'^\+7\d{10}$'
    message = 'Ожидаемый формат номера: +79991234567'


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, name, password=None, **extra_fields):
        if not phone:
            raise ValueError('Номер телефона обязателен')
        if not name:
            raise ValueError('Имя обязательно')

        user = self.model(
            phone=phone,
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(
            phone=phone,
            name=name,
            password=password,
            **extra_fields
        )


class User(AbstractUser):
    username = None
    objects = CustomUserManager()

    phone = models.CharField(
        max_length=12,
        validators=[PhoneValidator()],
        verbose_name='Номер телефона',
        unique=True,
        help_text='Ожидаемый формат номера: +79991234567'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Имя',
        blank=False
    )
    email = models.EmailField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Почта'
    )
    address = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Адрес доставки'
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'{self.name} ({self.phone})'


class Recipient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Имя получателя'
    )
    phone = models.CharField(
        max_length=12,
        validators=[PhoneValidator()],
        verbose_name='Номер телефона получателя'
    )
    address = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Адрес доставки получателя'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f'{self.id}, {self.name} ({self.phone})'

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
