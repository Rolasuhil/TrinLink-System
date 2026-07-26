"""
serializers لتحويل البيانات - يحتوي على جميع الـ serializers لتحويل بيانات JSON
إلى كائنات نماذج Django والعكس، بما في ذلك تسجيل الدخول والتسجيل والتحقق وإدارة كلمة المرور.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Person, Trainee, CompanyProfile, SupervisorProfile, AdminProfile, OTPVerification
import bcrypt
import jwt
import random
import string
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════════════
# serializers تسجيل الدخول - للتحقق من بيانات المستخدم عند تسجيل الدخول
# ═══════════════════════════════════════════════════════════════════════

class LoginSerializer(serializers.Serializer):
    """serializers تسجيل الدخول - يتحقق من صحة البريد الإلكتروني وكلمة المرور ونوع الحساب"""

    email = serializers.EmailField()  # البريد الإلكتروني للمستخدم
    password = serializers.CharField()  # كلمة المرور
    user_type = serializers.ChoiceField(choices=Person.PERSON_TYPE_CHOICES)  # نوع المستخدم المطلوب

    def validate(self, data):
        """التحقق من صحة بيانات تسجيل الدخول"""

        # التحقق من وجود المستخدم بالبريد الإلكتروني
        try:
            person = Person.objects.get(email=data['email'])
        except Person.DoesNotExist:
            raise serializers.ValidationError('البريد الإلكتروني غير مسجل')

        # التحقق من صحة كلمة المرور باستخدام bcrypt
        if not person.check_password(data['password']):
            raise serializers.ValidationError('كلمة المرور غير صحيحة')

        # التحقق من أن الحساب مفعل
        if not person.is_active:
            raise serializers.ValidationError('الحساب معطل')

        # التحقق من تطابق نوع الحساب مع النوع المحدد
        if person.person_type != data['user_type']:
            raise serializers.ValidationError('نوع الحساب غير مطابق')

        # إرفاق كائن المستخدم بالبيانات المُ validated
        data['user'] = person
        return data


# ═══════════════════════════════════════════════════════════════════════
# serializers تسجيل المتدرب - لإنشاء حساب متدرب جديد
# ═══════════════════════════════════════════════════════════════════════

class RegisterTraineeSerializer(serializers.Serializer):
    """serializers تسجيل المتدرب - يجمع بيانات التسجيل وينشئ حساب المتدرب مع ملفه الشخصي"""

    full_name = serializers.CharField(max_length=200)  # الاسم الكامل
    email = serializers.EmailField()  # البريد الإلكتروني
    password = serializers.CharField(min_length=8)  # كلمة المرور (8 أحرف على الأقل)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)  # رقم الهاتف (اختياري)
    address = serializers.CharField(max_length=300, required=False, allow_blank=True)  # العنوان (اختياري)
    university = serializers.CharField(max_length=200, required=False, allow_blank=True)  # الجامعة (اختياري)
    major = serializers.CharField(max_length=200, required=False, allow_blank=True)  # التخصص (اختياري)
    gpa = serializers.FloatField(required=False)  # المعدل التراكمي (اختياري)
    year_of_study = serializers.IntegerField(required=False)  # السنة الدراسية (اختياري)
    is_graduate = serializers.BooleanField(required=False)  # هل هو خريج (اختياري)
    gender = serializers.ChoiceField(choices=Trainee.GENDER_CHOICES, required=False)  # الجنس (اختياري)
    date_of_birth = serializers.DateField(required=False)  # تاريخ الميلاد (اختياري)
    skills = serializers.CharField(required=False, allow_blank=True)  # المهارات (اختياري)
    supervisor_id = serializers.CharField(max_length=20, required=False, allow_blank=True)  # معرف المشرف (اختياري)

    def validate_email(self, value):
        """التأكد من أن البريد الإلكتروني غير مسجل مسبقاً"""
        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError('البريد الإلكتروني مسجل مسبقاً')
        return value

    def create(self, validated_data):
        """إنشاء حساب المتدرب وملفه الشخصي مع رمز التحقق"""

        # استخراج معرف المشرف إن وُجد
        supervisor_id = validated_data.pop('supervisor_id', None)

        # إنشاء حساب المستخدم الأساسي
        person = Person(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            person_type='trainee',
        )
        person.set_password(validated_data['password'])  # تشفير كلمة المرور
        person.save()

        # إنشاء ملف المتدرب الشخصي
        trainee = Trainee.objects.create(
            person=person,
            university=validated_data.get('university', ''),
            major=validated_data.get('major', ''),
            gpa=validated_data.get('gpa', 0.0),
            year_of_study=validated_data.get('year_of_study', 1),
            is_graduate=validated_data.get('is_graduate', False),
            gender=validated_data.get('gender', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            skills=validated_data.get('skills', ''),
        )

        # ربط المتدرب بمشرفه إذا تم تحديد معرف المشرف
        if supervisor_id:
            try:
                from performance.models import SupervisionAssignment
                # استخراج معرف المشرف من السلسلة (إزالة البادئة SUP-)
                sid = int(supervisor_id.replace('SUP-', '').lstrip('0') or '0')
                supervisor = SupervisorProfile.objects.get(id=sid)
                # إنشاء سجل الإشراف
                SupervisionAssignment.objects.create(
                    supervisor=supervisor,
                    trainee=trainee,
                    role='academic',
                    status='active',
                )
            except (SupervisorProfile.DoesNotExist, ValueError):
                pass  # تجاهل الخطأ إذا لم يُعثر على المشرف

        # إنشاء رمز التحقق المؤقت (OTP) لتأكيد البريد الإلكتروني
        OTPVerification.objects.create(
            person=person,
            otp_code=''.join(random.choices(string.digits, k=6)),  # رمز عشوائي من 6 أرقام
            purpose='registration',  # الغرض: التحقق من التسجيل
            expires_at=datetime.now() + timedelta(minutes=15),  # صالح لمدة 15 دقيقة
        )

        return person


# ═══════════════════════════════════════════════════════════════════════
# serializers تسجيل الشركة - لإنشاء حساب شركة جديد
# ═══════════════════════════════════════════════════════════════════════

class RegisterCompanySerializer(serializers.Serializer):
    """serializers تسجيل الشركة - يجمع بيانات الشركة وينشئ حسابها مع ملفها الشخصي"""

    company_name = serializers.CharField(max_length=200)  # اسم الشركة
    email = serializers.EmailField()  # البريد الإلكتروني
    password = serializers.CharField(min_length=8)  # كلمة المرور
    phone_number = serializers.CharField(max_length=20, required=False)  # رقم الهاتف (اختياري)
    industry = serializers.CharField(max_length=200, required=False)  # مجال العمل (اختياري)
    company_size = serializers.CharField(max_length=50, required=False)  # حجم الشركة (اختياري)
    location = serializers.CharField(max_length=200, required=False)  # الموقع (اختياري)
    website = serializers.URLField(required=False)  # الموقع الإلكتروني (اختياري)
    description = serializers.CharField(required=False)  # وصف الشركة (اختياري)

    def validate_email(self, value):
        """التأكد من عدم تكرار البريد الإلكتروني"""
        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError('البريد الإلكتروني مسجل مسبقاً')
        return value

    def create(self, validated_data):
        """إنشاء حساب الشركة وملفها الشخصي مع رمز التحقق"""

        company_name = validated_data['company_name']

        # إنشاء حساب المستخدم بنوع شركة
        person = Person(
            full_name=company_name,  # اسم المستخدم = اسم الشركة
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            person_type='company',
            is_verified=False,  # الشركة غير موثقة حتى تؤكد بريدها
        )
        person.set_password(validated_data['password'])
        person.save()

        # إنشاء ملف الشركة الشخصي
        CompanyProfile.objects.create(
            person=person,
            company_name=company_name,
            industry=validated_data.get('industry', ''),
            location=validated_data.get('location', ''),
            company_size=validated_data.get('company_size', ''),
            website=validated_data.get('website', ''),
            about=validated_data.get('description', ''),
        )

        # إنشاء رمز التحقق لتأكيد البريد الإلكتروني
        OTPVerification.objects.create(
            person=person,
            otp_code=''.join(random.choices(string.digits, k=6)),
            purpose='registration',
            expires_at=datetime.now() + timedelta(minutes=15),
        )

        return person


# ═══════════════════════════════════════════════════════════════════════
# serializers تسجيل المشرف - لإنشاء حساب مشرف أكاديمي جديد
# ═══════════════════════════════════════════════════════════════════════

class RegisterSupervisorSerializer(serializers.Serializer):
    """serializers تسجيل المشرف - يجمع بيانات المشرف وينشئ حسابه مع ملفه الشخصي"""

    full_name = serializers.CharField(max_length=200)  # الاسم الكامل
    email = serializers.EmailField()  # البريد الإلكتروني
    password = serializers.CharField(min_length=8)  # كلمة المرور
    phone_number = serializers.CharField(max_length=20, required=False)  # رقم الهاتف (اختياري)
    university = serializers.CharField(max_length=200, required=False)  # الجامعة (اختياري)
    department = serializers.CharField(max_length=200, required=False)  # القسم (اختياري)
    specialization = serializers.CharField(max_length=200, required=False)  # التخصص (اختياري)

    def validate_email(self, value):
        """التأكد من عدم تكرار البريد الإلكتروني"""
        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError('البريد الإلكتروني مسجل مسبقاً')
        return value

    def create(self, validated_data):
        """إنشاء حساب المشرف وملفه الشخصي مع رمز التحقق"""

        # إنشاء حساب المستخدم بنوع مشرف
        person = Person(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            person_type='supervisor',
        )
        person.set_password(validated_data['password'])
        person.save()

        # إنشاء ملف المشرف الشخصي
        SupervisorProfile.objects.create(
            person=person,
            university=validated_data.get('university', ''),
            department=validated_data.get('department', ''),
            job_title=validated_data.get('specialization', ''),  # التخصص يُخزن كمسمى وظيفي
        )

        # إنشاء رمز التحقق لتأكيد البريد الإلكتروني
        OTPVerification.objects.create(
            person=person,
            otp_code=''.join(random.choices(string.digits, k=6)),
            purpose='registration',
            expires_at=datetime.now() + timedelta(minutes=15),
        )

        return person


# ═══════════════════════════════════════════════════════════════════════
# serializers التحقق من OTP - للتحقق من رمز التأكيد المرسل بالبريد
# ═══════════════════════════════════════════════════════════════════════

class OTPVerifySerializer(serializers.Serializer):
    """serializers التحقق من رمز OTP - يتحقق من صحة الرمز وصلاحيته"""

    email = serializers.EmailField()  # البريد الإلكتروني للمستخدم
    otp_code = serializers.CharField(max_length=6)  # رمز التحقق المكون من 6 أرقام

    def validate(self, data):
        """التحقق من صحة الرمز ومشاركته مع المستخدم"""

        # البحث عن المستخدم بالبريد الإلكتروني
        try:
            person = Person.objects.get(email=data['email'])
        except Person.DoesNotExist:
            raise serializers.ValidationError('البريد الإلكتروني غير مسجل')

        # البحث عن رمز التحقق غير المستخدم وغير منتهي الصلاحية
        otp = OTPVerification.objects.filter(
            person=person,
            otp_code=data['otp_code'],
            purpose='registration',
            is_used=False,
            expires_at__gt=datetime.now()  # الرمز لم تنتهي صلاحيته بعد
        ).first()

        if not otp:
            raise serializers.ValidationError('رمز التحقق غير صحيح أو منتهي الصلاحية')

        # إرفاق كائن المستخدم ورمز التحقق بالبيانات
        data['person'] = person
        data['otp'] = otp
        return data


# ═══════════════════════════════════════════════════════════════════════
# serializers طلب إعادة تعيين كلمة المرور - لإرسال رمز التأكيد
# ═══════════════════════════════════════════════════════════════════════

class ResetPasswordSerializer(serializers.Serializer):
    """serializers طلب إعادة تعيين كلمة المرور - يتحقق من وجود البريد الإلكتروني"""

    email = serializers.EmailField()  # البريد الإلكتروني للمستخدم

    def validate_email(self, value):
        """التأكد من أن البريد الإلكتروني مسجل في النظام"""
        try:
            Person.objects.get(email=value)
        except Person.DoesNotExist:
            raise serializers.ValidationError('البريد الإلكتروني غير مسجل')
        return value


# ═══════════════════════════════════════════════════════════════════════
# serializers تأكيد إعادة تعيين كلمة المرور - لتطبيق كلمة المرور الجديدة
# ═══════════════════════════════════════════════════════════════════════

class ResetPasswordConfirmSerializer(serializers.Serializer):
    """serializers تأكيد إعادة تعيين كلمة المرور - يتحقق من OTP ويُعيّن كلمة المرور الجديدة"""

    email = serializers.EmailField()  # البريد الإلكتروني
    otp_code = serializers.CharField(max_length=6)  # رمز التحقق
    new_password = serializers.CharField(min_length=8)  # كلمة المرور الجديدة
    confirm_password = serializers.CharField(min_length=8)  # تأكيد كلمة المرور الجديدة

    def validate(self, data):
        """التحقق من تطابق كلمتي المرور وصحة رمز OTP"""

        # التحقق من تطابق كلمة المرور الجديدة مع التأكيد
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('كلمتا المرور غير متطابقتين')

        # البحث عن المستخدم
        try:
            person = Person.objects.get(email=data['email'])
        except Person.DoesNotExist:
            raise serializers.ValidationError('البريد الإلكتروني غير مسجل')

        # البحث عن رمز إعادة تعيين كلمة المرور غير المستخدم
        otp = OTPVerification.objects.filter(
            person=person,
            otp_code=data['otp_code'],
            purpose='password_reset',
            is_used=False,
            expires_at__gt=datetime.now()
        ).first()

        if not otp:
            raise serializers.ValidationError('رمز التحقق غير صحيح')

        # إرفاق كائن المستخدم ورمز التحقق بالبيانات
        data['person'] = person
        data['otp'] = otp
        return data


# ═══════════════════════════════════════════════════════════════════════
# serializers بيانات المستخدم - لتحويل بيانات المستخدم للعرض في API
# ═══════════════════════════════════════════════════════════════════════

class PersonSerializer(serializers.ModelSerializer):
    """serializers عرض بيانات المستخدم - يجمع بيانات الحساب مع ملفه الشخصي حسب نوعه"""

    # حقول محسوبة (computed) - يتم جلبها من الملف الشخصي المناسب لكل نوع مستخدم
    trainee_id = serializers.SerializerMethodField()  # معرف المتدرب
    company_id = serializers.SerializerMethodField()  # معرف الشركة
    supervisor_id = serializers.SerializerMethodField()  # معرف المشرف
    company_name = serializers.SerializerMethodField()  # اسم الشركة
    skills = serializers.SerializerMethodField()  # مهارات المتدرب
    university = serializers.SerializerMethodField()  # الجامعة (للمتدرب أو المشرف)
    major = serializers.SerializerMethodField()  # التخصص
    gpa = serializers.SerializerMethodField()  # المعدل التراكمي
    year_of_study = serializers.SerializerMethodField()  # السنة الدراسية
    is_graduate = serializers.SerializerMethodField()  # هل خريج
    industry = serializers.SerializerMethodField()  # مجال عمل الشركة
    company_size = serializers.SerializerMethodField()  # حجم الشركة
    department = serializers.SerializerMethodField()  # القسم (للمشرف)
    about = serializers.SerializerMethodField()  # نبذة عن الشركة
    website = serializers.SerializerMethodField()  # موقع الشركة الإلكتروني
    location = serializers.SerializerMethodField()  # الموقع الجغرافي

    class Meta:
        model = Person
        # جميع الحقول المرسلة للواجهة الأمامية
        fields = ['id', 'user_id', 'full_name', 'email', 'phone_number', 'address',
                  'profile_picture', 'person_type', 'is_verified', 'created_at',
                  'trainee_id', 'company_id', 'supervisor_id', 'company_name',
                  'skills', 'university', 'major', 'gpa', 'year_of_study', 'is_graduate',
                  'industry', 'company_size', 'department', 'about', 'website', 'location']
        read_only_fields = ['id', 'user_id', 'person_type', 'is_verified', 'created_at']  # حقول للقراءة فقط

    def get_trainee_id(self, obj):
        """جلب معرف المتدرب من ملفه الشخصي (إذا كان متدرباً)"""
        try: return obj.trainee_profile.id
        except Exception: return None

    def get_company_id(self, obj):
        """جلب معرف الشركة من ملفها الشخصي (إذا كانت شركة)"""
        try: return obj.company_profile.id
        except Exception: return None

    def get_supervisor_id(self, obj):
        """جلب معرف المشرف من ملفه الشخصي (إذا كان مشرفاً)"""
        try: return obj.supervisor_profile.id
        except Exception: return None

    def get_company_name(self, obj):
        """جلب اسم الشركة من ملفها الشخصي"""
        try: return obj.company_profile.company_name
        except Exception: return None

    def get_skills(self, obj):
        """جلب مهارات المتدرب من ملفه الشخصي"""
        try: return obj.trainee_profile.skills
        except Exception: return None

    def get_university(self, obj):
        """جلب الجامعة - من ملف المتدرب إذا كان متدرباً، أو من ملف المشرف إذا كان مشرفاً"""
        try:
            if obj.person_type == 'trainee':
                return obj.trainee_profile.university
            elif obj.person_type == 'supervisor':
                return obj.supervisor_profile.university
        except Exception: pass
        return None

    def get_major(self, obj):
        """جلب التخصص الأكاديمي من ملف المتدرب"""
        try: return obj.trainee_profile.major
        except Exception: return None

    def get_gpa(self, obj):
        """جلب المعدل التراكمي من ملف المتدرب"""
        try: return obj.trainee_profile.gpa
        except Exception: return None

    def get_year_of_study(self, obj):
        """جلب السنة الدراسية من ملف المتدرب"""
        try: return obj.trainee_profile.year_of_study
        except Exception: return None

    def get_is_graduate(self, obj):
        """جلب حالة التخرج من ملف المتدرب"""
        try: return obj.trainee_profile.is_graduate
        except Exception: return None

    def get_industry(self, obj):
        """جلب مجال عمل الشركة من ملفها الشخصي"""
        try: return obj.company_profile.industry
        except Exception: return None

    def get_company_size(self, obj):
        """جلب حجم الشركة من ملفها الشخصي"""
        try: return obj.company_profile.company_size
        except Exception: return None

    def get_department(self, obj):
        """جلب القسم الأكاديمي من ملف المشرف"""
        try: return obj.supervisor_profile.department
        except Exception: return None

    def get_about(self, obj):
        """جلب نبذة عن الشركة من ملفها الشخصي"""
        try: return obj.company_profile.about
        except Exception: return None

    def get_website(self, obj):
        """جلب رابط الموقع الإلكتروني للشركة من ملفها الشخصي"""
        try: return obj.company_profile.website
        except Exception: return None

    def get_location(self, obj):
        """جلب الموقع الجغرافي - من ملف الشركة إذا كانت شركة، أو من ملف المتدرب إذا كان متدرباً"""
        try:
            if obj.person_type == 'company':
                return obj.company_profile.location
        except Exception: pass
        try:
            if obj.person_type == 'trainee':
                return obj.trainee_profile.location
        except Exception: pass
        return None
