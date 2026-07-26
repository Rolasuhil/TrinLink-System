# ملف إدارة لوحة تحكمjango للوحة تحكم المدير
# يسجل نموذج بلاغات المحتوى في لوحة التحكم لإدارتها

from django.contrib import admin
from .models import ContentReport


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    """إدارة بلاغات المحتوى في لوحة التحكم
    يعرض المُبلّغ ونوع المحتوى والحالة والتاريخ مع إمكانية التصفية
    """

    # الأعمدة المعروضة في قائمة البلاغات
    list_display = ['reported_by', 'content_type', 'content_id', 'status', 'created_at']
    # فلتر حسب الحالة ونوع المحتوى
    list_filter = ['status', 'content_type']
