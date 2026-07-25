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


def generate_token(user):
    payload = {
        'user_id': user.user_id,
        'email': user.email,
        'person_type': user.person_type,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = generate_token(user)
        return Response({
            'token': token,
            'user': PersonSerializer(user).data,
            'message': 'تم تسجيل الدخول بنجاح'
        }, status=status.HTTP_200_OK)


class RegisterTraineeView(APIView):
    def post(self, request):
        serializer = RegisterTraineeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        otp_obj = OTPVerification.objects.filter(person=user, purpose='registration', is_used=False).last()
        if otp_obj:
            send_otp_email(user.email, otp_obj.otp_code, purpose='registration')
        return Response({
            'message': 'تم التسجيل بنجاح. تم إرسال رمز التحقق على بريدك الإلكتروني.',
            'otp_code': otp_obj.otp_code if otp_obj else None,
            'user': PersonSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class RegisterCompanyView(APIView):
    def post(self, request):
        serializer = RegisterCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        otp_obj = OTPVerification.objects.filter(person=user, purpose='registration', is_used=False).last()
        if otp_obj:
            send_otp_email(user.email, otp_obj.otp_code, purpose='registration')
        return Response({
            'message': 'تم التسجيل بنجاح. تم إرسال رمز التحقق على بريدك الإلكتروني.',
            'otp_code': otp_obj.otp_code if otp_obj else None,
            'user': PersonSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class RegisterSupervisorView(APIView):
    def post(self, request):
        serializer = RegisterSupervisorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        otp_obj = OTPVerification.objects.filter(person=user, purpose='registration', is_used=False).last()
        if otp_obj:
            send_otp_email(user.email, otp_obj.otp_code, purpose='registration')
        return Response({
            'message': 'تم التسجيل بنجاح. تم إرسال رمز التحقق على بريدك الإلكتروني.',
            'otp_code': otp_obj.otp_code if otp_obj else None,
            'user': PersonSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        person = serializer.validated_data['person']
        otp = serializer.validated_data['otp']

        person.is_verified = True
        person.save()
        otp.is_used = True
        otp.save()

        token = generate_token(person)
        return Response({
            'token': token,
            'user': PersonSerializer(person).data,
            'message': 'تم التحقق من الحساب بنجاح'
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        if not email:
            return Response({'error': 'البريد الإلكتروني مطلوب'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            person = Person.objects.get(email=email)
        except Person.DoesNotExist:
            return Response({'error': 'البريد الإلكتروني غير مسجل'}, status=status.HTTP_404_NOT_FOUND)

        OTPVerification.objects.filter(person=person, purpose='registration', is_used=False).update(is_used=True)
        otp_code = ''.join(__import__('random').choices(__import__('string').digits, k=6))
        OTPVerification.objects.create(
            person=person,
            otp_code=otp_code,
            purpose='registration',
            expires_at=datetime.now() + timedelta(minutes=15),
        )
        send_otp_email(person.email, otp_code, purpose='registration')
        return Response({'message': 'تم إعادة إرسال رمز التحقق على بريدك الإلكتروني', 'otp_code': otp_code}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        person = Person.objects.get(email=email)

        import random, string
        OTPVerification.objects.filter(person=person, purpose='password_reset', is_used=False).update(is_used=True)
        OTPVerification.objects.create(
            person=person,
            otp_code=''.join(random.choices(string.digits, k=6)),
            purpose='password_reset',
            expires_at=datetime.now() + timedelta(minutes=15),
        )

        otp_obj = OTPVerification.objects.filter(person=person, purpose='password_reset', is_used=False).last()
        if otp_obj:
            send_otp_email(person.email, otp_obj.otp_code, purpose='password_reset')
        return Response({'message': 'تم إرسال رمز التحقق على بريدك الإلكتروني', 'otp_code': otp_obj.otp_code if otp_obj else None}, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView):
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        person = serializer.validated_data['person']
        otp = serializer.validated_data['otp']

        person.set_password(serializer.validated_data['new_password'])
        person.save()
        otp.is_used = True
        otp.save()

        return Response({'message': 'تم تحديث كلمة المرور بنجاح'}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = Person.objects.get(user_id=payload['user_id'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Person.DoesNotExist):
            return Response({'error': 'رمز غير صالح'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(PersonSerializer(user).data)

    def put(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = Person.objects.get(user_id=payload['user_id'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Person.DoesNotExist):
            return Response({'error': 'رمز غير صالح'}, status=status.HTTP_401_UNAUTHORIZED)

        for field in ['full_name', 'phone_number', 'address']:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()

        return Response(PersonSerializer(user).data)


class LogoutView(APIView):
    def post(self, request):
        return Response({'message': 'تم تسجيل الخروج بنجاح'}, status=status.HTTP_200_OK)
