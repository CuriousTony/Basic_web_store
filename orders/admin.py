from django.contrib import admin
from django import forms
from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        help_texts = {
            'delivery_address': 'Обязательное поле',
            'contact_phone': 'Обязательное поле',
            'delivery_date': 'Обязательное поле'
        }


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['bouquet', 'quantity', 'price']
    readonly_fields = ['price']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'delivery_type', 'total_price')
    list_filter = ('status', 'delivery_type')
    actions = ['mark_confirmed', 'mark_processing', 'mark_completed', 'mark_cancelled']
    list_per_page = 20

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "Подтвердить выбранные заказы"

    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_processing.short_description = "Перевести в доставку"

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "Завершить заказы"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = "Отменить выбранные заказы"

    def has_delete_permission(self, request, obj=None):
        return False
