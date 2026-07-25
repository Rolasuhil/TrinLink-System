from django.urls import path
from . import views

urlpatterns = [
    path('channels/', views.ChatChannelListView.as_view(), name='chat-channels'),
    path('channels/<int:channel_id>/messages/', views.MessageListView.as_view(), name='chat-messages'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
]
