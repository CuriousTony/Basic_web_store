# Generated by Django 5.1.5 on 2025-05-26 13:22

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_alter_order_delivery_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(datetime.datetime(2025, 5, 26, 15, 22, 0, 39858, tzinfo=datetime.timezone.utc))]),
        ),
    ]
