from django.db import models
from django.db.models import Avg, Sum, F


class BouquetManager(models.Manager):
    def top_selling(self, start_date, end_date, limit=5):
        return self.annotate(
            total_sold=Sum(
                'orderitem__quantity',
                filter=models.Q(orderitem__order__created_at__date__range=(start_date, end_date))
            ),
            total_revenue=Sum(
                F('orderitem__price') * F('orderitem__quantity'),
                filter=models.Q(orderitem__order__created_at__date__range=(start_date, end_date))
            )
        ).order_by('-total_sold')[:limit]


class Bouquet(models.Model):
    name = models.CharField(max_length=30, blank=False, verbose_name='Название')
    consists = models.TextField(max_length=100, blank=False, verbose_name='Содержит')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Себестоимость',
                                     blank=False, null=False, default=0)
    pic1 = models.ImageField(upload_to='bouquets/', verbose_name='Фото1')
    pic2 = models.ImageField(upload_to='bouquets/', verbose_name='Фото2')
    is_bestseller = models.BooleanField(default=False, verbose_name='Бестселлер')
    objects = BouquetManager()

    @property
    def average_rating(self):
        return self.reviews.filter(is_approved=True,
                                   order__status='completed').aggregate(Avg('rating'))['rating__avg'] or 0

    @property
    def approved_reviews(self):
        return self.reviews.filter(is_approved=True)

    def __str__(self):
        return f"{self.name} {self.price}"
