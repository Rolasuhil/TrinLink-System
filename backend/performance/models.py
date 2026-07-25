from django.db import models
from accounts.models import Trainee, SupervisorProfile, CompanyProfile


class SupervisionAssignment(models.Model):
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    ROLE_CHOICES = [
        ('academic', 'أكاديمي'),
        ('field', 'ميداني'),
    ]

    id = models.AutoField(primary_key=True)
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.CASCADE, related_name='assignments', verbose_name='المشرف')
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='supervision_assignments', verbose_name='المتدرب')
    assignment_date = models.DateField(auto_now_add=True, verbose_name='تاريخ التعيين')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='academic', verbose_name='نوع الإشراف')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')

    class Meta:
        verbose_name = 'إشراف'
        verbose_name_plural = 'عمليات الإشراف'

    def __str__(self):
        return f'{self.supervisor.person.full_name} يشرف على {self.trainee.person.full_name}'


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(SupervisionAssignment, on_delete=models.CASCADE, related_name='reports', verbose_name='الإشراف')
    report_date = models.DateField(auto_now_add=True, verbose_name='التاريخ')
    grade = models.FloatField(default=0.0, verbose_name='التقييم')
    feedback = models.TextField(blank=True, verbose_name='الملاحظات')
    file = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name='ملف التقرير')
    week_number = models.IntegerField(default=1, verbose_name='رقم الأسبوع')

    class Meta:
        verbose_name = 'تقرير إشرافي'
        verbose_name_plural = 'التقارير الإشرافية'
        ordering = ['-report_date']

    def __str__(self):
        return f'تقرير - {self.assignment} - أسبوع {self.week_number}'


class WorkReport(models.Model):
    id = models.AutoField(primary_key=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='work_reports', verbose_name='المتدرب')
    task_title = models.CharField(max_length=300, verbose_name='عنوان المهمة')
    description = models.TextField(verbose_name='الوصف')
    attachment = models.FileField(upload_to='work_reports/', blank=True, null=True, verbose_name='المرفق')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسليم')
    company_feedback = models.TextField(blank=True, verbose_name='ملاحظات الشركة')
    performance_rating = models.IntegerField(default=0, verbose_name='تقييم الأداء')

    class Meta:
        verbose_name = 'تقرير يومي'
        verbose_name_plural = 'التقارير اليومية'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.trainee.person.full_name} - {self.task_title}'


class PerformanceReport(models.Model):
    id = models.AutoField(primary_key=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='performance_reports', verbose_name='المتدرب')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='performance_reports', verbose_name='الشركة')
    week_number = models.IntegerField(verbose_name='رقم الأسبوع')
    attendance_confirmed = models.BooleanField(default=False, verbose_name='تم تأكيد الحضور')
    performance_score = models.FloatField(default=0.0, verbose_name='درجة الأداء')
    comments = models.TextField(blank=True, verbose_name='الملاحظات')
    ai_summary = models.TextField(blank=True, verbose_name='ملخص الذكاء الاصطناعي')
    ai_rating = models.CharField(max_length=20, blank=True, verbose_name='تقييم الذكاء الاصطناعي')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')

    class Meta:
        verbose_name = 'تقرير أداء أسبوعي'
        verbose_name_plural = 'تقارير الأداء الأسبوعية'
        ordering = ['-week_number']
        unique_together = ['trainee', 'company', 'week_number']

    def __str__(self):
        return f'أداء {self.trainee.person.full_name} - أسبوع {self.week_number}'


class DailyAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('late', 'متأخر'),
    ]

    id = models.AutoField(primary_key=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='attendance', verbose_name='المتدرب')
    date = models.DateField(verbose_name='التاريخ')
    check_in_time = models.DateTimeField(null=True, blank=True, verbose_name='وقت الحضور')
    check_out_time = models.DateTimeField(null=True, blank=True, verbose_name='وقت الانصراف')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present', verbose_name='الحالة')

    class Meta:
        verbose_name = 'سجل حضور'
        verbose_name_plural = 'سجلات الحضور'
        unique_together = ['trainee', 'date']

    def __str__(self):
        return f'{self.trainee.person.full_name} - {self.date} ({self.get_status_display()})'
