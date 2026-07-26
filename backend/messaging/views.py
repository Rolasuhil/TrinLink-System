"""
 views API لتطبيق الرسائل
تتضمن واجهات برمجية لإدارة قنوات الدردشة والرسائل والإشعارات
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatChannel, Message, Notification
from django.conf import settings
import jwt


# دالة مساعدة لاستخراج المستخدم من رمز JWT في رأس التصريح
def get_user(request):
    """تستخرج المستخدم الحالي من التوكن المُرسل في رأس Authorization"""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    try:
        payload = jwt.decode(auth.split(' ')[1], settings.SECRET_KEY, algorithms=['HS256'])
        from accounts.models import Person
        return Person.objects.get(user_id=payload['user_id'])
    except Exception:
        return None


# واجهة API لإدارة قنوات الدردشة
class ChatChannelListView(APIView):
    """عرض قائمة قنوات الدردشة الخاصة بالمستخدم أو إنشاء قناة فردية جديدة"""
    def get(self, request):
        """إرجاع جميع قنوات الدردشة التي يشارك فيها المستخدم مع آخر رسالة في كل قناة"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        channels = user.chat_channels.all()
        data = []
        for ch in channels:
            # استبعاد المستخدم الحالي من قائمة المشاركين لعرض الأسماء الأخرى فقط
            participants = ch.participants.exclude(id=user.id)
            last_msg = ch.last_message
            data.append({
                'id': ch.id,
                'name': ch.name or ', '.join([p.full_name for p in participants]),
                'channel_type': ch.channel_type,
                'participants': [{'id': p.id, 'name': p.full_name} for p in participants],
                'last_message': {
                    'content': last_msg.content if last_msg else '',
                    'sent_at': str(last_msg.sent_at) if last_msg else '',
                    'sender': last_msg.sender.full_name if last_msg else '',
                },
            })
        return Response(data)

    def post(self, request):
        """إنشاء قناة دردشة فردية جديدة بين المستخدم الحالي والمستخدم المحدد"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        from accounts.models import Person
        recipient_id = request.data.get('recipient_id')
        try:
            recipient = Person.objects.get(id=recipient_id)
        except Person.DoesNotExist:
            return Response({'error': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        # التحقق من وجود قناة فردية مسبقاً بين المستخدمين لتجنب التكرار
        existing = ChatChannel.objects.filter(channel_type='direct', participants=user).filter(participants=recipient)
        if existing.exists():
            return Response({'id': existing.first().id, 'message': 'القناة موجودة مسبقاً'})

        channel = ChatChannel.objects.create(channel_type='direct')
        channel.participants.add(user, recipient)
        return Response({'id': channel.id, 'message': 'تم إنشاء القناة'}, status=status.HTTP_201_CREATED)


# واجهة API لإدارة الرسائل داخل قناة دردشة
class MessageListView(APIView):
    """عرض جميع رسائل قناة معينة أو إرسال رسالة جديدة فيها"""
    def get(self, request, channel_id):
        """إرجاع جميع الرسائل في قناة محددة بعد التحقق من مشاركة المستخدم في القناة"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            channel = ChatChannel.objects.get(id=channel_id, participants=user)
        except ChatChannel.DoesNotExist:
            return Response({'error': 'القناة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        messages = channel.messages.all()
        data = [{
            'id': m.id,
            'sender_id': m.sender.id,
            'sender_name': m.sender.full_name,
            'content': m.content,
            'attachment': m.attachment.url if m.attachment else None,
            'is_read': m.is_read,
            'sent_at': str(m.sent_at),
        } for m in messages]
        return Response(data)

    def post(self, request, channel_id):
        """إرسال رسالة جديدة في قناة معينة وإنشاء إشعار لكل مشارك آخر"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            channel = ChatChannel.objects.get(id=channel_id, participants=user)
        except ChatChannel.DoesNotExist:
            return Response({'error': 'القناة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        msg = Message.objects.create(
            channel=channel,
            sender=user,
            content=request.data.get('content', ''),
        )

        # إنشاء إشعار لكل مشارك آخر في القناة
        recipients = channel.participants.exclude(id=user.id)
        for r in recipients:
            Notification.objects.create(
                user=r,
                notification_type='message',
                title='رسالة جديدة',
                message=f'رسالة جديدة من {user.full_name}',
                link=f'/chat/{channel_id}',
            )

        return Response({
            'id': msg.id,
            'content': msg.content,
            'sent_at': str(msg.sent_at),
            'message': 'تم الإرسال'
        }, status=status.HTTP_201_CREATED)


# واجهة API لإدارة إشعارات المستخدم
class NotificationListView(APIView):
    """عرض إشعارات المستخدم وتحديث حالة قراءتها"""
    def get(self, request):
        """إرجاع آخر 50 إشعار للمستخدم مع عدد الإشعارات غير المقروءة"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        notifications = user.notifications.all()[:50]
        unread_count = user.notifications.filter(is_read=False).count()

        data = [{
            'id': n.id,
            'type': n.notification_type,
            'title': n.title,
            'message': n.message,
            'is_read': n.is_read,
            'link': n.link,
            'created_at': str(n.created_at),
        } for n in notifications]

        return Response({'notifications': data, 'unread_count': unread_count})

    def patch(self, request):
        """تحديث حالة الإشعار: تعليم الكل كمقروء أو تعليم إشعار واحد كمقروء"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        # تعليم جميع الإشعارات غير المقروءة كمقروءة
        if request.data.get('mark_all_read'):
            user.notifications.filter(is_read=False).update(is_read=True)
        # تعليم إشعار محدد كمقروء
        elif request.data.get('notification_id'):
            try:
                n = user.notifications.get(id=request.data['notification_id'])
                n.is_read = True
                n.save()
            except Notification.DoesNotExist:
                pass

        return Response({'message': 'تم التحديث'})
