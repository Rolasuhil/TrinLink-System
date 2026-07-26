"""
تسجيل النماذج في لوحة تحكم المشرف لتطبيق المجتمع
يُعرّف كيفية عرض بيانات المنشورات والتعليقات وتقييمات الشركات في لوحة التحكم
"""

from django.contrib import admin
from .models import CommunityPost, Comment, CompanyRating


# إعداد لوحة تحكم المنشورات المجتمعية
@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    """عرض وإدارة منشورات المجتمع في لوحة تحكم المشرف"""
    # الأعمدة المعروضة في قائمة المنشورات
    list_display = ['title', 'author', 'likes_count', 'comments_count', 'created_at']
    # تصفية المنشورات حسب حالة الموافقة
    list_filter = ['is_approved']


# إعداد لوحة تحكم التعليقات
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """عرض وإدارة التعليقات على المنشورات في لوحة تحكم المشرف"""
    list_display = ['author', 'post', 'content', 'created_at']


# إعداد لوحة تحكم تقييمات الشركات
@admin.register(CompanyRating)
class CompanyRatingAdmin(admin.ModelAdmin):
    """عرض وإدارة تقييمات الشركات في لوحة تحكم المشرف"""
    list_display = ['trainee', 'company', 'score', 'created_at']
    # تصفية التقييمات حسب درجة التقييم
    list_filter = ['score']
