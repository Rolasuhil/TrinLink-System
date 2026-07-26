"""
أدوات إرسال البريد الإلكتروني - يحتوي على دوال لإرسال رسائل البريد الإلكتروني
المؤقتة مثل رموز التحقق ورموز إعادة تعيين كلمة المرور.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


# ═══════════════════════════════════════════════════════════════════════
# دالة إرسال رمز التحقق بالبريد الإلكتروني
# ═══════════════════════════════════════════════════════════════════════

def send_otp_email(email, otp_code, purpose='registration'):
    """إرسال بريد إلكتروني يحتوي على رمز التحقق (OTP) للمستخدم"""

    # خريطة العناوين حسب غرض الرمز
    subject_map = {
        'registration': 'TrainLink - رمز التحقق',  # عنوان رسالة التحقق من التسجيل
        'password_reset': 'TrainLink - رمز إعادة تعيين كلمة المرور',  # عنوان رسالة إعادة التعيين
    }

    # خريطة محتوى الرسائل حسب الغرض
    message_map = {
        'registration': f'مرحباً،\n\nرمز التحقق الخاص بك هو: {otp_code}\n\nهذا الرمز صالح لمدة 15 دقيقة.\n\nمع تحيات،\nفريق TrainLink',
        'password_reset': f'مرحباً،\n\nرمز إعادة تعيين كلمة المرور هو: {otp_code}\n\nهذا الرمز صالح لمدة 15 دقيقة.\n\nمع تحيات،\nفريق TrainLink',
    }

    # اختيار العنوان والمحتوى المناسبين
    subject = subject_map.get(purpose, 'TrainLink - رمز التحقق')
    message = message_map.get(purpose, f'رمز التحقق: {otp_code}')

    try:
        # إرسال البريد الإلكتروني باستخدام Django
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,  # البريد المرسل من (محدد في الإعدادات)
            recipient_list=[email],  # البريد المستقبل
            fail_silently=False,  # رفع خطأ إذا فشل الإرسال
        )
        return True  # نجاح الإرسال
    except Exception as e:
        # تسجيل الخطأ في وحدة التحكم عند فشل الإرسال
        print(f'Failed to send OTP email to {email}: {e}')
        return False  # فشل الإرسال
