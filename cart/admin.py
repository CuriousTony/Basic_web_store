from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['bouquet']
    extra = 0
    readonly_fields = ('price',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'total_price')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

    def total_price(self, obj):
        return obj.get_total_price()

    total_price.short_description = 'Общая сумма'
