"""
دوال API للمصادقة والملف الشخصي - يحتوي على جميع Views المسؤولة عن
تسجيل الدخول، التسجيل، التحقق من OTP، إعادة تعيين كلمة المرور، إدارة الملف الشخصي، وتسجيل الخروج.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import jwt
from datetime import datetime, timedelta
from .models import Person, OTPVerification
from .serializers import (
    LoginSerializer, RegisterTraineeSerializer, RegisterCompanySerializer,
    RegisterSupervisorSerializer, OTPVerifySerializer, ResetPasswordSerializer,
    ResetPasswordConfirmSerializer, PersonSerializer
)
from .email_utils import send_otp_email
from django.conf import settings


# ═══════════════════════════════════════════════════════════════════════
# دالة مساعدة لإنشاء رمز JWT للمصادقة
# ═══════════════════════════════════════════════════════════════════════

def generate_token(user):
    """إنشاء رمز JWT يحتوي على بيانات المستخدم وصلاحية لمدة 7 أيام"""
    payload = {
        'user_id': user.user_id,  # المعرف الفريد للمستخدم
        'email': user.email,  # البريد الإلكتروني
        'person_type': user.person_type,  # نوع المستخدم
        'exp': datetime.utcnow() + timedelta(days=7),  # تاريخ انتهاء الصلاحية (7 أيام)
        'iat': datetime.utcnow(),  # تاريخ إصدار الرمز
    }
    # تشفير الرمز بالمفتاح السري
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


# ═══════════════════════════════════════════════════════════════════════
# واجهة تسجيل الدخول
# ═══════════════════════════════════════════════════════════════════════

class LoginView(APIView):
    """API تسجيل الدخول - يتحقق من بيانات المستخدم ويعيد رمز JWT"""

    def post(self, request):
        """معالجة طلب تسجيل الدخول"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # التحقق من صحة البيانات
        user = serializer.validated_data['user']
        token = generate_token(user)  # إنشاء رمز JWT
        return Response({
            'token': token,
            'user': PersonSerializer(user).data,  # بيانات المستخدم كاملة
            'message': 'تم تسجيل الدخول بنجاح'
        }, status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════
# واجهات التسجيل لأنواع المستخدمين المختلفة
# ═══════════════════════════════════════════════════════════════════════

class RegisterTraineeView(APIView):
    """API تسجيل متدرب جديد - ينشئ حساب المتدرب ويرسل رمز التحقق"""

    def post(self, request):
        """معالجة طلب تسجيل المتدرب"""
        serializer = RegisterTraineeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # إنشاء حساب المتدرب

        # جلب أحدث رمز تحقق غير مستخدم
        otp_obj = OTPVerification.objects.filter(person=user, purpose='registration', is_used=False).last()
        if otp_obj:
            try:
                # إرسال رمز التحقق بالبريد الإلكتروني
                send_otp_email(user.email, otp_obj.otp_code, purpose='registration')
            except Exception:
                pass  # تجاهل الخطأ إذا فشل إرسال البريد

        return Response({
            'message': 'تم التسجيل بنجاح. تم إرسال رمز التحقق على بريدك الإلكتروني.',
            'otp_code': otp_obj.otp_code if otp_obj else None,  # الرمز تُرجع للتطوير فقط
            'user': PersonSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class RegisterCompanyView(APIView):
    """API تسجيل شركة جديدة - ينشئ حساب الشركة ويرسل رمز التحقق"""

    def post(self, request):
        """معالجة طلب تسجيل الشركة"""
        serializer = RegisterCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # إنشاء حساب الشركة

        # جلب وإرسال رمز التحقق
        otp_obj = OTPVerification.objects.filter(person=user, purpose='registration', is_used=False).last()
        if otp_obj:
            try:
                send_otp_email(user.email, otp_obj.otp_code, purpose='registration')
            except Exception:
                pass

        return Response({
            'message': 'تم التسجيل بنجاح. تم إرسال رمز التحقق على بريدك الإلكتروني.',
            'otp_code': otp_obj.otp_code if otp_obj else None,
            'user': PersonSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class RegisterSupervisorView(APIView):
    """API تسجيل مشرف جديد - ينشئ حساب المشرف ويرسل رمز التحقق"""

    def post(self, request):
        """معالجة طلب تسجيل المشرف"""
        serializer = RegisterSupervisorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # إنشاء حساب المشرف

        # جلب وإرسال رمز التحقق
        otp_obj = OTPVerification.objects.filter(person=user, purpose='registration', is_used=False).last()
        if otp_obj:
            try:
                send_otp_email(user.email, otp_obj.otp_code, purpose='registration')
            except Exception:
                pass

        return Response({
            'message': 'تم التسجيل بنجاح. تم إرسال رمز التحقق على بريدك الإلكتروني.',
            'otp_code': otp_obj.otp_code if otp_obj else None,
            'user': PersonSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


# ═══════════════════════════════════════════════════════════════════════
# واجهات التحقق من OTP
# ═══════════════════════════════════════════════════════════════════════

class VerifyOTPView(APIView):
    """API التحقق من رمز OTP - يُفعّل الحساب بعد إدخال الرمز الصحيح"""

    def post(self, request):
        """معالجة طلب التحقق من OTP"""
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        person = serializer.validated_data['person']
        otp = serializer.validated_data['otp']

        # تفعيل حساب المستخدم (التحقق من البريد الإلكتروني)
        person.is_verified = True
        person.save()

        # تعليم الرمز كمستخدم حتى لا يمكن استخدامه مرة أخرى
        otp.is_used = True
        otp.save()

        # إنشاء رمز JWT للمستخدم بعد التحقق
        token = generate_token(person)
        return Response({
            'token': token,
            'user': PersonSerializer(person).data,
            'message': 'تم التحقق من الحساب بنجاح'
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """API إعادة إرسال رمز التحقق - يُنشئ رمزاً جديداً ويرسله بالبريد"""

    def post(self, request):
        """معالجة طلب إعادة إرسال OTP"""
        email = request.data.get('email', '')
        if not email:
            return Response({'error': 'البريد الإلكتروني مطلوب'}, status=status.HTTP_400_BAD_REQUEST)

        # البحث عن المستخدم بالبريد الإلكتروني
        try:
            person = Person.objects.get(email=email)
        except Person.DoesNotExist:
            return Response({'error': 'البريد الإلكتروني غير مسجل'}, status=status.HTTP_404_NOT_FOUND)

        # تعطيل أي رموز تحقق سابقة لم تُستخدم
        OTPVerification.objects.filter(person=person, purpose='registration', is_used=False).update(is_used=True)

        # إنشاء رمز تحقق جديد عشوائي من 6 أرقام
        otp_code = ''.join(__import__('random').choices(__import__('string').digits, k=6))
        OTPVerification.objects.create(
            person=person,
            otp_code=otp_code,
            purpose='registration',
            expires_at=datetime.now() + timedelta(minutes=15),  # صالح لمدة 15 دقيقة
        )

        # إرسال الرمز الجديد بالبريد الإلكتروني
        send_otp_email(person.email, otp_code, purpose='registration')
        return Response({'message': 'تم إعادة إرسال رمز التحقق على بريدك الإلكتروني', 'otp_code': otp_code}, status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════
# واجهات إعادة تعيين كلمة المرور
# ═══════════════════════════════════════════════════════════════════════

class ForgotPasswordView(APIView):
    """API نسيان كلمة المرور - يُرسل رمز تحقق لإعادة تعيين كلمة المرور"""

    def post(self, request):
        """معالجة طلب نسيان كلمة المرور"""
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        person = Person.objects.get(email=email)

        import random, string

        # تعطيل أي رموز إعادة تعيين سابقة
        OTPVerification.objects.filter(person=person, purpose='password_reset', is_used=False).update(is_used=True)

        # إنشاء رمز إعادة تعيين كلمة المرور الجديد
        OTPVerification.objects.create(
            person=person,
            otp_code=''.join(random.choices(string.digits, k=6)),
            purpose='password_reset',  # غرض مختلف: إعادة تعيين كلمة المرور
            expires_at=datetime.now() + timedelta(minutes=15),
        )

        # جلب الرمز وإرساله بالبريد الإلكتروني
        otp_obj = OTPVerification.objects.filter(person=person, purpose='password_reset', is_used=False).last()
        if otp_obj:
            send_otp_email(person.email, otp_obj.otp_code, purpose='password_reset')
        return Response({'message': 'تم إرسال رمز التحقق على بريدك الإلكتروني', 'otp_code': otp_obj.otp_code if otp_obj else None}, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView):
    """API تأكيد إعادة تعيين كلمة المرور - يُعيّن كلمة المرور الجديدة"""

    def post(self, request):
        """معالجة طلب تأكيد إعادة تعيين كلمة المرور"""
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        person = serializer.validated_data['person']
        otp = serializer.validated_data['otp']

        # تشفير وحفظ كلمة المرور الجديدة
        person.set_password(serializer.validated_data['new_password'])
        person.save()

        # تعليم رمز OTP كمستخدم
        otp.is_used = True
        otp.save()

        return Response({'message': 'تم تحديث كلمة المرور بنجاح'}, status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════
# واجهة الملف الشخصي - لعرض وتعديل بيانات المستخدم
# ═══════════════════════════════════════════════════════════════════════

class ProfileView(APIView):
    """API الملف الشخصي - عرض وتحديث بيانات المستخدم وملفه الشخصي"""

    def get(self, request):
        """عرض بيانات المستخدم الحالي"""
        # استخراج و التحقق من رمز JWT من الهيدر Authorization
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # فك تشفير الرمز والبحث عن المستخدم
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = Person.objects.get(user_id=payload['user_id'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Person.DoesNotExist):
            return Response({'error': 'رمز غير صالح'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(PersonSerializer(user).data)

    def put(self, request):
        """تحديث بيانات المستخدم وملفه الشخصي حسب نوعه"""
        # استخراج و التحقق من رمز JWT
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = Person.objects.get(user_id=payload['user_id'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Person.DoesNotExist):
            return Response({'error': 'رمز غير صالح'}, status=status.HTTP_401_UNAUTHORIZED)

        # تحديث الحقول الأساسية في نموذج Person
        for field in ['full_name', 'phone_number', 'address']:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()

        # تحديث ملف المتدرب الشخصي إذا كان المستخدم متدرباً
        if user.person_type == 'trainee':
            try:
                profile = user.trainee_profile
            except Exception:
                from .models import Trainee
                profile = Trainee.objects.create(person=user)
            # تحديث حقول المتدرب مع تحويل الأنواع المناسبة
            for field in ['university', 'major', 'gpa', 'year_of_study', 'is_graduate', 'gender', 'skills', 'location']:
                if field in request.data:
                    val = request.data[field]
                    # تحويل الأنواع حسب الحقل
                    if field in ['gpa']:
                        val = float(val) if val else 0.0
                    elif field in ['year_of_study']:
                        val = int(val) if val else 1
                    elif field in ['is_graduate']:
                        val = bool(val)
                    setattr(profile, field, val)
            profile.save()

        # تحديث ملف الشركة الشخصي إذا كان المستخدم شركة
        elif user.person_type == 'company':
            try:
                profile = user.company_profile
            except Exception:
                from .models import CompanyProfile
                profile = CompanyProfile.objects.create(person=user, company_name=user.full_name)
            # تحديث حقول الشركة
            for field in ['company_name', 'industry', 'company_size', 'location', 'website', 'about']:
                if field in request.data:
                    setattr(profile, field, request.data[field])
            profile.save()

        # تحديث ملف المشرف الشخصي إذا كان المستخدم مشرفاً
        elif user.person_type == 'supervisor':
            try:
                profile = user.supervisor_profile
            except Exception:
                from .models import SupervisorProfile
                profile = SupervisorProfile.objects.create(person=user)
            # تحديث حقول المشرف
            for field in ['university', 'department', 'job_title', 'professional_experience']:
                if field in request.data:
                    setattr(profile, field, request.data[field])
            profile.save()

        # إعادة بيانات المستخدم المحدثة
        return Response(PersonSerializer(user).data)


# ═══════════════════════════════════════════════════════════════════════
# واجهة تسجيل الخروج
# ═══════════════════════════════════════════════════════════════════════

class LogoutView(APIView):
    """API تسجيل الخروج - يُرجع رسالة تأكيد (تسجيل الخروج يتم بالطرف العميل عبر حذف الرمز)"""

    def post(self, request):
        """معالجة طلب تسجيل الخروج"""
        return Response({'message': 'تم تسجيل الخروج بنجاح'}, status=status.HTTP_200_OK)
