"""
تسجيل النماذج في لوحة إدارة Django
- تسجيل نموذج التصنيفات (Category) مع إمكانية البحث
- تسجيل نموذج فرصة التدريب (Internship) مع الفلاتر والتسلسل الزمني
- تسجيل نموذج طلب التقديم (Application) مع الفلاتر والبحث
- تسجيل نموذج الفرصة المحفوظة (SavedInternship)
- تسجيل نموذج المتدرب المقبول (AcceptedTrainee)
"""

from django.contrib import admin
from .models import Category, Internship, Application, SavedInternship, AcceptedTrainee


# ──────────────────────────────────────────────
# إدارة نموذج التصنيفات في لوحة التحكم
# ──────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج التصنيفات في لوحة إدارة Django"""
    list_display = ['name', 'description']  # الأعمدة المعروضة في القائمة
    search_fields = ['name']  # حقل البحث في لوحة التحكم


# ──────────────────────────────────────────────────
# إدارة نموذج فرصة التدريب في لوحة التحكم
# ──────────────────────────────────────────────────
@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج فرص التدريب في لوحة إدارة Django مع فلاتر متعددة"""
    # الأعمدة المعروضة في قائمة فرص التدريب
    list_display = ['title', 'company', 'category', 'location', 'internship_type', 'status', 'deadline']
    # فلاتر جانبية لتصفية الفرص حسب الحالة أو النوع أو التصنيف
    list_filter = ['status', 'internship_type', 'category']
    # حقول البحث في لوحة التحكم
    search_fields = ['title', 'company__company_name']
    # تسلسل زمني لعرض الفرص حسب تاريخ النشر
    date_hierarchy = 'created_at'


# ──────────────────────────────────────────────
# إدارة نموذج طلبات التقديم في لوحة التحكم
# ──────────────────────────────────────────────
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج طلبات التقديم في لوحة إدارة Django"""
    list_display = ['trainee', 'internship', 'status', 'application_date']  # الأعمدة المعروضة
    list_filter = ['status']  # فلتر حسب حالة الطلب (معلق/مقبول/مرفوض/مسحوب)
    # حقول البحث باسم المتدرب وعنوان الفرصة
    search_fields = ['trainee__person__full_name', 'internship__title']


# ──────────────────────────────────────────────────
# إدارة نموذج الفرصة المحفوظة في لوحة التحكم
# ──────────────────────────────────────────────────
@admin.register(SavedInternship)
class SavedInternshipAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج الفرصة المحفوظة في لوحة إدارة Django"""
    list_display = ['trainee', 'internship', 'saved_at']  # الأعمدة المعروضة


# ──────────────────────────────────────────────────
# إدارة نموذج المتدرب المقبول في لوحة التحكم
# ──────────────────────────────────────────────────
@admin.register(AcceptedTrainee)
class AcceptedTraineeAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج المتدرب المقبول في لوحة إدارة Django"""
    list_display = ['application', 'department', 'joining_date', 'supervisor']  # الأعمدة المعروضة
