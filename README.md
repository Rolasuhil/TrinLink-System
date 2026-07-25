# TrainLink - منصة البحث عن فرص التدريب

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![HTML5](https://img.shields.io/badge/HTML5-34-pages-orange?logo=html5)
![License](https://img.shields.io/badge/License-MIT-yellow)

> منصة متكاملة لربط المتدربيين الجامعيين بفرص التدريب في الشركات، مع نظام ذكاء اصطناعي لتحليل السير الذاتية والمطابقة.

## جدول المحتويات

- [نظرة عامة](#نظرة-عامة)
- [الميزات الرئيسية](#الميزات-الرئيسية)
- [معمارية النظام](#معمارية-النظام)
- [هيكل المشروع](#هيكل-المشروع)
- [تثبيت وتشغيل](#تثبيت-وتشغيل)
- [واجهة برمجة التطبيقات API](#واجهة-برمجة-التطبيقات)
- [نماذج البيانات](#نماذج-البيانات)
- [أنماط التصميم](#أنماط-التصميم)
- [التقنيات المستخدمة](#التقنيات-المستخدمة)
- [الفريق](#الفريق)

---

## نظرة عامة

**TrainLink** هو نظام ويب متكامل مبني بمنهجية **MVC / 3-Tier** يهدف إلى:

- تسهيل عملية البحث عن فرص التدريب للمتدربيين الجامعيين
- توفير لوحة تحكم شاملة للشركات لإدارة فرص التدريب
- تمكين المشرفين الأكاديميين من متابعة تقدم المتدربيين
- استخدام الذكاء الاصطناعي (Gemini API) لتحليل السير الذاتية والمطابقة

### إحصائيات المشروع

| المقياس | العدد |
|---------|-------|
| تطبيقات Django | 7 |
| نماذج البيانات | 25 |
| نقاط نهاية API | 36 |
| صفحات الواجهة | 34 |
| ملفات Python | ~65 |
| مستخدمين مدعومين | 4 أنواع |

---

## الميزات الرئيسية

### للمتدرب (Trainee)
- تسجيل حساب مع التحقق بالبريد OTP
- البحث عن فرص التدريب بالتصنيف والموقع
- تقديم الطلبات ومتابعة حالتها
- رفع وتحليل السيرة الذاتية بالذكاء الاصطناعي
- تقييم الشركات وتجربتها
- نظام دردشة مع الشركات والمشرفين
- تسجيل الحضور اليومي وإرسال التقارير
- منشورات المجتمع والتفاعل

### للشركة (Company)
- نشر فرص التدريب
- مراجعة وقبول/رفض المتقدمين
- متابعة تقدم المتدربيين
- ملف الشركة التعريفي
- نظام دردشة مع المتدربيين

### للمشرف الأكاديمي (Supervisor)
- عرض قائمة المتدربيين المُعيَّنين
- مراجعة وتقييم تقارير التقدم
- نظام دردشة مع المتدربيين

### للمسؤول (Admin)
- لوحة تحكم شاملة بإحصائيات النظام
- إدارة المستخدمين (قبول/حظر/تعديل)
- إدارة المحتوى والمنشورات
- تقارير الإحصائيات
- إيعاز المتدربيين للمشرفين

---

## معمارية النظام

### نمط 3-Tier + MVC

```
┌─────────────────────────────────────────────────┐
│           طبقة العرض (Presentation)              │
│   Frontend: HTML5 + CSS3 + JavaScript            │
│   34 صفحة - RTL - ثيم بنفسجي                      │
├─────────────────────────────────────────────────┤
│           طبقة منطق الأعمال (Business Logic)     │
│   Backend: Django 4.2 + Django REST Framework    │
│   7 تطبيقات - JWT Auth - Gemini AI              │
├─────────────────────────────────────────────────┤
│           طبقة البيانات (Data Layer)             │
│   Database: MySQL / SQLite                       │
│   25 نموذج - ORM - Migrations                     │
└─────────────────────────────────────────────────┘
```

### فصل المسؤوليات (Separation of Concerns)

| الطبقة | المسؤولية | الموقع |
|--------|----------|--------|
| **العرض** | واجهة المستخدم، التنقل، التحقق من المدخلات | `frontend/` |
| **المنطق** | معالجة الطلبات، المصادقة، قواعد الأعمال | `backend/*/views.py` |
| **البيانات** | نماذج البيانات، علاقات الجداول، الاستعلامات | `backend/*/models.py` |

---

## هيكل المشروع

```
TrinLink-System/
├── backend/                        # طبقة الخادم (Server-Side)
│   ├── manage.py                   # Django CLI
│   ├── trainlink/                  # إعدادات المشروع
│   │   ├── settings.py             # الإعدادات العامة
│   │   ├── urls.py                 # توجيهات URLs الرئيسية
│   │   ├── wsgi.py                 # نقطة دخول WSGI
│   │   └── asgi.py                 # نقطة دخول ASGI
│   │
│   ├── accounts/                   # التطبيق: إدارة الحسابات
│   │   ├── models.py               # Person, Trainee, CompanyProfile, OTP, CV
│   │   ├── views.py                # تسجيل الدخول، التسجيل، OTP، الملف الشخصي
│   │   ├── serializers.py          # مسلسلات البيانات
│   │   ├── urls.py                 # 10 نقاط نهاية API
│   │   └── email_utils.py          # إرسال OTP عبر Gmail SMTP
│   │
│   ├── internships/                # التطبيق: فرص التدريب
│   │   ├── models.py               # Internship, Application, Category
│   │   ├── views.py                # CRUD للفرص والطلبات
│   │   └── urls.py                 # 6 نقاط نهاية API
│   │
│   ├── ai_engine/                  # التطبيق: محرك الذكاء الاصطناعي
│   │   ├── models.py               # AIMatchingResult, CVAnalysis
│   │   ├── views.py                # تحليل CV، المطابقة
│   │   └── urls.py                 # 3 نقاط نهاية API
│   │
│   ├── messaging/                  # التطبيق: الرسائل والإشعارات
│   │   ├── models.py               # ChatChannel, Message, Notification
│   │   └── urls.py                 # 3 نقاط نهاية API
│   │
│   ├── community/                  # التطبيق: مجتمع المتدربيين
│   │   ├── models.py               # CommunityPost, Comment, CompanyRating
│   │   └── urls.py                 # 4 نقاط نهاية API
│   │
│   ├── performance/                # التطبيق: الأداء والحضور
│   │   ├── models.py               # DailyAttendance, WorkReport, PerformanceReport
│   │   └── urls.py                 # 4 نقاط نهاية API
│   │
│   └── admin_panel/                # التطبيق: لوحة تحكم المسؤول
│       ├── models.py               # ContentReport
│       └── urls.py                 # 5 نقاط نهاية API
│
├── frontend/                       # طبقة العرض (Client-Side)
│   ├── css/style.css               # التنسيقات العامة
│   ├── js/app.js                   # السكريبتات العامة
│   └── pages/                      # 34 صفحة HTML
│       ├── public/                 # 8 صفحات عامة (تسجيل، دخول)
│       ├── trainee/                # 11 صفحة متدرب
│       ├── company/                # 6 صفحات شركة
│       ├── supervisor/             # 4 صفحات مشرف
│       └── admin/                  # 5 صفحات مسؤول
│
├── media/                          # الملفات المرفوعة
│   ├── cvs/                        # السير الذاتية
│   └── reports/                    # التقارير
│
└── .gitignore                      # ملفات مستبعدة من Git
```

---

## تثبيت وتشغيل

### المتطلبات

- Python 3.11+
- pip
- حساب Gmail مع App Password (للإشعارات)
- مفتاح Gemini API (للذكاء الاصطناعي)

### خطوات التثبيت

```bash
# 1. استنساخ المستودع
git clone https://github.com/Rolasuhil/TrinLink-System.git
cd TrinLink-System

# 2. إنشاء بيئة افتراضية
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. تثبيت المكتبات
cd backend
pip install djangorestframework django-cors-headers python-decouple PyJWT

# 4. إعداد ملف .env
# أنشئ ملف backend/.env يحتوي:
# SECRET_KEY=your-secret-key
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# GEMINI_API_KEY=your-gemini-key

# 5. تطبيق الترحيلات
python manage.py migrate

# 6. إنشاء حساب مسؤول
python manage.py createsuperuser

# 7. تشغيل الخادم
python manage.py runserver
```

### حسابات الاختبار

| الدور | البريد | كلمة المرور |
|-------|--------|------------|
| مسؤول | admin@trainlink.com | admin123456 |

### الوصول

| الصفحة | الرابط |
|--------|--------|
| الرئيسية | http://127.0.0.1:8000/ |
| لوحة تحكم Django | http://127.0.0.1:8000/admin/ |
| API | http://127.0.0.1:8000/api/ |

---

## واجهة برمجة التطبيقات

### المصادقة

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### نقاط نهاية API

#### الحسابات `api/auth/`

| الطريقة | النقطة | الوصف |
|---------|--------|-------|
| POST | `login/` | تسجيل الدخول |
| POST | `register/trainee/` | تسجيل متدرب |
| POST | `register/company/` | تسجيل شركة |
| POST | `register/supervisor/` | تسجيل مشرف |
| POST | `verify-otp/` | التحقق من OTP |
| POST | `resend-otp/` | إعادة إرسال OTP |
| POST | `forgot-password/` | نسيت كلمة المرور |
| POST | `reset-password/` | إعادة تعيين كلمة المرور |
| GET/PUT | `profile/` | عرض/تعديل الملف الشخصي |
| POST | `logout/` | تسجيل الخروج |

#### فرص التدريب `api/internships/`

| الطريقة | النقطة | الوصف |
|---------|--------|-------|
| GET/POST | `` | قائمة/إضافة الفرق |
| GET | `<int:pk>/` | تفاصيل فرصة |
| GET/POST | `applications/` | قائمة/تقديم طلبات |
| PATCH | `applications/<int:pk>/` | تحديث حالة الطلب |
| GET/POST | `saved/` | حفظ/إلغاء حفظ فرصة |
| GET | `categories/` | قائمة التصنيفات |

#### الرسائل `api/chat/`

| الطريقة | النقطة | الوصف |
|---------|--------|-------|
| GET/POST | `channels/` | قنوات الدردشة |
| GET/POST | `channels/<int:id>/messages/` | رسائل القناة |
| GET/PATCH | `notifications/` | الإشعارات |

#### المجتمع `api/community/`

| الطريقة | النقطة | الوصف |
|---------|--------|-------|
| GET/POST | `posts/` | المنشورات |
| GET/DELETE | `posts/<int:pk>/` | تفاصيل/حذف منشور |
| POST | `posts/<id>/comments/` | إضافة تعليق |
| GET/POST | `companies/<id>/ratings/` | تقييم شركة |

#### الأداء `api/performance/`

| الطريقة | النقطة | الوصف |
|---------|--------|-------|
| GET/POST | `attendance/` | تسجيل الحضور |
| GET/POST | `work-reports/` | تقارير العمل |
| GET/POST | `performance-reports/` | تقارير الأداء |
| GET | `supervisor/trainees/` | متدربي المشرف |

#### الذكاء الاصطناعي `api/ai/`

| الطريقة | النقطة | الوصف |
|---------|--------|-------|
| POST | `cv/upload/` | رفع السيرة الذاتية |
| GET | `match/` | مطابقة بالذكاء الاصطناعي |
| GET | `cv/analysis/` | نتائج التحليل |

#### لوحة التحكم `api/admin-panel/`

| الطريقة | النقطة | الوصف |
|---------|--------|-------|
| GET | `dashboard/` | إحصائيات لوحة التحكم |
| GET/PATCH/DELETE | `users/` | إدارة المستخدمين |
| GET/PATCH/DELETE | `content/` | إدارة المحتوى |
| GET | `reports/` | التقارير |
| POST | `assign/` | إيعاز متدرب |

---

## نماذج البيانات

### مخطط العلاقات (ER Diagram)

```
Person ──┬── Trainee ──┬── Assignment ──┬── Report
         │             │                └── PerformanceReport
         │             ├── CV ── CVAnalysis
         │             ├── DailyAttendance
         │             └── WorkReport
         │
         ├── CompanyProfile ──┬── Internship ──┬── Application ── AcceptedTrainee
         │                    │                └── SavedInternship
         │                    └── CompanyRating
         │
         ├── SupervisorProfile ── SupervisionAssignment
         │
         ├── AdminProfile
         │
         ├── OTPVerification
         ├── AuditLog
         │
         ├── ChatChannel ── Message
         └── Notification

CommunityPost ── Comment
ContentReport
Category
AIMatchingResult
```

---

## أنماط التصميم

### 1. Singleton Pattern
- **الغرض:** ضمان وجود نسخة واحدة من إعدادات Django (`settings.py`)
- **السبب في الاختيار:** Django يستخدم Singleton تلقائياً لإدارة الإعدادات
- **التنفيذ:** `django.conf.settings` يوفر نقطة وصول واحدة للإعدادات

### 2. Factory Pattern
- **الغرض:** إنشاء مستخدمين بأنواع مختلفة (متدرب، شركة، مشرف، مسؤول)
- **السبب في الاختيار:** كل نوع له مسلسل ونموذج مختلف
- **التنفيذ:** `RegisterTraineeView`, `RegisterCompanyView`, `RegisterSupervisorView` كل واحد ينشئ نوع مختلف

### 3. Observer Pattern
- **الغرض:** إرسال إشعارات تلقائية عند تحديث الحالات
- **السبب في الاختيار:** عند قبول طلب تدريب، يجب إشعار المتدرب والشركة
- **التنفيذ:** `Notification.objects.create()` في views عند تغيير حالة الطلبات

### 4. Strategy Pattern
- **الغرض:** تحليل السير الذاتية بطرق مختلفة
- **السبب في الاختيار:** يمكن تحليل CV بالذكاء الاصطناعي أو يدوياً
- **التنفيذ:** `CVAnalysis` model مع `overall_score` و `suggestions` و `strengths`

### 5. MVC Pattern (المعمارية العامة)
- **الغرض:** فصل العرض عن المنطق عن البيانات
- **السبب في الاختيار:** سهولة الصيانة والتعديل
- **التنفيذ:**
  - **View (العرض):** `frontend/pages/*.html` - 34 صفحة
  - **Controller (المنطق):** `backend/*/views.py` - 36 نقطة نهاية
  - **Model (البيانات):** `backend/*/models.py` - 25 نموذج

---

## التقنيات المستخدمة

### الخادم (Backend)

| التقنية | الغرض |
|---------|-------|
| **Python 3.11+** | لغة البرمجة |
| **Django 4.2** | إطار العمل |
| **Django REST Framework** | بناء API |
| **PyJWT** | مصادقة JWT |
| **python-decouple** | إدارة المتغيرات البيئية |
| **django-cors-headers** | معالجة CORS |
| **SQLite3** | قاعدة البيانات |
| **Gmail SMTP** | إرسال OTP بالبريد |

### العميل (Frontend)

| التقنية | الغرض |
|---------|-------|
| **HTML5** | بنية الصفحات |
| **CSS3** | التنسيقات (RTL - Cairo Font - Purple Theme) |
| **JavaScript** | التفاعل مع API |
| **Tabler Icons** | الأيقونات |

### الخدمات الخارجية

| الخدمة | الغرض |
|--------|-------|
| **Google Gemini API** | تحليل السيرة الذاتية بالذكاء الاصطناعي |
| **Cloudinary** | تخزين الملفات |
| **Gmail SMTP** | إرسال OTP |

### أنواع المستخدمين

| النوع | المعرّف | الوصف |
|-------|---------|-------|
| متدرب | `TR` | طالب جامعي يبحث عن تدريب |
| شركة | `CO` | جهة تقدم فرص تدريب |
| مشرف | `SV` | مشرف أكاديمي يتتبع المتدربيين |
| مسؤول | `AD` | مسؤول النظام |

---

## الفريق

| العضو | الدور |
|-------|-------|
| **رولا سهيل أبو الدهن** | مطورة المشروع |
| **المهندس فراس العجلة** | المشرف على المشروع |

**الجامعة:** جامعة الأقصى - غزة
**المقرر:** هندسة البرمجيات
