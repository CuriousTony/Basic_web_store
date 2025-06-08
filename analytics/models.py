from django.db import models
from django.db.models import JSONField


class Report(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'День'),
        ('weekly', 'Неделя'),
        ('monthly', 'Месяц')
    ]

    period_type = models.CharField(max_length=7, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    top_bouquets = JSONField(default=dict)

    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'
        indexes = [models.Index(fields=['start_date', 'end_date'])]

    @property
    def top_bouquets_data(self):
        return self.top_bouquets
