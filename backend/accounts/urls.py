from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/trainee/', views.RegisterTraineeView.as_view(), name='register-trainee'),
    path('register/company/', views.RegisterCompanyView.as_view(), name='register-company'),
    path('register/supervisor/', views.RegisterSupervisorView.as_view(), name='register-supervisor'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordConfirmView.as_view(), name='reset-password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
