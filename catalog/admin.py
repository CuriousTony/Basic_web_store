from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import Bouquet


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_bestseller', 'display_average_rating', 'image_preview')
    list_editable = ('price', 'is_bestseller')
    readonly_fields = ('average_rating', 'approved_reviews_count', 'image_preview')

    def save_model(self, request, obj, form, change):
        if obj.cost_price >= obj.price:
            raise ValidationError('Себестоимость должна быть меньше цены!')
        super().save_model(request, obj, form, change)

    def display_average_rating(self, obj):
        return f"{obj.average_rating:.1f}/5"

    display_average_rating.short_description = 'Рейтинг'

    def approved_reviews_count(self, obj):
        return obj.approved_reviews.count()

    approved_reviews_count.short_description = 'Одобренных отзывов'

    def image_preview(self, obj):
        if obj.pic1:
            return format_html('<img src="{}" height="100" />', obj.pic1.url)
        return "-"

    image_preview.short_description = 'Превью'
