from django.contrib import admin
from .models import ContentReport


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ['reported_by', 'content_type', 'content_id', 'status', 'created_at']
    list_filter = ['status', 'content_type']
