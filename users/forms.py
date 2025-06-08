from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django import forms

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'phone',
            'name',
            'password1',
            'password2'
        ]
        labels = {
            'phone': 'Телефон',
            'name': 'Имя',
            'password': 'Пароль',
        }
        help_texts = {
            'phone': 'Формат +79991234567'
        }


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Телефон",
        validators=[
            RegexValidator(
                regex=r'^\+7\d{10}$',
                message='Ожидаемый формат номера: +79991234567'
            )
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].label = "Пароль"
