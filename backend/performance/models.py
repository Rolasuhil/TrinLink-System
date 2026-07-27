# ملف نماذج أداء النظام
# يحتوي على النماذج المتعلقة بالإشراف على المتدربين والتقارير اليومية والأسبوعية وسجلات الحضور

from django.db import models
from accounts.models import Trainee, SupervisorProfile, CompanyProfile


class SupervisionAssignment(models.Model):
    """نموذج تعيين الإشراف
    يربط المتدرب بالمشرف المسؤول عن متابعته أثناء فترة التدريب
    """

    # خيارات حالة الإشراف
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    # خيارات نوع الإشراف (أكاديمي أو ميداني)
    ROLE_CHOICES = [
        ('academic', 'أكاديمي'),
        ('field', 'ميداني'),
    ]

    id = models.AutoField(primary_key=True)
    # المشرف المسؤول عن متابعة المتدرب
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.CASCADE, related_name='assignments', verbose_name='المشرف')
    # المتدرب تحت الإشراف
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='supervision_assignments', verbose_name='المتدرب')
    # تاريخ تعيين الإشراف تلقائياً
    assignment_date = models.DateField(auto_now_add=True, verbose_name='تاريخ التعيين')
    # نوع الإشراف (أكاديمي أو ميداني)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='academic', verbose_name='نوع الإشراف')
    # حالة الإشراف
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')

    class Meta:
        verbose_name = 'إشراف'
        verbose_name_plural = 'عمليات الإشراف'

    def __str__(self):
        """تمثيل النصي لعملية الإشراف"""
        return f'{self.supervisor.person.full_name} يشرف على {self.trainee.person.full_name}'


class Report(models.Model):
    """نموذج التقرير الإشرافي
    يخزن تقارير المشرف الدورية عن المتدرب مع التقييم والملاحظات
    """

    id = models.AutoField(primary_key=True)
    # رابط عملية الإشراف المرتبطة بالتقرير
    assignment = models.ForeignKey(SupervisionAssignment, on_delete=models.CASCADE, related_name='reports', verbose_name='الإشراف')
    # تاريخ إنشاء التقرير تلقائياً
    report_date = models.DateField(auto_now_add=True, verbose_name='التاريخ')
    # درجة التقييم التي أعطاها المشرف
    grade = models.FloatField(default=0.0, verbose_name='التقييم')
    # ملاحظات المشرف على أداء المتدرب
    feedback = models.TextField(blank=True, verbose_name='الملاحظات')
    # ملف مرفق للتقرير (اختياري)
    file = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name='ملف التقرير')
    # رقم الأسبوع في فترة التدريب
    week_number = models.IntegerField(default=1, verbose_name='رقم الأسبوع')

    class Meta:
        verbose_name = 'تقرير إشرافي'
        verbose_name_plural = 'التقارير الإشرافية'
        # ترتيب التقارير من الأحدث إلى الأقدم
        ordering = ['-report_date']

    def __str__(self):
        """تمثيل النصي للتقرير الإشرافي"""
        return f'تقرير - {self.assignment} - أسبوع {self.week_number}'


class WorkReport(models.Model):
    """نموذج التقرير اليومي للمتدرب
    يخزن مهام المتدرب اليومية ووصفها مع ملاحظات الشركة وتقدير الأداء
    """

    id = models.AutoField(primary_key=True)
    # المتدرب الذي قام بتقديم التقرير
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='work_reports', verbose_name='المتدرب')
    # عنوان المهمة التي تم إنجازها
    task_title = models.CharField(max_length=300, verbose_name='عنوان المهمة')
    # وصف تفصيلي للمهمة المنجزة
    description = models.TextField(verbose_name='الوصف')
    # ملف مرفق للتقرير (اختياري)
    attachment = models.FileField(upload_to='work_reports/', blank=True, null=True, verbose_name='المرفق')
    # تاريخ ووقت تسليم التقرير تلقائياً
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسليم')
    # ملاحظات الشركة على المهمة المنجزة
    company_feedback = models.TextField(blank=True, verbose_name='ملاحظات الشركة')
    # تقييم الأداء من الشركة (من 1 إلى 5)
    performance_rating = models.IntegerField(default=0, verbose_name='تقييم الأداء')

    class Meta:
        verbose_name = 'تقرير يومي'
        verbose_name_plural = 'التقارير اليومية'
        # ترتيب التقارير من الأحدث إلى الأقدم
        ordering = ['-submitted_at']

    def __str__(self):
        """تمثيل النصي للتقرير اليومي"""
        return f'{self.trainee.person.full_name} - {self.task_title}'


