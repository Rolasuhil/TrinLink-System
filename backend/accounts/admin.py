from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Person, Trainee, CompanyProfile, SupervisorProfile, AdminProfile, OTPVerification, CV


@admin.register(Person)
class PersonAdmin(UserAdmin):
    model = Person
    list_display = ['user_id', 'full_name', 'email', 'person_type', 'is_verified', 'is_active', 'created_at']
    list_filter = ['person_type', 'is_verified', 'is_active']
    search_fields = ['full_name', 'email', 'user_id']
    ordering = ['-created_at']

    fieldsets = (
        ('المعلومات الأساسية', {'fields': ('email', 'password', 'full_name', 'user_id')}),
        ('معلومات التواصل', {'fields': ('phone_number', 'address', 'profile_picture')}),
        ('نوع المستخدم', {'fields': ('person_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('الصلاحيات', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        ('إنشاء مستخدم جديد', {
            'fields': ('email', 'full_name', 'password1', 'password2', 'person_type'),
        }),
    )

    readonly_fields = ['user_id', 'created_at', 'updated_at']


@admin.register(Trainee)
class TraineeAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'university', 'major', 'gpa', 'year_of_study', 'is_graduate']
    search_fields = ['person__full_name', 'university', 'major']
    list_filter = ['is_graduate', 'university']

    def get_name(self, obj):
        return obj.person.full_name
    get_name.short_description = 'الاسم'


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'industry', 'location', 'is_verified']
    list_filter = ['is_verified', 'industry']
    search_fields = ['company_name', 'person__full_name']


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'department', 'job_title']
    search_fields = ['person__full_name', 'department']

    def get_name(self, obj):
        return obj.person.full_name
    get_name.short_description = 'الاسم'


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'role']

    def get_name(self, obj):
        return obj.person.full_name
    get_name.short_description = 'الاسم'


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['person', 'otp_code', 'purpose', 'is_used', 'expires_at']
    list_filter = ['purpose', 'is_used']


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'upload_date', 'is_primary', 'ai_score']
    list_filter = ['is_primary']
