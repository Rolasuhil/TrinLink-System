from django.contrib import admin
from .models import ChatChannel, Message, Notification


@admin.register(ChatChannel)
class ChatChannelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'channel_type', 'created_at']
    list_filter = ['channel_type']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'channel', 'content', 'is_read', 'sent_at']
    list_filter = ['is_read']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
