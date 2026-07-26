"""
نماذج قاعدة البيانات للمستخدمين - يحتوي على نموذج المستخدم الرئيسي (Person) والنماذج المرتبطة به
مثل المتدرب، الشركة، المشرف، الأدمن، رموز التحقق، السيرة الذاتية، وسجل المراقبة.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


# ═══════════════════════════════════════════════════════════════════════
# مدير المستخدمين - مسؤول عن إنشاء المستخدمين و超级_admin
# ═══════════════════════════════════════════════════════════════════════

class UserManager(BaseUserManager):
    """مدير المستخدمين المخصص لإنشاء المستخدمين العاديين والمديرين العامين"""

    def create_user(self, email, password=None, **extra_fields):
        """إنشاء مستخدم جديد بالبريد الإلكتروني وكلمة المرور"""
        if not email:
            raise ValueError('البريد الإلكتروني مطلوب')
        # تطبيع البريد الإلكتروني للتأكد من صيغته الصحيحة
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # تشفير كلمة المرور قبل حفظها
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """إنشاء مدير عام (superuser) بصلاحيات كاملة"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# ═══════════════════════════════════════════════════════════════════════
# النموذج الرئيسي للمستخدم (Person) - يمثل جميع المستخدمين في النظام
# ═══════════════════════════════════════════════════════════════════════

class Person(AbstractBaseUser, PermissionsMixin):
    """النموذج الرئيسي للمستخدم - يخزن بيانات الحساب والمصادقة لجميع أنواع المستخدمين"""

    # مجموعات الصلاحيات - تربط المستخدم بمجموعات الصلاحيات
    groups = models.ManyToManyField(
        'auth.Group', verbose_name='المجموعات', blank=True, related_name='trainlink_person_groups'
    )
    # صلاحيات المستخدم الفردية
    user_permissions = models.ManyToManyField(
        'auth.Permission', verbose_name='صلاحيات المستخدم', blank=True, related_name='trainlink_person_permissions'
    )
    # أنواع المستخدمين المتاحة في النظام
    PERSON_TYPE_CHOICES = [
        ('trainee', 'متدرب'),
        ('company', 'شركة'),
        ('supervisor', 'مشرف'),
        ('admin', 'أدمن'),
    ]

    id = models.AutoField(primary_key=True)  # المعرف الأساسي للمستخدم
    # المعرف الفريد للمستخدم - يتم إنشاؤه تلقائياً بناءً على النوع (TR/CO/SV/AD + معرف عشوائي)
    user_id = models.CharField(max_length=20, unique=True, editable=False, verbose_name='المعرف الفريد')
    full_name = models.CharField(max_length=200, verbose_name='الاسم الكامل')  # الاسم الكامل للمستخدم
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')  # البريد الإلكتروني (يُستخدم كاسم مستخدم)
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')  # رقم الهاتف اختياري
    address = models.CharField(max_length=300, blank=True, verbose_name='العنوان')  # العنوان اختياري
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='الصورة الشخصية')  # صورة الملف الشخصي
    person_type = models.CharField(max_length=20, choices=PERSON_TYPE_CHOICES, verbose_name='نوع المستخدم')  # نوع المستخدم
    is_verified = models.BooleanField(default=False, verbose_name='موثق')  # هل تم توثيق الحساب بالبريد الإلكتروني
    is_active = models.BooleanField(default=True, verbose_name='نشط')  # هل الحساب مفعل
    is_staff = models.BooleanField(default=False, verbose_name='موظف')  # هل له صلاحية الدخول للوحة الإدارة
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')  # تاريخ ووقت الإنشاء
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')  # تاريخ آخر تحديث

    objects = UserManager()  # استخدام مدير المستخدمين المخصص
    USERNAME_FIELD = 'email'  # البريد الإلكتروني هو حقل تسجيل الدخول
    REQUIRED_FIELDS = ['full_name']  # الحقول المطلوبة عند الإنشاء

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'

    def __str__(self):
        """تمثيل النصي للمستخدم - يعرض الاسم الكامل مع نوع المستخدم"""
        return f'{self.full_name} ({self.get_person_type_display()})'

    def save(self, *args, **kwargs):
        """حفظ المستخدم مع إنشاء المعرف الفريد تلقائياً إذا لم يكن موجوداً"""
        if not self.user_id:
            # تحديد البادئة حسب نوع المستخدم
            prefix = {'trainee': 'TR', 'company': 'CO', 'supervisor': 'SV', 'admin': 'AD'}
            # إنشاء معرف فريد: البادئة + أول 8 أحرف من UUID عشوائي
            self.user_id = f'{prefix.get(self.person_type, "US")}{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════════════
# نموذج المتدرب - يحتوي على المعلومات الأكاديمية والشخصية للمتدرب
# ═══════════════════════════════════════════════════════════════════════

