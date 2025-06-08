from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'bouquet', 'rating', 'is_approved', 'created_at')
    list_filter = ('order__status', 'is_approved', 'rating', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('user__email', 'bouquet__name', 'text')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} отзывов одобрено")

    approve_reviews.short_description = "Одобрить выбранные отзывы"
