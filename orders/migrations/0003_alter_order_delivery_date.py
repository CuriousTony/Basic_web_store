# Generated by Django 5.1.5 on 2025-05-20 15:36

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(datetime.datetime(2025, 5, 20, 17, 36, 55, 245444, tzinfo=datetime.timezone.utc))]),
        ),
    ]
