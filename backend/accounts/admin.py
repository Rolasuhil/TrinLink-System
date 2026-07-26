"""
تسجيل النماذج في لوحة إدارة Django - يحتوي على تسجيل جميع نماذج accounts
في لوحة الإدارة مع تخصيص العرض والبحث والفلاتر لتسهيل إدارة البيانات.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Person, Trainee, CompanyProfile, SupervisorProfile, AdminProfile, OTPVerification, CV


# ═══════════════════════════════════════════════════════════════════════
# إدارة نموذج المستخدم (Person) في لوحة الإدارة
# ═══════════════════════════════════════════════════════════════════════

@admin.register(Person)
class PersonAdmin(UserAdmin):
    """تكوين عرض نموذج المستخدم في لوحة الإدارة مع الحقول والفلاتر"""

    model = Person

    # الأعمدة المعروضة في قائمة المستخدمين
    list_display = ['user_id', 'full_name', 'email', 'person_type', 'is_verified', 'is_active', 'created_at']

    # الفلاتر الجانبية لتصنيف المستخدمين
    list_filter = ['person_type', 'is_verified', 'is_active']

    # حقول البحث السريع
    search_fields = ['full_name', 'email', 'user_id']

    # ترتيب المستخدمين حسب تاريخ الإنشاء (الأحدث أولاً)
    ordering = ['-created_at']

    # تقسيم الحقول إلى مجموعات منظمة في صفحة تعديل المستخدم
    fieldsets = (
        ('المعلومات الأساسية', {'fields': ('email', 'password', 'full_name', 'user_id')}),  # بيانات الحساب الأساسية
        ('معلومات التواصل', {'fields': ('phone_number', 'address', 'profile_picture')}),  # بيانات الاتصال
        ('نوع المستخدم', {'fields': ('person_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),  # النوع والحالة
        ('الصلاحيات', {'fields': ('groups', 'user_permissions')}),  # مجموعات وصلاحيات المستخدم
    )

    # حقول إنشاء مستخدم جديد من لوحة الإدارة
    add_fieldsets = (
        ('إنشاء مستخدم جديد', {
            'fields': ('email', 'full_name', 'password1', 'password2', 'person_type'),
        }),
    )

    # الحقول للقراءة فقط (لا يمكن تعديلها من لوحة الإدارة)
    readonly_fields = ['user_id', 'created_at', 'updated_at']


# ═══════════════════════════════════════════════════════════════════════
# إدارة نموذج المتدرب في لوحة الإدارة
# ═══════════════════════════════════════════════════════════════════════

@admin.register(Trainee)
class TraineeAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج المتدرب في لوحة الإدارة"""

    # الأعمدة المعروضة في قائمة المتدربين
    list_display = ['id', 'get_name', 'university', 'major', 'gpa', 'year_of_study', 'is_graduate']

    # حقول البحث السريع (يشمل اسم المستخدم المرتبط)
    search_fields = ['person__full_name', 'university', 'major']

    # الفلاتر الجانبية
    list_filter = ['is_graduate', 'university']

    def get_name(self, obj):
        """جلب اسم المتدرب من نموذج Person المرتبط"""
        return obj.person.full_name
    get_name.short_description = 'الاسم'  # عنوان العمود في لوحة الإدارة


# ═══════════════════════════════════════════════════════════════════════
# إدارة نموذج الشركة في لوحة الإدارة
# ═══════════════════════════════════════════════════════════════════════

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج الشركة في لوحة الإدارة"""

    # الأعمدة المعروضة
    list_display = ['company_name', 'industry', 'location', 'is_verified']

    # الفلاتر الجانبية
    list_filter = ['is_verified', 'industry']

    # حقول البحث (يشمل اسم المستخدم المرتبط)
    search_fields = ['company_name', 'person__full_name']


# ═══════════════════════════════════════════════════════════════════════
# إدارة نموذج المشرف في لوحة الإدارة
# ═══════════════════════════════════════════════════════════════════════

@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج المشرف في لوحة الإدارة"""

    # الأعمدة المعروضة
    list_display = ['get_name', 'department', 'job_title']

    # حقول البحث
    search_fields = ['person__full_name', 'department']

    def get_name(self, obj):
        """جلب اسم المشرف من نموذج Person المرتبط"""
        return obj.person.full_name
    get_name.short_description = 'الاسم'


# ═══════════════════════════════════════════════════════════════════════
# إدارة نموذج الأدمن في لوحة الإدارة
# ═══════════════════════════════════════════════════════════════════════

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    """تكوين عرض نموذج الأدمن في لوحة الإدارة"""

    # الأعمدة المعروضة
    list_display = ['get_name', 'role']

    def get_name(self, obj):
        """جلب اسم الأدمن من نموذج Person المرتبط"""
        return obj.person.full_name
    get_name.short_description = 'الاسم'


# ═══════════════════════════════════════════════════════════════════════
# إدارة نموذج رموز التحقق OTP في لوحة الإدارة
# ═══════════════════════════════════════════════════════════════════════

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    """تكوين عرض رموز التحقق في لوحة الإدارة"""

    # الأعمدة المعروضة
    list_display = ['person', 'otp_code', 'purpose', 'is_used', 'expires_at']

    # الفلاتر الجانبية حسب الغرض وحالة الاستخدام
    list_filter = ['purpose', 'is_used']


# ═══════════════════════════════════════════════════════════════════════
# إدارة نموذج السيرة الذاتية CV في لوحة الإدارة
# ═══════════════════════════════════════════════════════════════════════

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    """تكوين عرض السير الذاتية في لوحة الإدارة"""

    # الأعمدة المعروضة
    list_display = ['trainee', 'upload_date', 'is_primary', 'ai_score']

    # الفلاتر الجانبية حسب النسخة الأساسية
    list_filter = ['is_primary']