class Trainee(models.Model):
    """الملف الشخصي للمتدرب - يخزن المعلومات الدراسية والمهنية"""
    GENDER_CHOICES = [('M', 'ذكر'), ('F', 'أنثى')]  # خيارات الجنس

    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='trainee_profile', verbose_name='المستخدم')  # ربط بحساب المستخدم
    university = models.CharField(max_length=200, blank=True, verbose_name='الجامعة')  # الجامعة
    major = models.CharField(max_length=200, blank=True, verbose_name='التخصص')  # التخصص الأكاديمي
    gpa = models.FloatField(default=0.0, verbose_name='المعدل التراكمي')  # المعدل التراكمي
    year_of_study = models.IntegerField(default=1, verbose_name='السنة الدراسية')  # السنة الدراسية الحالية
    is_graduate = models.BooleanField(default=False, verbose_name='خريج')  # هل المتدرب خريج
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='الجنس')  # الجنس
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='تاريخ الميلاد')  # تاريخ الميلاد
    nationality = models.CharField(max_length=100, blank=True, verbose_name='الجنسية')  # الجنسية
    bio = models.TextField(blank=True, verbose_name='نبذة تعريفية')  # نبذة تعريفية شخصية
    skills = models.TextField(blank=True, verbose_name='المهارات')  # المهارات
    location = models.CharField(max_length=200, blank=True, verbose_name='الموقع')  # الموقع الجغرافي
    id_document = models.FileField(upload_to='id_documents/', blank=True, null=True, verbose_name='وثيقة الهوية')  # وثيقة الهوية الشخصية
    # سجل الإشراف - يربط المتدرب بمشرفه الأكاديمي (العلاقة اختيارية)
    assignment = models.ForeignKey('performance.SupervisionAssignment', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_trainees', verbose_name='سجل الإشراف')

    class Meta:
        verbose_name = 'متدرب'
        verbose_name_plural = 'المتدربون'

    def __str__(self):
        """تمثيل النصي للمتدرب - يعرض الاسم والتخصص"""
        return f'{self.person.full_name} - {self.major}'


# ═══════════════════════════════════════════════════════════════════════
# نموذج ملف الشركة - يحتوي على معلومات الشركة والنشاط التجاري
# ═══════════════════════════════════════════════════════════════════════

class CompanyProfile(models.Model):
    """الملف الشخصي للشركة - يخزن معلومات النشاط التجاري والبيانات الأساسية"""
    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='company_profile', verbose_name='المستخدم')  # ربط بحساب المستخدم
    company_name = models.CharField(max_length=200, verbose_name='اسم الشركة')  # اسم الشركة
    commercial_id = models.CharField(max_length=50, blank=True, verbose_name='السجل التجاري')  # رقم السجل التجاري
    industry = models.CharField(max_length=200, blank=True, verbose_name='مجال العمل')  # مجال النشاط التجاري
    location = models.CharField(max_length=200, blank=True, verbose_name='الموقع')  # موقع الشركة
    company_size = models.CharField(max_length=50, blank=True, verbose_name='حجم الشركة')  # حجم الشركة (عدد الموظفين)
    website = models.URLField(blank=True, verbose_name='الموقع الإلكتروني')  # رابط الموقع الإلكتروني
    about = models.TextField(blank=True, verbose_name='نبذة عن الشركة')  # وصف مختصر عن الشركة
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, verbose_name='شعار الشركة')  # شعار الشركة
    is_verified = models.BooleanField(default=False, verbose_name='موثقة')  # هل تم توثيق الشركة

    class Meta:
        verbose_name = 'شركة'
        verbose_name_plural = 'الشركات'

    def __str__(self):
        """تمثيل النصي للشركة - يعرض اسم الشركة"""
        return self.company_name


# ═══════════════════════════════════════════════════════════════════════
# نموذج ملف المشرف - يحتوي على المعلومات المهنية للمشرف الأكاديمي
# ═══════════════════════════════════════════════════════════════════════

class SupervisorProfile(models.Model):
    """الملف الشخصي للمشرف - يخزن معلوماته الجامعية والمهنية"""
    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='supervisor_profile', verbose_name='المستخدم')  # ربط بحساب المستخدم
    university = models.CharField(max_length=200, blank=True, verbose_name='الجامعة')  # الجامعة التابع لها
    department = models.CharField(max_length=200, blank=True, verbose_name='القسم')  # القسم الأكاديمي
    job_title = models.CharField(max_length=200, blank=True, verbose_name='المسمى الوظيفي')  # المسمى الوظيفي
    professional_experience = models.TextField(blank=True, verbose_name='الخبرة العملية')  # الخبرات العملية

    class Meta:
        verbose_name = 'مشرف'
        verbose_name_plural = 'المشرفون'

    def __str__(self):
        """تمثيل النصي للمشرف - يعرض الاسم والقسم"""
        return f'{self.person.full_name} - {self.department}'


# ═══════════════════════════════════════════════════════════════════════
# نموذج ملف الأدمن - يحتوي على دور المستخدم الإداري
# ═══════════════════════════════════════════════════════════════════════

