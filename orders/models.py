import datetime
from django.db import models
from django.db.models import Sum, Avg, Count, F
from django.utils import timezone
from django.conf import settings
from catalog.models import Bouquet


class OrderQuerySet(models.QuerySet):
    def for_period(self, start, end):
        return self.filter(created_at__range=(start, end))

    def sales_report(self):
        return self.aggregate(
            total_sales=Sum('total_price'),
            avg_order=Avg('total_price'),
            count=Count('id')
        )


def min_delivery_time():
    return timezone.now() + datetime.timedelta(hours=2)


class Order(models.Model):
    STATUS_CHOICES = [
        ('prepaid', 'Предоплачен'),
        ('pending', 'В обработке'),
        ('confirmed', 'Подтверждён'),
        ('processing', 'В доставке'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    DELIVERY_CHOICES = [
        ('delivery', 'Доставка'),
        ('pickup', 'Самовывоз'),
    ]
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default='delivery',
        verbose_name='Тип доставки'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    recipient = models.ForeignKey(
        'users.Recipient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Получатель'
    )
    delivery_address = models.CharField(max_length=255)
    delivery_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prepaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        recipient_phone = self.recipient.phone if self.recipient else self.user.phone
        return f"Заказ #{self.id} - {recipient_phone}"

    def update_total(self):
        self.total_price = self.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0
        self.save(update_fields=['total_price'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    bouquet = models.ForeignKey(Bouquet, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    @property
    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.bouquet.name} × {self.quantity}"
