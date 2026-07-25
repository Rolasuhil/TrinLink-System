from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('البريد الإلكتروني مطلوب')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Person(AbstractBaseUser, PermissionsMixin):
    groups = models.ManyToManyField(
        'auth.Group', verbose_name='المجموعات', blank=True, related_name='trainlink_person_groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', verbose_name='صلاحيات المستخدم', blank=True, related_name='trainlink_person_permissions'
    )
    PERSON_TYPE_CHOICES = [
        ('trainee', 'متدرب'),
        ('company', 'شركة'),
        ('supervisor', 'مشرف'),
        ('admin', 'أدمن'),
    ]

    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=20, unique=True, editable=False, verbose_name='المعرف الفريد')
    full_name = models.CharField(max_length=200, verbose_name='الاسم الكامل')
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    address = models.CharField(max_length=300, blank=True, verbose_name='العنوان')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='الصورة الشخصية')
    person_type = models.CharField(max_length=20, choices=PERSON_TYPE_CHOICES, verbose_name='نوع المستخدم')
    is_verified = models.BooleanField(default=False, verbose_name='موثق')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    is_staff = models.BooleanField(default=False, verbose_name='موظف')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'

    def __str__(self):
        return f'{self.full_name} ({self.get_person_type_display()})'

    def save(self, *args, **kwargs):
        if not self.user_id:
            prefix = {'trainee': 'TR', 'company': 'CO', 'supervisor': 'SV', 'admin': 'AD'}
            self.user_id = f'{prefix.get(self.person_type, "US")}{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)


class Trainee(models.Model):
    GENDER_CHOICES = [('M', 'ذكر'), ('F', 'أنثى')]

    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='trainee_profile', verbose_name='المستخدم')
    university = models.CharField(max_length=200, blank=True, verbose_name='الجامعة')
    major = models.CharField(max_length=200, blank=True, verbose_name='التخصص')
    gpa = models.FloatField(default=0.0, verbose_name='المعدل التراكمي')
    year_of_study = models.IntegerField(default=1, verbose_name='السنة الدراسية')
    is_graduate = models.BooleanField(default=False, verbose_name='خريج')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='الجنس')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='تاريخ الميلاد')
    nationality = models.CharField(max_length=100, blank=True, verbose_name='الجنسية')
    bio = models.TextField(blank=True, verbose_name='نبذة تعريفية')
    assignment = models.ForeignKey('performance.SupervisionAssignment', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_trainees', verbose_name='سجل الإشراف')

    class Meta:
        verbose_name = 'متدرب'
        verbose_name_plural = 'المتدربون'

    def __str__(self):
        return f'{self.person.full_name} - {self.major}'


class CompanyProfile(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='company_profile', verbose_name='المستخدم')
    company_name = models.CharField(max_length=200, verbose_name='اسم الشركة')
    commercial_id = models.CharField(max_length=50, blank=True, verbose_name='السجل التجاري')
    industry = models.CharField(max_length=200, blank=True, verbose_name='مجال العمل')
    location = models.CharField(max_length=200, blank=True, verbose_name='الموقع')
    website = models.URLField(blank=True, verbose_name='الموقع الإلكتروني')
    about = models.TextField(blank=True, verbose_name='نبذة عن الشركة')
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, verbose_name='شعار الشركة')
    is_verified = models.BooleanField(default=False, verbose_name='موثقة')

    class Meta:
        verbose_name = 'شركة'
        verbose_name_plural = 'الشركات'

    def __str__(self):
        return self.company_name


class SupervisorProfile(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='supervisor_profile', verbose_name='المستخدم')
    department = models.CharField(max_length=200, blank=True, verbose_name='القسم')
    job_title = models.CharField(max_length=200, blank=True, verbose_name='المسمى الوظيفي')
    professional_experience = models.TextField(blank=True, verbose_name='الخبرة العملية')

    class Meta:
        verbose_name = 'مشرف'
        verbose_name_plural = 'المشرفون'

    def __str__(self):
        return f'{self.person.full_name} - {self.department}'


class AdminProfile(models.Model):
    ROLE_CHOICES = [('superadmin', 'مدير عام'), ('support', 'دعم')]

    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='admin_profile', verbose_name='المستخدم')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='support', verbose_name='الدور')

    class Meta:
        verbose_name = 'أدمن'
        verbose_name_plural = 'الأدمن'

    def __str__(self):
        return f'{self.person.full_name} ({self.get_role_display()})'


class OTPVerification(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='otps', verbose_name='المستخدم')
    otp_code = models.CharField(max_length=6, verbose_name='رمز التحقق')
    purpose = models.CharField(max_length=50, default='registration', verbose_name='الغرض')
    expires_at = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    is_used = models.BooleanField(default=False, verbose_name='مستخدم')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'رمز التحقق'
        verbose_name_plural = 'رموز التحقق'

    def __str__(self):
        return f'{self.person.full_name} - {self.otp_code}'


class CV(models.Model):
    id = models.AutoField(primary_key=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='cvs', verbose_name='المتدرب')
    file = models.FileField(upload_to='cvs/', verbose_name='ملف السيرة الذاتية')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='مسار الملف')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')
    is_primary = models.BooleanField(default=True, verbose_name='النسخة الافتراضية')
    ai_analysis = models.JSONField(null=True, blank=True, verbose_name='تحليل الذكاء الاصطناعي')
    ai_score = models.FloatField(null=True, blank=True, verbose_name='درجة التحليل')

    class Meta:
        verbose_name = 'سيرة ذاتية'
        verbose_name_plural = 'السيرة الذاتية'

    def __str__(self):
        return f'CV - {self.trainee.person.full_name}'


class AuditLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, verbose_name='المستخدم')
    action = models.CharField(max_length=20, verbose_name='الإجراء')
    table_name = models.CharField(max_length=100, verbose_name='الجدول')
    record_id = models.IntegerField(verbose_name='معرف السجل')
    details = models.JSONField(null=True, blank=True, verbose_name='التفاصيل')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='الوقت')

    class Meta:
        verbose_name = 'سجل المراقبة'
        verbose_name_plural = 'سجلات المراقبة'

    def __str__(self):
        return f'{self.user} - {self.action} - {self.table_name}'
