from django.db import models
from accounts.models import Person


class ContentReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'تمت الموافقة'),
        ('removed', 'تمت الإزالة'),
    ]

    id = models.AutoField(primary_key=True)
    reported_by = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='content_reports', verbose_name='المبلغ')
    content_type = models.CharField(max_length=50, verbose_name='نوع المحتوى')
    content_id = models.IntegerField(verbose_name='معرف المحتوى')
    reason = models.TextField(verbose_name='السبب')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    reviewed_by = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports', verbose_name='قام بمراجعته')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'بلاغ محتوى'
        verbose_name_plural = 'بلاغات المحتوى'

    def __str__(self):
        return f'بلاغ {self.content_type} #{self.content_id} - {self.status}'
