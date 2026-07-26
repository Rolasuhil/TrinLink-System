"""
نماذج قاعدة البيانات للتدريب والتقديمات
- تعريف نموذج التصنيفات (Category) لتصنيف فرص التدريب
- تعريف نموذج فرصة التدريب (Internship) مع جميع تفاصيلها
- تعريف نموذج الفرصة المحفوظة (SavedInternship) للمتدربين
- تعريف نموذج طلب التقديم (Application) مع حالاته المختلفة
- تعريف نموذج المتدرب المقبول (AcceptedTrainee) مع معلومات الالتحاق
"""

from django.db import models
from accounts.models import Person, Trainee, CompanyProfile, SupervisorProfile


# ──────────────────────────────────────────────
# نموذج التصنيفات - يُستخدم لتصنيف فرص التدريب
# ──────────────────────────────────────────────
class Category(models.Model):
    """يمثل تصنيفاً واحداً (مثل: هندسة، تكنولوجيا، تسويق...) يُستخدم لتجميع فرص التدريب"""

    id = models.AutoField(primary_key=True)  # المعرف الفريد للتصنيف
    name = models.CharField(max_length=200, verbose_name='اسم التخصص')  # اسم التصنيف
    description = models.TextField(blank=True, verbose_name='الوصف')  # وصف مختصر للتصنيف
    icon = models.CharField(max_length=50, blank=True, verbose_name='الأيقونة')  # رمز الأيقونة المستخدم في واجهة المستخدم

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────────────────
# نموذج فرصة التدريب - يمثل فرصة تدريب واحدة مقدمة من شركة
# ──────────────────────────────────────────────────────────
class Internship(models.Model):
    """يمثل فرصة تدريب مقدمة من شركة ما، ويشمل جميع التفاصيل المتعلقة بها مثل الموقع والمتطلبات والتواريخ"""

    # خيارات نوع التدريب (حضوري، عن بُعد، أو مختلط)
    TYPE_CHOICES = [
        ('onsite', 'حضوري'),
        ('remote', 'عن بعد'),
        ('hybrid', 'مختلط'),
    ]

    # خيارات حالة الفرصة (مفتوح للتقديم، مغلق، أو مكتمل)
    STATUS_CHOICES = [
        ('open', 'مفتوح'),
        ('closed', 'مغلق'),
        ('full', 'مكتمل'),
    ]

    id = models.AutoField(primary_key=True)  # المعرف الفريد لفرصة التدريب
    # الشركة المقدمة للفرصة - علاقة один إلى متعدد مع نموذج ملف الشركة
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='internships', verbose_name='الشركة')
    # التصنيف الذي تنتمي إليه الفرصة - يمكن أن يكون فارغاً إذا لم يتم التصنيف
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='internships', verbose_name='التصنيف')
    title = models.CharField(max_length=300, verbose_name='المسمى الوظيفي')  # عنوان الفرصة
    description = models.TextField(verbose_name='الوصف')  # وصف تفصيلي للفرصة
    requirements = models.TextField(blank=True, verbose_name='المتطلبات')  # المهارات والمتطلبات المطلوبة من المتدرب
    deadline = models.DateField(verbose_name='آخر موعد للتقديم')  # تاريخ انتهاء صلاحية التقديم
    available_positions = models.IntegerField(default=1, verbose_name='عدد المقاعد')  # عدد المقاعد المتاحة
    location = models.CharField(max_length=200, verbose_name='الموقع')  # موقع العمل أو المدينة
    # نوع التدريب: حضوري أو عن بُعد أو مختلط
    internship_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='onsite', verbose_name='النوع')
    start_date = models.DateField(verbose_name='تاريخ البدء')  # تاريخ بدء التدريب
    end_date = models.DateField(verbose_name=' تاريخ الانتهاء')  # تاريخ انتهاء التدريب
    # حالة الفرصة: مفتوح، مغلق، أو مكتمل
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='الحالة')
    acceptance_rate = models.FloatField(default=0.0, verbose_name='نسبة القبول')  # نسبة القبول الحسابية
    is_paid = models.BooleanField(default=False, verbose_name='مدفوع')  # هل الفرصة مدفوعة أم تطوعية
    learning_outcomes = models.TextField(blank=True, verbose_name='ما سيتعلمه المتدرب')  # مخرجات التعلم المتوقعة
    additional_skills = models.TextField(blank=True, verbose_name='المهارات الإضافية')  # مهارات إضافية مفضلة لكن ليست إلزامية
    has_certificate = models.BooleanField(default=False, verbose_name='شهادة إتمام')  # هل تصدر شهادة إتمام
    work_days = models.CharField(max_length=50, blank=True, verbose_name='أيام العمل')  # أيام العمل الأسبوعية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ النشر')  # تاريخ نشر الفرصة (يُملأ تلقائياً)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')  # آخر تاريخ تعديل (يُحدّث تلقائياً)

    class Meta:
        verbose_name = 'فرصة تدريب'
        verbose_name_plural = 'فرص التدريب'
        ordering = ['-created_at']  # ترتيب من الأحدث إلى الأقدم

    def __str__(self):
        return f'{self.title} - {self.company.company_name}'

    def update_acceptance_rate(self):
        """تحديث نسبة القبول بناءً على عدد الطلبات المقبولة إلى العدد الكلي للطلبات"""
        total = self.applications.count()  # العدد الكلي لطلبات التقديم
        # عدد الطلبات التي حالتها "مقبول"
        accepted = self.applications.filter(status='accepted').count()
        # حساب النسبة المئوية: (مقبول / الكلي) * 100، أو 0 إذا لا توجد طلبات
        self.acceptance_rate = (accepted / total * 100) if total > 0 else 0
        self.save(update_fields=['acceptance_rate'])


