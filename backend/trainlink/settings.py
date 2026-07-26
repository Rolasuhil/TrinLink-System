"""
ملف الإعدادات الرئيسي لمشروع TrainLink
يحتوي على جميع إعدادات Django بما في ذلك قاعدة البيانات، الأمان، التطبيقات، البريد الإلكتروني، والخدمات الخارجية
"""

import os
from pathlib import Path
from decouple import config

# ============================================================
# المسار الأساسي للمشروع - يمثل مجلد backend/
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# مفتاح الأمان السري للمشروع (يُقرأ من متغيرات البيئة)
# ============================================================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-_$^5bm2cg+rnjm_fbs2h-58+%m8%m781xd3=!-yd)^z804v0ap')

# ============================================================
# وضع التطوير - عند تفعيله يعرض أخطاء التفصيلية
# ============================================================
DEBUG = config('DEBUG', default=True, cast=bool)

# ============================================================
# الأسماء المسموح لها بالوصول للموقع ( * تعني جميع الأسماء )
# ============================================================
ALLOWED_HOSTS = ['*']

# ============================================================
# التطبيقات المسجلة في المشروع
# ============================================================
INSTALLED_APPS = [
    # --- تطبيقات Django الأساسية ---
    'django.contrib.admin',         # لوحة إدارة Django
    'django.contrib.auth',          # نظام المصادقة وإدارة المستخدمين
    'django.contrib.contenttypes',  # نظام أنواع المحتوى
    'django.contrib.sessions',      # نظام جلسات المستخدمين
    'django.contrib.messages',      # نظام الرسائل
    'django.contrib.staticfiles',   # إدارة الملفات الثابتة (CSS, JS, صور)

    # --- تطبيقات bênParty ---
    'rest_framework',   # واجهة برمجة تطبيقات Django REST
    'corsheaders',      # إدارة سياسة مصادر تعدد الأصول (CORS)

    # --- تطبيقات المشروع ---
    'accounts',         # تطبيق إدارة الحسابات والمستخدمين
    'internships',      # تطبيق التدريب العملي والتمارين
    'ai_engine',        # محرك الذكاء الاصطناعي
    'messaging',        # تطبيق المراسلة
    'community',        # تطبيق المجتمع والتفاعل
    'admin_panel',      # تطبيق لوحة الإدارة المخصصة
    'performance',      # تطبيق الأداء والتقييم
]

# ============================================================
# طبقات الوسيطات (Middleware)
# تمر الطلبات عبرها قبل الوصول لل views
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # حماية أمنية للطلبات
    'corsheaders.middleware.CorsMiddleware',                   # السماح بالطلبات من مصادر خارجية
    'django.contrib.sessions.middleware.SessionMiddleware',    # إدارة الجلسات
    'django.middleware.common.CommonMiddleware',               # المعالجات العامة
    'django.contrib.auth.middleware.AuthenticationMiddleware', # مصادقة المستخدم تلقائياً
    'django.contrib.messages.middleware.MessageMiddleware',    # إدارة الرسائل
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # حماية من هجمات Clickjacking
]

# ============================================================
# مسار ملف URLs الرئيسي للمشروع
# ============================================================
ROOT_URLCONF = 'trainlink.urls'

# ============================================================
# إعدادات القوالب (Templates)
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # محرك القوالب الافتراضي
        'DIRS': [BASE_DIR.parent / 'frontend'],  # مجلد القوالب = مجلد الواجهة الأمامية
        'APP_DIRS': True,  # البحث عن القوالب داخل تطبيقات المشروع
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',   # معالج الطلبات
                'django.contrib.auth.context_processors.auth',  # بيانات المستخدم المصادق عليه
                'django.contrib.messages.context_processors.messages', # الرسائل
            ],
        },
    },
]

# ============================================================
# تطبيق WSGI - نقطة الدخول للخادم
# ============================================================
WSGI_APPLICATION = 'trainlink.wsgi.application'

