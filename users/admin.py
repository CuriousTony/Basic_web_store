from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Recipient


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Персональная информация', {'fields': ('name',)}),
        ('Дополнительная информация', {
            'classes': ('collapse',),
            'fields': ('email', 'address'),
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'password1', 'password2'),
        }),
    )
    list_display = ('phone', 'name', 'is_staff')
    search_fields = ('phone', 'name')
    ordering = ('phone',)


class RecipientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'user', 'created_at')
    search_fields = ('name', 'phone', 'user__phone')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)


# admin.site.register(User, CustomUserAdmin)
# admin.site.register(Recipient, RecipientAdmin)
