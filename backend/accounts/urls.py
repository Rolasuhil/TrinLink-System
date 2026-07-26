"""
مسارات API للمصادقة - يحتوي على جميع مسارات API الخاصة بتسجيل الدخول والتسجيل
والتحقق وإعادة تعيين كلمة المرور والملف الشخصي وتسجيل الخروج.
"""

from django.urls import path
from . import views

# تعريف جميع مسارات API للمصادقة
urlpatterns = [
    # مسار تسجيل الدخول - POST مع البريد وكلمة المرور ونوع المستخدم
    path('login/', views.LoginView.as_view(), name='login'),

    # مسارات التسجيل لكل نوع مستخدم
    path('register/trainee/', views.RegisterTraineeView.as_view(), name='register-trainee'),  # تسجيل متدرب
    path('register/company/', views.RegisterCompanyView.as_view(), name='register-company'),  # تسجيل شركة
    path('register/supervisor/', views.RegisterSupervisorView.as_view(), name='register-supervisor'),  # تسجيل مشرف

    # مسارات التحقق من رمز OTP
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),  # تأكيد رمز التحقق
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),  # إعادة إرسال الرمز

    # مسارات إعادة تعيين كلمة المرور
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),  # طلب إعادة التعيين
    path('reset-password/', views.ResetPasswordConfirmView.as_view(), name='reset-password'),  # تأكيد كلمة المرور الجديدة

    # مسار إدارة الملف الشخصي
    path('profile/', views.ProfileView.as_view(), name='profile'),  # عرض وتحديث الملف الشخصي

    # مسار تسجيل الخروج
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
