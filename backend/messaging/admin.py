"""
تسجيل النماذج في لوحة تحكم المشرف لتطبيق الرسائل
يُعرّف كيفية عرض بيانات قنوات الدردشة والرسائل والإشعارات في لوحة التحكم
"""

from django.contrib import admin
from .models import ChatChannel, Message, Notification


# إعداد لوحة تحكم قنوات الدردشة
@admin.register(ChatChannel)
class ChatChannelAdmin(admin.ModelAdmin):
    """عرض وإدارة قنوات الدردشة في لوحة تحكم المشرف"""
    # الأعمدة المعروضة في قائمة القنوات
    list_display = ['id', 'name', 'channel_type', 'created_at']
    # تصفية القنوات حسب النوع (فردي أو مجموعة)
    list_filter = ['channel_type']


# إعداد لوحة تحكم الرسائل
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """عرض وإدارة الرسائل في لوحة تحكم المشرف"""
    # الأعمدة المعروضة مع حالة القراءة
    list_display = ['sender', 'channel', 'content', 'is_read', 'sent_at']
    # تصفية الرسائل حسب حالة القراءة
    list_filter = ['is_read']


# إعداد لوحة تحكم الإشعارات
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """عرض والإدارة الإشعارات في لوحة تحكم المشرف"""
    # الأعمدة المعروضة مع نوع الإشعار وحالة القراءة
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    # تصفية الإشعارات حسب النوع وحالة القراءة
    list_filter = ['notification_type', 'is_read']
