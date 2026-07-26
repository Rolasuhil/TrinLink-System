from django.db import models
from accounts.models import Person, Trainee, CompanyProfile, SupervisorProfile


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='اسم التخصص')
    description = models.TextField(blank=True, verbose_name='الوصف')
    icon = models.CharField(max_length=50, blank=True, verbose_name='الأيقونة')

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'

    def __str__(self):
        return self.name


class Internship(models.Model):
    TYPE_CHOICES = [
        ('onsite', 'حضوري'),
        ('remote', 'عن بعد'),
        ('hybrid', 'مختلط'),
    ]
    STATUS_CHOICES = [
        ('open', 'مفتوح'),
        ('closed', 'مغلق'),
        ('full', 'مكتمل'),
    ]

    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='internships', verbose_name='الشركة')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='internships', verbose_name='التصنيف')
    title = models.CharField(max_length=300, verbose_name='المسمى الوظيفي')
    description = models.TextField(verbose_name='الوصف')
    requirements = models.TextField(blank=True, verbose_name='المتطلبات')
    deadline = models.DateField(verbose_name='آخر موعد للتقديم')
    available_positions = models.IntegerField(default=1, verbose_name='عدد المقاعد')
    location = models.CharField(max_length=200, verbose_name='الموقع')
    internship_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='onsite', verbose_name='النوع')
    start_date = models.DateField(verbose_name='تاريخ البدء')
    end_date = models.DateField(verbose_name='تاريخ الانتهاء')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='الحالة')
    acceptance_rate = models.FloatField(default=0.0, verbose_name='نسبة القبول')
    is_paid = models.BooleanField(default=False, verbose_name='مدفوع')
    learning_outcomes = models.TextField(blank=True, verbose_name='ما سيتعلمه المتدرب')
    additional_skills = models.TextField(blank=True, verbose_name='المهارات الإضافية')
    has_certificate = models.BooleanField(default=False, verbose_name='شهادة إتمام')
    work_days = models.CharField(max_length=50, blank=True, verbose_name='أيام العمل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ النشر')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        verbose_name = 'فرصة تدريب'
        verbose_name_plural = 'فرص التدريب'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.company.company_name}'

    def update_acceptance_rate(self):
        total = self.applications.count()
        accepted = self.applications.filter(status='accepted').count()
        self.acceptance_rate = (accepted / total * 100) if total > 0 else 0
        self.save(update_fields=['acceptance_rate'])


class SavedInternship(models.Model):
    id = models.AutoField(primary_key=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='saved_internships', verbose_name='المتدرب')
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='saved_by', verbose_name='الفرصة')
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الحفظ')

    class Meta:
        verbose_name = 'فرصة محفوظة'
        verbose_name_plural = 'الفرص المحفوظة'
        unique_together = ['trainee', 'internship']

    def __str__(self):
        return f'{self.trainee.person.full_name} حفظ {self.internship.title}'


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'معلق'),
        ('accepted', 'مقبول'),
        ('rejected', 'مرفوض'),
        ('withdrawn', 'مسحوب'),
    ]

    id = models.AutoField(primary_key=True)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='applications', verbose_name='الفرصة')
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='applications', verbose_name='المتدرب')
    application_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التقديم')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    resume_version = models.CharField(max_length=500, blank=True, verbose_name='السيرة الذاتية المستخدمة')
    cover_letter = models.TextField(blank=True, verbose_name='رسالة التقديم')
    rejection_reason = models.TextField(blank=True, verbose_name='سبب الرفض')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'طلب تقديم'
        verbose_name_plural = 'طلبات التقديم'
        unique_together = ['internship', 'trainee']
        ordering = ['-application_date']

    def __str__(self):
        return f'{self.trainee.person.full_name} - {self.internship.title} ({self.get_status_display()})'


class AcceptedTrainee(models.Model):
    id = models.AutoField(primary_key=True)
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='acceptance', verbose_name='الطلب')
    department = models.CharField(max_length=200, verbose_name='القسم')
    joining_date = models.DateField(verbose_name='تاريخ الالتحاق')
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_trainees', verbose_name='المشرف')

    class Meta:
        verbose_name = 'متدرب مقبول'
        verbose_name_plural = 'المتدربون المقبولون'

    def __str__(self):
        return f'{self.application.trainee.person.full_name} - مقبول في {self.department}'