# ============================================================
# إعدادات قاعدة البيانات
# استخدام SQLite كقاعدة بيانات للتطوير
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # محرك SQLite
        'NAME': BASE_DIR / 'db.sqlite3',         # مسار ملف قاعدة البيانات
    }
}

# ============================================================
# مقاييس صحة كلمة المرور
# تتحقق من قوة كلمة مرور المستخدم
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # عدم تشابه كلمة المرور مع بيانات المستخدم
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},             # الحد الأدنى للطول
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},            # عدم استخدام كلمات مرور شائعة
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},           # عدم استخدام أرقام فقط
]

# ============================================================
# إعدادات اللغة والمنطقة الزمنية
# اللغة العربية ومنطقة غزة الزمنية
# ============================================================
LANGUAGE_CODE = 'ar'           # اللغة الافتراضية: العربية
TIME_ZONE = 'Asia/Gaza'        # المنطقة الزمنية: غزة
USE_I18N = True                # تفعيل التدويل (دعم اللغات المتعددة)
USE_TZ = True                  # استخدام المناطق الزمنية في التخزين

# ============================================================
# إعدادات الملفات الثابتة (Static Files)
# ملفات CSS و JavaScript والصور الثابتة
# ============================================================
STATIC_URL = '/static/'                    # عنوان URL للملفات الثابتة
STATICFILES_DIRS = [BASE_DIR.parent / 'frontend']  # مجلدات البحث عن الملفات الثابتة
STATIC_ROOT = BASE_DIR / 'staticfiles'     # مجلد جمع الملفات الثابتة للإنتاج

# ============================================================
# إعدادات ملفات الوسائط (Media Files)
# الملفات المرفوعة من المستخدمين (صور، مستندات، إلخ)
# ============================================================
MEDIA_URL = '/media/'                          # عنوان URL لملفات الوسائط
MEDIA_ROOT = BASE_DIR.parent / 'media'         # مجلد تخزين ملفات الوسائط

# ============================================================
# نموذج المستخدم المخصص
# استخدام نموذج Person من تطبيق accounts
# ============================================================
AUTH_USER_MODEL = 'accounts.Person'

# ============================================================
# نوع المفتاح الأساسي للنماذج الجديدة
# BigAutoField: مفتاح تلقائي من نوع integer كبير (64 بت)
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# إعدادات البريد الإلكتروني
# استخدام خادم Gmail SMTP لإرسال البريد
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # محرك البريد عبر SMTP
EMAIL_HOST = 'smtp.gmail.com'    # خادم SMTP الخاص بـ Gmail
EMAIL_PORT = 587                 # منفذ SMTP الآمن
EMAIL_USE_TLS = True             # استخدام التشفير TLS
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')          # بريد المرسل (من ملف .env)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')  # كلمة مرور البريد (من ملف .env)
DEFAULT_FROM_EMAIL = 'TrainLink <' + config('EMAIL_HOST_USER', default='noreply@trainlink.com') + '>'  # عنوان البريد الافتراضي للإرسال

# ============================================================
# إعدادات CORS
# السماح بجميع المصادر بالوصول (للتطوير فقط)
# ============================================================
CORS_ALLOW_ALL_ORIGINS = True

# ============================================================
# إعدادات Django REST Framework
# ============================================================
REST_FRAMEWORK = {
    # فئة المصادقة الافتراضية: لا توجد مصادقة مطلوبة بشكل افتراضي
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    # صلاحيات الافتراضية: السماح لأي شخص بالوصول
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    # معالج الأخطاء المخصص للتعامل مع أخطاء API
    'EXCEPTION_HANDLER': 'trainlink.exception_handler.custom_exception_handler',
}

# ============================================================
# مفاتيح الخدمات الخارجية
# ============================================================
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')            # مفتاح Google Gemini AI
CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default='')  # اسم السحابة في Cloudinary
CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY', default='')        # مفتاح API لـ Cloudinary
CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default='')  # السر الخاص بـ Cloudinary
