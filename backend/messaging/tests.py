"""
Unit Tests for messaging app
White Box Testing: Testing internal logic of models and views
"""
from django.test import TestCase
from accounts.models import Person
from .models import ChatChannel, Message, Notification


class ChatChannelModelTest(TestCase):
    """Unit tests for ChatChannel model"""

    def setUp(self):
        self.user1 = Person.objects.create(
            full_name='المستخدم الأول',
            email='user1@test.com',
            person_type='trainee',
        )
        self.user2 = Person.objects.create(
            full_name='المستخدم الثاني',
            email='user2@test.com',
            person_type='company',
        )
        self.channel = ChatChannel.objects.create(
            name='قناة تجريبية',
            channel_type='direct',
        )
        self.channel.participants.add(self.user1, self.user2)

    def test_channel_creation(self):
        self.assertEqual(self.channel.name, 'قناة تجريبية')
        self.assertEqual(self.channel.channel_type, 'direct')

    def test_channel_participants(self):
        self.assertEqual(self.channel.participants.count(), 2)

    def test_channel_type_choices(self):
        self.assertIn(self.channel.channel_type, ['direct', 'group'])


class MessageModelTest(TestCase):
    """Unit tests for Message model"""

    def setUp(self):
        self.user1 = Person.objects.create(
            full_name='مرسل',
            email='sender@test.com',
            person_type='trainee',
        )
        self.user2 = Person.objects.create(
            full_name='مستلم',
            email='receiver@test.com',
            person_type='company',
        )
        self.channel = ChatChannel.objects.create(
            name='قناة رسائل',
            channel_type='direct',
        )
        self.channel.participants.add(self.user1, self.user2)

    def test_message_creation(self):
        msg = Message.objects.create(
            channel=self.channel,
            sender=self.user1,
            content='مرحباً، كيف حالك؟',
        )
        self.assertEqual(msg.content, 'مرحباً، كيف حالك؟')
        self.assertFalse(msg.is_read)

    def test_message_sender(self):
        msg = Message.objects.create(
            channel=self.channel,
            sender=self.user1,
            content='اختبار',
        )
        self.assertEqual(msg.sender.full_name, 'مرسل')

    def test_message_channel(self):
        msg = Message.objects.create(
            channel=self.channel,
            sender=self.user1,
            content='اختبار القناة',
        )
        self.assertEqual(msg.channel.name, 'قناة رسائل')

    def test_multiple_messages(self):
        Message.objects.create(channel=self.channel, sender=self.user1, content='رسالة 1')
        Message.objects.create(channel=self.channel, sender=self.user2, content='رسالة 2')
        Message.objects.create(channel=self.channel, sender=self.user1, content='رسالة 3')
        self.assertEqual(self.channel.messages.count(), 3)

    def test_message_read_status(self):
        msg = Message.objects.create(
            channel=self.channel,
            sender=self.user1,
            content='رسالة غير مقروءة',
        )
        self.assertFalse(msg.is_read)
        msg.is_read = True
        msg.save()
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)


class NotificationModelTest(TestCase):
    """Unit tests for Notification model"""

    def setUp(self):
        self.user = Person.objects.create(
            full_name='مستخدم إشعارات',
            email='notif@test.com',
            person_type='trainee',
        )

    def test_notification_creation(self):
        notif = Notification.objects.create(
            user=self.user,
            notification_type='application',
            title='تم قبول طلبك',
            message='تم قبولك في فرصة تدريب TechPal',
        )
        self.assertEqual(notif.title, 'تم قبول طلبك')
        self.assertFalse(notif.is_read)

    def test_notification_types(self):
        for ntype in ['application', 'message', 'report', 'alert', 'system']:
            Notification.objects.create(
                user=self.user,
                notification_type=ntype,
                title=f'إشعار {ntype}',
                message=f'رسالة {ntype}',
            )
        self.assertEqual(self.user.notifications.count(), 5)

    def test_notification_read_status(self):
        notif = Notification.objects.create(
            user=self.user,
            notification_type='system',
            title='إشعار نظام',
            message='مرحباً بك في النظام',
        )
        self.assertFalse(notif.is_read)

    def test_notification_with_link(self):
        notif = Notification.objects.create(
            user=self.user,
            notification_type='message',
            title='رسالة جديدة',
            message='لديك رسالة جديدة',
            link='/pages/company/23-chat.html',
        )
        self.assertEqual(notif.link, '/pages/company/23-chat.html')

    def test_user_notifications_count(self):
        for i in range(3):
            Notification.objects.create(
                user=self.user,
                notification_type='system',
                title=f'إشعار {i}',
                message=f'رسالة {i}',
            )
        self.assertEqual(self.user.notifications.count(), 3)

    def test_unread_notifications(self):
        Notification.objects.create(
            user=self.user,
            notification_type='system',
            title='مقروء',
            message='تم القراءة',
            is_read=True,
        )
        Notification.objects.create(
            user=self.user,
            notification_type='system',
            title='غير مقروء',
            message='لم يُقرأ',
            is_read=False,
        )
        unread = self.user.notifications.filter(is_read=False).count()
        self.assertEqual(unread, 1)
