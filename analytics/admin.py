import json

from django.contrib import admin
from django.utils.html import format_html
from analytics.models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('top_bouquets_preview',)

    def top_bouquets_preview(self, obj):
        return format_html("<pre>{}</pre>", json.dumps(obj.get_top_bouquets(), indent=2))

    top_bouquets_preview.short_description = "Топ букетов (JSON)"
