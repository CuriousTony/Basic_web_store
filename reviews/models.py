from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from catalog.models import Bouquet
from orders.models import Order


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Заказ',
        limit_choices_to={'status': 'completed'}
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='пользователь'
    )

    bouquet = models.ForeignKey(
        Bouquet,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='букет'
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ['user', 'bouquet']
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв {self.user.phone} на {self.bouquet.name}"
