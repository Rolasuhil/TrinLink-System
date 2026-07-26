from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Person, Trainee, CompanyProfile, SupervisorProfile, AdminProfile, OTPVerification
import bcrypt
import jwt
import random
import string
from datetime import datetime, timedelta


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    user_type = serializers.ChoiceField(choices=Person.PERSON_TYPE_CHOICES)

    def validate(self, data):
        try:
            person = Person.objects.get(email=data['email'])
        except Person.DoesNotExist:
            raise serializers.ValidationError('البريد الإلكتروني غير مسجل')

        if not person.check_password(data['password']):
            raise serializers.ValidationError('كلمة المرور غير صحيحة')

        if not person.is_active:
            raise serializers.ValidationError('الحساب معطل')

        if person.person_type != data['user_type']:
            raise serializers.ValidationError('نوع الحساب غير مطابق')

        data['user'] = person
        return data


class RegisterTraineeSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(max_length=300, required=False, allow_blank=True)
    university = serializers.CharField(max_length=200, required=False, allow_blank=True)
    major = serializers.CharField(max_length=200, required=False, allow_blank=True)
    gpa = serializers.FloatField(required=False)
    year_of_study = serializers.IntegerField(required=False)
    is_graduate = serializers.BooleanField(required=False)
    gender = serializers.ChoiceField(choices=Trainee.GENDER_CHOICES, required=False)
    date_of_birth = serializers.DateField(required=False)
    skills = serializers.CharField(required=False, allow_blank=True)
    supervisor_id = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError('البريد الإلكتروني مسجل مسبقاً')
        return value

    def create(self, validated_data):
        supervisor_id = validated_data.pop('supervisor_id', None)

        person = Person(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            person_type='trainee',
        )
        person.set_password(validated_data['password'])
        person.save()

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

        if supervisor_id:
            try:
                from performance.models import SupervisionAssignment
                sid = int(supervisor_id.replace('SUP-', '').lstrip('0') or '0')
                supervisor = SupervisorProfile.objects.get(id=sid)
                SupervisionAssignment.objects.create(
                    supervisor=supervisor,
                    trainee=trainee,
                    role='academic',
                    status='active',
                )
            except (SupervisorProfile.DoesNotExist, ValueError):
                pass

        OTPVerification.objects.create(
            person=person,
            otp_code=''.join(random.choices(string.digits, k=6)),
            purpose='registration',
            expires_at=datetime.now() + timedelta(minutes=15),
        )

        return person


class RegisterCompanySerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    phone_number = serializers.CharField(max_length=20, required=False)
    industry = serializers.CharField(max_length=200, required=False)
    company_size = serializers.CharField(max_length=50, required=False)
    location = serializers.CharField(max_length=200, required=False)
    website = serializers.URLField(required=False)
    description = serializers.CharField(required=False)

    def validate_email(self, value):
        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError('البريد الإلكتروني مسجل مسبقاً')
        return value

    def create(self, validated_data):
        company_name = validated_data['company_name']
        person = Person(
            full_name=company_name,
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            person_type='company',
            is_verified=False,
        )
        person.set_password(validated_data['password'])
        person.save()

        CompanyProfile.objects.create(
            person=person,
            company_name=company_name,
            industry=validated_data.get('industry', ''),
            location=validated_data.get('location', ''),
            company_size=validated_data.get('company_size', ''),
            website=validated_data.get('website', ''),
            about=validated_data.get('description', ''),
        )

        OTPVerification.objects.create(
            person=person,
            otp_code=''.join(random.choices(string.digits, k=6)),
            purpose='registration',
            expires_at=datetime.now() + timedelta(minutes=15),
        )

        return person


class RegisterSupervisorSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    phone_number = serializers.CharField(max_length=20, required=False)
    university = serializers.CharField(max_length=200, required=False)
    department = serializers.CharField(max_length=200, required=False)
    specialization = serializers.CharField(max_length=200, required=False)

    def validate_email(self, value):
        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError('البريد الإلكتروني مسجل مسبقاً')
        return value

    def create(self, validated_data):
        person = Person(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            person_type='supervisor',
        )
        person.set_password(validated_data['password'])
        person.save()

        SupervisorProfile.objects.create(
            person=person,
            university=validated_data.get('university', ''),
            department=validated_data.get('department', ''),
            job_title=validated_data.get('specialization', ''),
        )

        OTPVerification.objects.create(
            person=person,
            otp_code=''.join(random.choices(string.digits, k=6)),
            purpose='registration',
            expires_at=datetime.now() + timedelta(minutes=15),
        )

        return person


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            person = Person.objects.get(email=data['email'])
        except Person.DoesNotExist:
            raise serializers.ValidationError('البريد الإلكتروني غير مسجل')

        otp = OTPVerification.objects.filter(
            person=person,
            otp_code=data['otp_code'],
            purpose='registration',
            is_used=False,
            expires_at__gt=datetime.now()
        ).first()

        if not otp:
            raise serializers.ValidationError('رمز التحقق غير صحيح أو منتهي الصلاحية')

        data['person'] = person
        data['otp'] = otp
        return data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            Person.objects.get(email=value)
        except Person.DoesNotExist:
            raise serializers.ValidationError('البريد الإلكتروني غير مسجل')
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('كلمتا المرور غير متطابقتين')

        try:
            person = Person.objects.get(email=data['email'])
        except Person.DoesNotExist:
            raise serializers.ValidationError('البريد الإلكتروني غير مسجل')

        otp = OTPVerification.objects.filter(
            person=person,
            otp_code=data['otp_code'],
            purpose='password_reset',
            is_used=False,
            expires_at__gt=datetime.now()
        ).first()

        if not otp:
            raise serializers.ValidationError('رمز التحقق غير صحيح')

        data['person'] = person
        data['otp'] = otp
        return data


class PersonSerializer(serializers.ModelSerializer):
    trainee_id = serializers.SerializerMethodField()
    company_id = serializers.SerializerMethodField()
    supervisor_id = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    university = serializers.SerializerMethodField()
    major = serializers.SerializerMethodField()
    gpa = serializers.SerializerMethodField()
    year_of_study = serializers.SerializerMethodField()
    is_graduate = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    company_size = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'user_id', 'full_name', 'email', 'phone_number', 'address',
                  'profile_picture', 'person_type', 'is_verified', 'created_at',
                  'trainee_id', 'company_id', 'supervisor_id', 'company_name',
                  'skills', 'university', 'major', 'gpa', 'year_of_study', 'is_graduate',
                  'industry', 'company_size', 'department', 'about', 'website', 'location']
        read_only_fields = ['id', 'user_id', 'person_type', 'is_verified', 'created_at']

    def get_trainee_id(self, obj):
        try: return obj.trainee_profile.id
        except Exception: return None

    def get_company_id(self, obj):
        try: return obj.company_profile.id
        except Exception: return None

    def get_supervisor_id(self, obj):
        try: return obj.supervisor_profile.id
        except Exception: return None

    def get_company_name(self, obj):
        try: return obj.company_profile.company_name
        except Exception: return None

    def get_skills(self, obj):
        try: return obj.trainee_profile.skills
        except Exception: return None

    def get_university(self, obj):
        try:
            if obj.person_type == 'trainee':
                return obj.trainee_profile.university
            elif obj.person_type == 'supervisor':
                return obj.supervisor_profile.university
        except Exception: pass
        return None

    def get_major(self, obj):
        try: return obj.trainee_profile.major
        except Exception: return None

    def get_gpa(self, obj):
        try: return obj.trainee_profile.gpa
        except Exception: return None

    def get_year_of_study(self, obj):
        try: return obj.trainee_profile.year_of_study
        except Exception: return None

    def get_is_graduate(self, obj):
        try: return obj.trainee_profile.is_graduate
        except Exception: return None

    def get_industry(self, obj):
        try: return obj.company_profile.industry
        except Exception: return None

    def get_company_size(self, obj):
        try: return obj.company_profile.company_size
        except Exception: return None

    def get_department(self, obj):
        try: return obj.supervisor_profile.department
        except Exception: return None

    def get_about(self, obj):
        try: return obj.company_profile.about
        except Exception: return None

    def get_website(self, obj):
        try: return obj.company_profile.website
        except Exception: return None

    def get_location(self, obj):
        try:
            if obj.person_type == 'company':
                return obj.company_profile.location
        except Exception: pass
        try:
            if obj.person_type == 'trainee':
                return obj.trainee_profile.location
        except Exception: pass
        return None
