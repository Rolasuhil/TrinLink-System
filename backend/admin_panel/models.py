# ملف نماذج لوحة تحكم المدير
# يحتوي على النماذج المتعلقة بإدارة المحتوى والبلاغات في المنصة

from django.db import models
from accounts.models import Person


class ContentReport(models.Model):
    """نموذج بلاغ المحتوى
    يخزن بلاغات المستخدمين عن المحتوى المسيء أو المخالف في المنصة
    """

    # خيارات حالة البلاغ
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'تمت الموافقة'),
        ('removed', 'تمت الإزالة'),
    ]

    id = models.AutoField(primary_key=True)
    # المستخدم الذي قام بالإبلاغ
    reported_by = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='content_reports', verbose_name='المبلغ')
    # نوع المحتوى المبلّغ عنه (مثل: منشور، تعليق، فرصة تدريبية)
    content_type = models.CharField(max_length=50, verbose_name='نوع المحتوى')
    # معرّف المحتوى المبلّغ عنه
    content_id = models.IntegerField(verbose_name='معرف المحتوى')
    # سبب الإبلاغ من المستخدم
    reason = models.TextField(verbose_name='السبب')
    # حالة البلاغ (قيد المراجعة، تمت الموافقة، تمت الإزالة)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    # المدير الذي قام بمراجعة البلاغ
    reviewed_by = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports', verbose_name='قام بمراجعته')
    # تاريخ إنشاء البلاغ تلقائياً
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'بلاغ محتوى'
        verbose_name_plural = 'بلاغات المحتوى'

    def __str__(self):
        """تمثيل النصي للبلاغ"""
        return f'بلاغ {self.content_type} #{self.content_id} - {self.status}'