# ──────────────────────────────────────────────────────────
# نموذج الفرصة المحفوظة - يمثل عملية حفظ فرصة من قبل متدرب
# ──────────────────────────────────────────────────────────
class SavedInternship(models.Model):
    """يحفظ المتدرب فرصة تدريب للاستعراض لاحقاً، مع ضمان عدم تكرار الحفظ لنفس الفرصة"""

    id = models.AutoField(primary_key=True)  # المعرف الفريد للسجل
    # المتدرب الذي قام بالحفظ
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='saved_internships', verbose_name='المتدرب')
    # الفرصة التي تم حفظها
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='saved_by', verbose_name='الفرصة')
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الحفظ')  # تاريخ ووقت الحفظ

    class Meta:
        verbose_name = 'فرصة محفوظة'
        verbose_name_plural = 'الفرص المحفوظة'
        unique_together = ['trainee', 'internship']  # ضمان عدم تكرار الحفظ لنفس المتدرب والفرصة

    def __str__(self):
        return f'{self.trainee.person.full_name} حفظ {self.internship.title}'


# ──────────────────────────────────────────────────────────
# نموذج طلب التقديم - يمثل طلب تقديم متدرب على فرصة تدريب
# ──────────────────────────────────────────────────────────
class Application(models.Model):
    """يمثل طلب تقديم متدرب على فرصة تدريب معينة، ويحتوي على حالات مختلفة (معلق، مقبول، مرفوض، مسحوب)"""

    # حالات طلب التقديم
    STATUS_CHOICES = [
        ('pending', 'معلق'),  # لم يتم مراجعته بعد
        ('accepted', 'مقبول'),  # تم قبول المتدرب
        ('rejected', 'مرفوض'),  # تم رفض المتدرب
        ('withdrawn', 'مسحوب'),  # سحب المتدرب طلبه
    ]

    id = models.AutoField(primary_key=True)  # المعرف الفريد للطلب
    # الفرصة التي تم التقديم عليها
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='applications', verbose_name='الفرصة')
    # المتدرب الذي قدم الطلب
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='applications', verbose_name='المتدرب')
    application_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التقديم')  # تاريخ ووقت تقديم الطلب
    # حالة الطلب الحالية
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    resume_version = models.CharField(max_length=500, blank=True, verbose_name='السيرة الذاتية المستخدمة')  # اسم ملف السيرة الذاتية المرفقة
    cover_letter = models.TextField(blank=True, verbose_name='رسالة التقديم')  # رسالة التقديم المرفقة
    rejection_reason = models.TextField(blank=True, verbose_name='سبب الرفض')  # سبب الرفض (يُملأ عند الرفض)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')  # تاريخ إنشاء السجل

    class Meta:
        verbose_name = 'طلب تقديم'
        verbose_name_plural = 'طلبات التقديم'
        unique_together = ['internship', 'trainee']  # ضمان عدم تكرار التقديم من نفس المتدرب على نفس الفرصة
        ordering = ['-application_date']  # ترتيب من الأحدث إلى الأقدم

    def __str__(self):
        return f'{self.trainee.person.full_name} - {self.internship.title} ({self.get_status_display()})'


# ──────────────────────────────────────────────────────────
# نموذج المتدرب المقبول - يمثل متدرباً تم قبوله وتعيينه في قسم
# ──────────────────────────────────────────────────────────
class AcceptedTrainee(models.Model):
    """يُسجل معلومات المتدرب المقبول بعد الموافقة على طلبه، مثل القسم والموعد والمشرف المخصص"""

    id = models.AutoField(primary_key=True)  # المعرف الفريد
    # الطلب المقبول - علاقة واحد إلى واحد مع نموذج طلب التقديم
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='acceptance', verbose_name='الطلب')
    department = models.CharField(max_length=200, verbose_name='القسم')  # القسم الذي سيتدرب فيه المتدرب
    joining_date = models.DateField(verbose_name='تاريخ الالتحاق')  # تاريخ بدء التدريب الفعلي
    # المشرف المخصص على المتدرب - يمكن أن يكون فارغاً مؤقتاً
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_trainees', verbose_name='المشرف')

    class Meta:
        verbose_name = 'متدرب مقبول'
        verbose_name_plural = 'المتدربون المقبولون'

    def __str__(self):
        return f'{self.application.trainee.person.full_name} - مقبول في {self.department}'