class AdminProfile(models.Model):
    """الملف الشخصي للمدير - يخزن دوره في النظام (مدير عام أو دعم فني)"""
    # الأدوار المتاحة في لوحة الإدارة
    ROLE_CHOICES = [('superadmin', 'مدير عام'), ('support', 'دعم')]

    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='admin_profile', verbose_name='المستخدم')  # ربط بحساب المستخدم
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='support', verbose_name='الدور')  # دور المدير

    class Meta:
        verbose_name = 'أدمن'
        verbose_name_plural = 'الأدمن'

    def __str__(self):
        """تمثيل النصي للأدمن - يعرض الاسم والدور"""
        return f'{self.person.full_name} ({self.get_role_display()})'


# ═══════════════════════════════════════════════════════════════════════
# نموذج رموز التحقق OTP - لتخزين رموز التحقق المؤقتة
# ═══════════════════════════════════════════════════════════════════════

class OTPVerification(models.Model):
    """رمز التحقق أحادي الاستخدام (OTP) - يُستخدم للتحقق من البريد الإلكتروني وإعادة تعيين كلمة المرور"""
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='otps', verbose_name='المستخدم')  # المستخدم صاحب الرمز
    otp_code = models.CharField(max_length=6, verbose_name='رمز التحقق')  # رمز التحقق المكون من 6 أرقام
    purpose = models.CharField(max_length=50, default='registration', verbose_name='الغرض')  # غرض الرمز (تسجيل أو إعادة تعيين كلمة المرور)
    expires_at = models.DateTimeField(verbose_name='تاريخ الانتهاء')  # تاريخ انتهاء صلاحية الرمز
    is_used = models.BooleanField(default=False, verbose_name='مستخدم')  # هل تم استخدام الرمز
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')  # تاريخ إنشاء الرمز

    class Meta:
        verbose_name = 'رمز التحقق'
        verbose_name_plural = 'رموز التحقق'

    def __str__(self):
        """تمثيل النصي لرمز التحقق - يعرض اسم المستخدم والرمز"""
        return f'{self.person.full_name} - {self.otp_code}'


# ═══════════════════════════════════════════════════════════════════════
# نموذج السيرة الذاتية - لتخزين ملفات CV للمتدربين مع التحليل بالذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════

class CV(models.Model):
    """السيرة الذاتية - تخزين ملفات CV المرفوعة مع نتائج التحليل بالذكاء الاصطناعي"""
    id = models.AutoField(primary_key=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='cvs', verbose_name='المتدرب')  # المتدرب صاحب السيرة الذاتية
    file = models.FileField(upload_to='cvs/', verbose_name='ملف السيرة الذاتية')  # ملف السيرة الذاتية المرفوع
    file_path = models.CharField(max_length=500, blank=True, verbose_name='مسار الملف')  # مسار الملف على السيرفر
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')  # تاريخ رفع الملف
    is_primary = models.BooleanField(default=True, verbose_name='النسخة الافتراضية')  # هل هذه النسخة هي الأساسية
    ai_analysis = models.JSONField(null=True, blank=True, verbose_name='تحليل الذكاء الاصطناعي')  # نتائج التحليل بالذكاء الاصطناعي (JSON)
    ai_score = models.FloatField(null=True, blank=True, verbose_name='درجة التحليل')  # درجة التقييم من التحليل

    class Meta:
        verbose_name = 'سيرة ذاتية'
        verbose_name_plural = 'السيرة الذاتية'

    def __str__(self):
        """تمثيل النصي للسيرة الذاتية - يعرض اسم المتدرب"""
        return f'CV - {self.trainee.person.full_name}'


# ═══════════════════════════════════════════════════════════════════════
# نموذج سجل المراقبة (Audit Log) - لتسجيل العمليات والتغييرات في النظام
# ═══════════════════════════════════════════════════════════════════════

class AuditLog(models.Model):
    """سجل المراقبة - يسجل جميع العمليات والتغييرات التي تحدث في قاعدة البيانات"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, verbose_name='المستخدم')  # المستخدم الذي نفذ العملية (يُحذف إذا حُذف الحساب)
    action = models.CharField(max_length=20, verbose_name='الإجراء')  # نوع العملية (إضافة/تعديل/حذف)
    table_name = models.CharField(max_length=100, verbose_name='الجدول')  # اسم الجدول المتأثر
    record_id = models.IntegerField(verbose_name='معرف السجل')  # معرف السجل المتأثر
    details = models.JSONField(null=True, blank=True, verbose_name='التفاصيل')  # تفاصيل إضافية عن العملية
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='الوقت')  # توقيت العملية

    class Meta:
        verbose_name = 'سجل المراقبة'
        verbose_name_plural = 'سجلات المراقبة'

    def __str__(self):
        """تمثيل النصي لسجل المراقبة - يعرض المستخدم والعملية والجدول"""
        return f'{self.user} - {self.action} - {self.table_name}'