class PerformanceReport(models.Model):
    """نموذج التقرير الأدوي الأسبوعي
    يخزن تقييم أداء المتدرب الأسبوعي من الشركة مع تأكيد الحضور والملخص بالذكاء الاصطناعي
    """

    id = models.AutoField(primary_key=True)
    # المتدرب المرتبط بالتقرير
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='performance_reports', verbose_name='المتدرب')
    # الشركة التي تقيّم أداء المتدرب
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='performance_reports', verbose_name='الشركة')
    # رقم الأسبوع في فترة التدريب
    week_number = models.IntegerField(verbose_name='رقم الأسبوع')
    # هل تم تأكيد حضور المتدرب هذا الأسبوع
    attendance_confirmed = models.BooleanField(default=False, verbose_name='تم تأكيد الحضور')
    # درجة الأداء الأسبوعية
    performance_score = models.FloatField(default=0.0, verbose_name='درجة الأداء')
    # ملاحظات الشركة على الأداء
    comments = models.TextField(blank=True, verbose_name='الملاحظات')
    # ملخص مولّد بالذكاء الاصطناعي لأداء المتدرب
    ai_summary = models.TextField(blank=True, verbose_name='ملخص الذكاء الاصطناعي')
    # تقييم الذكاء الاصطناعي لأداء المتدرب
    ai_rating = models.CharField(max_length=20, blank=True, verbose_name='تقييم الذكاء الاصطناعي')
    # تاريخ إرسال التقرير تلقائياً
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')

    class Meta:
        verbose_name = 'تقرير أداء أسبوعي'
        verbose_name_plural = 'تقارير الأداء الأسبوعية'
        # ترتيب التقارير حسب رقم الأسبوع من الأعلى إلى الأقل
        ordering = ['-week_number']
        # ضمان عدم تكرار التقرير لنفس المتدرب والشركة ونفس الأسبوع
        unique_together = ['trainee', 'company', 'week_number']

    def __str__(self):
        """تمثيل النصي للتقرير الأدوي"""
        return f'أداء {self.trainee.person.full_name} - أسبوع {self.week_number}'


class DailyAttendance(models.Model):
    """نموذج سجل الحضور اليومي
    يخزن سجل حضور وانصراف المتدرب مع حالاته (حاضر، غائب، متأخر)
    """

    # خيارات حالة الحضور
    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('late', 'متأخر'),
    ]

    id = models.AutoField(primary_key=True)
    # المتدرب المرتبط بسجل الحضور
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='attendance', verbose_name='المتدرب')
    # تاريخ اليوم الذي تم تسجيل الحضور فيه
    date = models.DateField(verbose_name='التاريخ')
    # وقت تسجيل الحضور
    check_in_time = models.DateTimeField(null=True, blank=True, verbose_name='وقت الحضور')
    # وقت تسجيل الانصراف
    check_out_time = models.DateTimeField(null=True, blank=True, verbose_name='وقت الانصراف')
    # حالة الحضور (حاضر، غائب، متأخر)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present', verbose_name='الحالة')

    class Meta:
        verbose_name = 'سجل حضور'
        verbose_name_plural = 'سجلات الحضور'
        # ضمان وجود سجل واحد فقط لكل متدرب في كل يوم
        unique_together = ['trainee', 'date']

    def __str__(self):
        """تمثيل النصي لسجل الحضور"""
        return f'{self.trainee.person.full_name} - {self.date} ({self.get_status_display()})'
