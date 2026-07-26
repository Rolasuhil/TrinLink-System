"""
مسارات API لتطبيق الرسائل
تُعرّف نقاط النهاية لقنوات الدردشة والرسائل والإشعارات
"""

from django.urls import path
from . import views

urlpatterns = [
    # عرض جميع قنوات الدردشة وإنشاء قناة جديدة
    path('channels/', views.ChatChannelListView.as_view(), name='chat-channels'),
    # عرض رسائل قناة معينة وإرسال رسالة جديدة فيها
    path('channels/<int:channel_id>/messages/', views.MessageListView.as_view(), name='chat-messages'),
    # عرض إشعارات المستخدم وتحديث حالة قراءتها
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
]
