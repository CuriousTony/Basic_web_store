from django import forms
from django.core.exceptions import ValidationError
from .models import Review
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'text': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)
        self.bouquet = kwargs.pop('bouquet', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Field('rating', css_class='form_check_input'),
                css_class='form-group mb4'
            ),
            Submit('submit', 'Отправить отзыв', css_class='btn-primary')
        )

    def clean(self):
        cleaned_data = super().clean()
        if not self.order or not self.bouquet:
            raise ValidationError('Недостаточно данных для проверки заказа.')

        if not self.order.items.filter(bouquet=self.bouquet).exists():
            raise ValidationError('Этот букет не был куплен в данном заказе.')

        return cleaned_data
