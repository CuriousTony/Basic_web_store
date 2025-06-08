from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает суперпользователя для кастомной модели User'

    def handle(self, *args, **options):
        email = input("Email: ")
        phone = input("Телефон: ")
        address = input("Адрес: ")
        password = input("Пароль: ")

        User.objects.create_superuser(
            email=email,
            phone=phone,
            address=address,
            password=password
        )
        self.stdout.write(self.style.SUCCESS('Суперпользователь создан!'))
