from django.db import models
from django.conf import settings
from django.db.models import Sum, F
from catalog.models import Bouquet


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'session_key'],
                name='unique_cart_identifier'
            )
        ]

    def __str__(self):
        identifier = self.user.phone if self.user else self.session_key
        return f"Корзина ({identifier})"

    @property
    def total_price(self):
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total']
        return total if total else 0

    def merge_carts(self, session_cart):
        for item in session_cart.items.all():
            existing = self.items.filter(bouquet=item.bouquet).first()
            if existing:
                existing.quantity += item.quantity
                existing.save()
            else:
                item.cart = self
                item.save()
        session_cart.delete()

    def add_item(self, bouquet, quantity=1):
        cart_item, created = self.items.get_or_create(
            bouquet=bouquet,
            defaults={
                'quantity': quantity,
                'price': bouquet.price
            }
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    def clean(self):
        from django.core.exceptions import ValidationError

        # Проверка уникальности user
        if self.user_id:
            existing = Cart.objects.filter(user=self.user).exclude(id=self.id)
            if existing.exists():
                raise ValidationError("Пользователь уже имеет корзину")

        # Проверка уникальности session_key
        if self.session_key:
            existing = Cart.objects.filter(session_key=self.session_key).exclude(id=self.id)
            if existing.exists():
                raise ValidationError("Корзина с этим ключом сессии уже существует")

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызываем валидацию
        super().save(*args, **kwargs)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        unique_together = ['cart', 'bouquet']

    def __str__(self):
        return f"{self.bouquet.name} × {self.quantity}"

    @property
    def item_total(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if not self.price and self.bouquet:
            self.price = self.bouquet.price
        super().save(*args, **kwargs)
