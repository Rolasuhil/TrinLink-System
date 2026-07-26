"""
نماذج قاعدة البيانات لتطبيق الرسائل
تتضمن نماذج قنوات الدردشة والرسائل والإشعارات
"""

from django.db import models
from accounts.models import Person


# نموذج قنوات الدردشة (فردية أو مجموعة)
class ChatChannel(models.Model):
    """يمثل قناة دردشة يمكن أن تكون فردية (بين شخصين) أو جماعية (مجموعة أشخاص)"""
    # خيارات نوع القناة: فردية أو جماعية
    TYPE_CHOICES = [
        ('direct', 'فردي'),
        ('group', 'مجموعة'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, blank=True, verbose_name='اسم القناة')
    channel_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='direct', verbose_name='النوع')
    participants = models.ManyToManyField(Person, related_name='chat_channels', verbose_name='المشاركون')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        verbose_name = 'قناة دردشة'
        verbose_name_plural = 'قنوات الدردشة'
        # ترتيب القنوات حسب آخر تحديث (الأحدث أولاً)
        ordering = ['-updated_at']

    def __str__(self):
        return self.name or f'قناة {self.id}'

    @property
    def last_message(self):
        """إرجاع آخر رسالة في القناة"""
        return self.messages.first()


# نموذج الرسائل داخل قنوات الدردشة
class Message(models.Model):
    """يمثل رسالة نصية مرسلة داخل قناة دردشة"""
    id = models.AutoField(primary_key=True)
    channel = models.ForeignKey(ChatChannel, on_delete=models.CASCADE, related_name='messages', verbose_name='القناة')
    sender = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='المرسل')
    content = models.TextField(verbose_name='المحتوى')
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True, verbose_name='المرفق')
    is_read = models.BooleanField(default=False, verbose_name='مقروءة')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت الإرسال')

    class Meta:
        verbose_name = 'رسالة'
        verbose_name_plural = 'الرسائل'
        # ترتيب الرسائل تصاعدياً حسب وقت الإرسال
        ordering = ['sent_at']

    def __str__(self):
        return f'{self.sender.full_name}: {self.content[:50]}'


# نموذج الإشعارات للمستخدمين
class Notification(models.Model):
    """يمثل إشعاراً يُرسل للمستخدمين لتنبيههم بأحداث مختلفة"""
    # أنواع الإشعارات المتاحة
    TYPE_CHOICES = [
        ('application', 'طلب تقديم'),
        ('message', 'رسالة'),
        ('report', 'تقرير'),
        ('alert', 'تنبيه'),
        ('system', 'نظام'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='notifications', verbose_name='المستخدم')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system', verbose_name='النوع')
    title = models.CharField(max_length=300, verbose_name='العنوان')
    message = models.TextField(verbose_name='الرسالة')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    link = models.CharField(max_length=500, blank=True, verbose_name='الرابط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        # ترتيب الإشعارات من الأحدث إلى الأقدم
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.user.full_name}'
