from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_otp_email(email, otp_code, purpose='registration'):
    subject_map = {
        'registration': 'TrainLink - رمز التحقق',
        'password_reset': 'TrainLink - رمز إعادة تعيين كلمة المرور',
    }
    message_map = {
        'registration': f'مرحباً،\n\nرمز التحقق الخاص بك هو: {otp_code}\n\nهذا الرمز صالح لمدة 15 دقيقة.\n\nمع تحيات،\nفريق TrainLink',
        'password_reset': f'مرحباً،\n\nرمز إعادة تعيين كلمة المرور هو: {otp_code}\n\nهذا الرمز صالح لمدة 15 دقيقة.\n\nمع تحيات،\nفريق TrainLink',
    }

    subject = subject_map.get(purpose, 'TrainLink - رمز التحقق')
    message = message_map.get(purpose, f'رمز التحقق: {otp_code}')

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f'Failed to send OTP email to {email}: {e}')
        return False
