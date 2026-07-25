# TrainLink API Documentation

> توثيق شامل لواجهة برمجة التطبيقات — TrainLink منصة البحث عن فرص التدريب

---

## عام

### العنوان الأساسي

```
http://127.0.0.1:8000/api/
```

### المصادقة

جميع الطلبات المحمية تتطلب JWT Token في الـ Header:

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### أنواع الاستجابة

النظام يُرجع JSON دائماً مع الكود المناسب:

| الكود | المعنى |
|-------|--------|
| `200 OK` | نجاح |
| `201 Created` | إنشاء ناجح |
| `400 Bad Request` | طلب خاطئ / بيانات ناقصة |
| `401 Unauthorized` | غير مصرح / Token منتهي |
| `403 Forbidden` | الصلاحيات غير كافية |
| `404 Not Found` | المورد غير موجود |
| `500 Server Error` | خطأ داخلي بالخادم |

### الأخطاء الشائعة

```json
// بيانات ناقصة
{ "error": "البريد الإلكتروني مطلوب" }

// كلمة مرور خاطئة
{ "error": "كلمة المرور غير صحيحة" }

// حساب معطل
{ "error": "الحساب معطل" }

// Token منتهي
{ "detail": "Given token not valid for any token type" }
```

---

## 1. الحسابات (Accounts) — `api/auth/`

### 1.1 تسجيل الدخول

```
POST api/auth/login/
```

**لا يتطلب مصادقة**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `email` | string | نعم | البريد الإلكتروني |
| `password` | string | نعم | كلمة المرور |
| `user_type` | string | نعم | نوع الحساب: `trainee`, `company`, `supervisor`, `admin` |

**مثال:**

```json
POST /api/auth/login/
{
    "email": "ahmed@test.com",
    "password": "password123",
    "user_type": "trainee"
}
```

**استجابة ناجحة (200):**

```json
{
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "user_id": "TR1234ABCD",
        "full_name": "أحمد محمد",
        "email": "ahmed@test.com",
        "person_type": "trainee",
        "trainee_id": 1,
        "company_id": null,
        "supervisor_id": null,
        "company_name": null
    }
}
```

**أخطاء محتملة:**

| الكود | الخطأ |
|-------|-------|
| 400 | البريد الإلكتروني غير مسجل |
| 400 | كلمة المرور غير صحيحة |
| 400 | نوع الحساب غير مطابق |
| 400 | الحساب معطل |

---

### 1.2 تسجيل متدرب

```
POST api/auth/register/trainee/
```

**لا يتطلب مصادقة**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `full_name` | string | نعم | الاسم الكامل |
| `email` | string | نعم | البريد الإلكتروني (فريد) |
| `password` | string | نعم | كلمة المرور (8 أحرف على الأقل) |
| `phone_number` | string | لا | رقم الهاتف |
| `university` | string | لا | الجامعة |
| `major` | string | لا | التخصص |
| `gpa` | float | لا | المعدل التراكمي |
| `year_of_study` | integer | لا | السنة الدراسية |
| `is_graduate` | boolean | لا | خريج؟ |
| `gender` | string | لا | `M` أو `F` |
| `date_of_birth` | string | لا | تاريخ الميلاد (YYYY-MM-DD) |
| `supervisor_id` | string | لا | معرف المشرف |

**مثال:**

```json
POST /api/auth/register/trainee/
{
    "full_name": "سارة علي",
    "email": "sara@test.com",
    "password": "securepass123",
    "university": "جامعة الأقصى",
    "major": "هندسة برمجيات",
    "gpa": 3.8,
    "year_of_study": 3
}
```

**استجابة ناجحة (201):**

```json
{
    "message": "تم التسجيل بنجاح. يرجى التحقق من بريدك الإلكتروني",
    "user": {
        "id": 2,
        "user_id": "TR5678EFGH",
        "full_name": "سارة علي",
        "email": "sara@test.com",
        "person_type": "trainee"
    },
    "otp_sent": true
}
```

---

### 1.3 تسجيل شركة

```
POST api/auth/register/company/
```

**لا يتطلب مصادقة**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `company_name` | string | نعم | اسم الشركة |
| `email` | string | نعم | البريد الإلكتروني |
| `password` | string | نعم | كلمة المرور |

**مثال:**

```json
POST /api/auth/register/company/
{
    "company_name": "TechPal",
    "email": "techpal@test.com",
    "password": "securepass123"
}
```

**استجابة ناجحة (201):**

```json
{
    "message": "تم التسجيل بنجاح. يرجى التحقق من بريدك الإلكتروني",
    "user": {
        "id": 3,
        "user_id": "CO9012IJKL",
        "full_name": "TechPal",
        "email": "techpal@test.com",
        "person_type": "company"
    },
    "otp_sent": true
}
```

---

### 1.4 تسجيل مشرف

```
POST api/auth/register/supervisor/
```

**لا يتطلب مصادقة**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `full_name` | string | نعم | الاسم الكامل |
| `email` | string | نعم | البريد الإلكتروني |
| `password` | string | نعم | كلمة المرور |

**مثال:**

```json
POST /api/auth/register/supervisor/
{
    "full_name": "خالد أحمد",
    "email": "khalid@test.com",
    "password": "securepass123"
}
```

**استجابة ناجحة (201):**

```json
{
    "message": "تم التسجيل بنجاح. يرجى التحقق من بريدك الإلكتروني",
    "user": {
        "id": 4,
        "user_id": "SV3456MNOP",
        "full_name": "خالد أحمد",
        "email": "khalid@test.com",
        "person_type": "supervisor"
    },
    "otp_sent": true
}
```

---

### 1.5 التحقق من OTP

```
POST api/auth/verify-otp/
```

**لا يتطلب مصادقة**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `email` | string | نعم | البريد الإلكتروني |
| `otp_code` | string | نعم | رمز التحقق (6 أرقام) |

**مثال:**

```json
POST /api/auth/verify-otp/
{
    "email": "sara@test.com",
    "otp_code": "123456"
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم التحقق بنجاح",
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 2,
        "user_id": "TR5678EFGH",
        "full_name": "سارة علي",
        "email": "sara@test.com",
        "person_type": "trainee"
    }
}
```

---

### 1.6 إعادة إرسال OTP

```
POST api/auth/resend-otp/
```

**لا يتطلب مصادقة**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `email` | string | نعم | البريد الإلكتروني |

**مثال:**

```json
POST /api/auth/resend-otp/
{
    "email": "sara@test.com"
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم إعادة إرسال رمز التحقق"
}
```

---

### 1.7 نسيت كلمة المرور

```
POST api/auth/forgot-password/
```

**لا يتطلب مصادقة**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `email` | string | نعم | البريد الإلكتروني |

**مثال:**

```json
POST /api/auth/forgot-password/
{
    "email": "sara@test.com"
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني"
}
```

---

### 1.8 إعادة تعيين كلمة المرور

```
POST api/auth/reset-password/
```

**لا يتطلب مصادقة**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `email` | string | نعم | البريد الإلكتروني |
| `otp_code` | string | نعم | رمز التحقق |
| `new_password` | string | نعم | كلمة المرور الجديدة |

**مثال:**

```json
POST /api/auth/reset-password/
{
    "email": "sara@test.com",
    "otp_code": "123456",
    "new_password": "newsecure123"
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم تغيير كلمة المرور بنجاح"
}
```

---

### 1.9 عرض الملف الشخصي

```
GET api/auth/profile/
```

**يتطلب مصادقة (JWT)**

**استجابة ناجحة (200):**

```json
{
    "id": 2,
    "user_id": "TR5678EFGH",
    "full_name": "سارة علي",
    "email": "sara@test.com",
    "phone_number": "0599123456",
    "address": "غزة",
    "person_type": "trainee",
    "is_verified": true,
    "created_at": "2026-07-25T10:00:00Z"
}
```

---

### 1.10 تعديل الملف الشخصي

```
PUT api/auth/profile/
```

**يتطلب مصادقة (JWT)**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `full_name` | string | لا | الاسم الجديد |
| `phone_number` | string | لا | رقم الهاتف |
| `address` | string | لا | العنوان |

**مثال:**

```json
PUT /api/auth/profile/
{
    "full_name": "سارة علي محمد",
    "phone_number": "0599876543"
}
```

**استجابة ناجحة (200):**

```json
{
    "id": 2,
    "user_id": "TR5678EFGH",
    "full_name": "سارة علي محمد",
    "email": "sara@test.com",
    "phone_number": "0599876543",
    "person_type": "trainee"
}
```

---

### 1.11 تسجيل الخروج

```
POST api/auth/logout/
```

**لا يتطلب مصادقة (Token-based stateless)**

**استجابة ناجحة (200):**

```json
{
    "message": "تم تسجيل الخروج بنجاح"
}
```

---

## 2. فرص التدريب (Internships) — `api/internships/`

### 2.1 قائمة فرص التدريب / إضافة فرصة

```
GET    api/internships/
POST   api/internships/
```

#### GET — عرض الفرص

**لا يتطلب مصادقة**

**معاملات الاستعلام (Query Parameters):**

| المعامل | النوع | الوصف |
|---------|-------|-------|
| `search` | string | بحث بالعنوان أو الوصف |
| `category` | integer | تصفية حسب التصنيف |
| `location` | string | تصفية حسب الموقع |
| `type` | string | تصفية حسب النوع: `onsite`, `remote`, `hybrid` |

**مثال:**

```
GET /api/internships/?search=frontend&location=غزة
```

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "title": "مطور Frontend",
        "description": "فرصة تدريب في تطوير واجهات المستخدم",
        "company": {
            "id": 1,
            "company_name": "TechPal",
            "industry": "تكنولوجيا"
        },
        "category": {
            "id": 1,
            "name": "تطوير الويب"
        },
        "location": "غزة",
        "internship_type": "onsite",
        "start_date": "2026-09-01",
        "end_date": "2026-12-01",
        "deadline": "2026-08-15",
        "available_positions": 3,
        "status": "open",
        "created_at": "2026-07-25T10:00:00Z"
    }
]
```

#### POST — إنشاء فرصة جديدة

**يتطلب مصادقة (JWT) — شركة فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `title` | string | نعم | عنوان الفرصة |
| `description` | string | نعم | وصف الفرصة |
| `requirements` | string | لا | المتطلبات |
| `deadline` | string | نعم | آخر موعد للتقديم |
| `location` | string | نعم | الموقع |
| `internship_type` | string | نعم | `onsite`, `remote`, `hybrid` |
| `start_date` | string | نعم | تاريخ البدء |
| `end_date` | string | نعم | تاريخ الانتهاء |
| `available_positions` | integer | لا | عدد المواقع المتاحة (افتراضي: 1) |
| `category_id` | integer | لا | معرف التصنيف |

**مثال:**

```json
POST /api/internships/
{
    "title": "مطور Backend",
    "description": "فرصة تدريب في تطوير الخادم",
    "requirements": "خبرة في Python و Django",
    "deadline": "2026-12-31",
    "location": "remote",
    "internship_type": "remote",
    "start_date": "2026-09-01",
    "end_date": "2026-12-01",
    "available_positions": 2,
    "category_id": 1
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 2,
    "title": "مطور Backend",
    "description": "فرصة تدريب في تطوير الخادم",
    "status": "open"
}
```

---

### 2.2 تفاصيل فرصة تدريب

```
GET api/internships/<int:pk>/
```

**لا يتطلب مصادقة**

**استجابة ناجحة (200):**

```json
{
    "id": 1,
    "title": "مطور Frontend",
    "description": "فرصة تدريب في تطوير واجهات المستخدم",
    "requirements": "خبرة في HTML CSS JS",
    "company": {
        "id": 1,
        "company_name": "TechPal",
        "industry": "تكنولوجيا",
        "location": "غزة"
    },
    "category": {
        "id": 1,
        "name": "تطوير الويب"
    },
    "location": "غزة",
    "internship_type": "onsite",
    "start_date": "2026-09-01",
    "end_date": "2026-12-01",
    "deadline": "2026-08-15",
    "available_positions": 3,
    "status": "open"
}
```

---

### 2.3 الطلبات (Applications)

```
GET    api/internships/applications/
POST   api/internships/applications/
```

#### GET — عرض الطلبات

**يتطلب مصادقة (JWT)**

- **المتدرب:** يرى طلباته فقط
- **الشركة:** ترى طلبات فرصها فقط

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "internship": {
            "id": 1,
            "title": "مطور Frontend"
        },
        "trainee": {
            "id": 1,
            "full_name": "سارة علي",
            "email": "sara@test.com"
        },
        "status": "pending",
        "applied_at": "2026-07-25T10:00:00Z"
    }
]
```

#### POST — تقديم طلب

**يتطلب مصادقة (JWT) — متدرب فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `internship_id` | integer | نعم | معرف الفرصة |

**مثال:**

```json
POST /api/internships/applications/
{
    "internship_id": 1
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 1,
    "internship": 1,
    "status": "pending",
    "message": "تم تقديم الطلب بنجاح"
}
```

**أخطاء محتملة:**

| الخطأ |
|-------|
| لقد قدمت على هذه الفرصة مسبقاً |

---

### 2.4 تحديث حالة الطلب

```
PATCH api/internships/applications/<int:pk>/
```

**يتطلب مصادقة (JWT) — شركة فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `status` | string | نعم | `accepted` أو `rejected` |
| `rejection_reason` | string | لا | سبب الرفض |

**مثال:**

```json
PATCH /api/internships/applications/1/
{
    "status": "accepted"
}
```

**استجابة ناجحة (200):**

```json
{
    "id": 1,
    "status": "accepted",
    "message": "تم قبول الطلب"
}
```

---

### 2.5 المحفوظات (Saved)

```
GET    api/internships/saved/
POST   api/internships/saved/
```

#### GET — عرض المحفوظات

**يتطلب مصادقة (JWT) — متدرب فقط**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "internship": {
            "id": 1,
            "title": "مطور Frontend",
            "company": { "company_name": "TechPal" }
        },
        "saved_at": "2026-07-25T10:00:00Z"
    }
]
```

#### POST — حفظ / إلغاء حفظ (Toggle)

**يتطلب مصادقة (JWT) — متدرب فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `internship_id` | integer | نعم | معرف الفرصة |

**مثال:**

```json
POST /api/internships/saved/
{
    "internship_id": 1
}
```

**استجابة ناجحة (200):**

```json
{
    "saved": true,
    "message": "تم حفظ الفرصة"
}
```

---

### 2.6 التصنيفات

```
GET api/internships/categories/
```

**لا يتطلب مصادقة**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "name": "تطوير الويب",
        "description": "فرص تطوير المواقع الإلكترونية",
        "icon": "ti-code"
    },
    {
        "id": 2,
        "name": "تصميم الجرافيك",
        "description": "فرص التصميم والإبداع",
        "icon": "ti-palette"
    }
]
```

---

## 3. الرسائل والدردشة (Messaging) — `api/chat/`

### 3.1 قنوات الدردشة

```
GET    api/chat/channels/
POST   api/chat/channels/
```

#### GET — عرض القنوات

**يتطلب مصادقة (JWT)**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "participants": [
            { "id": 1, "full_name": "سارة علي", "person_type": "trainee" },
            { "id": 3, "full_name": "TechPal", "person_type": "company" }
        ],
        "last_message": {
            "content": "مرحباً، كيف حالك؟",
            "created_at": "2026-07-25T10:00:00Z"
        },
        "unread_count": 2
    }
]
```

#### POST — إنشاء قناة جديدة

**يتطلب مصادقة (JWT)**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `recipient_id` | integer | نعم | معرف المستخدم المقابل |

**مثال:**

```json
POST /api/chat/channels/
{
    "recipient_id": 3
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 1,
    "participants": [1, 3],
    "message": "تم إنشاء القناة"
}
```

**ملاحظة:** إذا كانت القناة موجودة مسبقاً، يُرجع القناة الحالية (200).

---

### 3.2 رسائل القناة

```
GET    api/chat/channels/<int:channel_id>/messages/
POST   api/chat/channels/<int:channel_id>/messages/
```

#### GET — عرض الرسائل

**يتطلب مصادقة (JWT) — مشارك في القناة فقط**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "sender": {
            "id": 1,
            "full_name": "سارة علي"
        },
        "content": "مرحباً، أريد الاستفسار عن فرصة التدريب",
        "attachment": null,
        "is_read": true,
        "created_at": "2026-07-25T10:00:00Z"
    }
]
```

#### POST — إرسال رسالة

**يتطلب مصادقة (JWT) — مشارك في القناة فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `content` | string | نعم | نص الرسالة |
| `attachment` | file | لا | مرفق |

**مثال:**

```json
POST /api/chat/channels/1/messages/
{
    "content": "شكراً لك، سأراجع الطلب"
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 2,
    "sender": 1,
    "content": "شكراً لك، سأراجع الطلب",
    "created_at": "2026-07-25T11:00:00Z"
}
```

---

### 3.3 الإشعارات

```
GET    api/chat/notifications/
PATCH  api/chat/notifications/
```

#### GET — عرض الإشعارات

**يتطلب مصادقة (JWT)**

**استجابة ناجحة (200):**

```json
{
    "notifications": [
        {
            "id": 1,
            "type": "application_accepted",
            "message": "تم قبول طلبك في فرصة مطور Frontend",
            "link": "/applications/1",
            "is_read": false,
            "created_at": "2026-07-25T10:00:00Z"
        }
    ],
    "unread_count": 5
}
```

#### PATCH — تعليم كمقروء

**يتطلب مصادقة (JWT)**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `mark_all_read` | boolean | لا | تعليم الكل كمقروء |
| `notification_id` | integer | لا | تعليم إشعار محدد كمقروء |

**مثال:**

```json
PATCH /api/chat/notifications/
{
    "mark_all_read": true
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم تحديث الإشعارات",
    "updated": 5
}
```

---

## 4. المجتمع (Community) — `api/community/`

### 4.1 المنشورات

```
GET    api/community/posts/
POST   api/community/posts/
```

#### GET — عرض المنشورات

**لا يتطلب مصادقة**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "author": {
            "id": 1,
            "full_name": "سارة علي",
            "person_type": "trainee"
        },
        "title": "نصائح للتدريب الناجح",
        "content": "شاركت تجربتي في التدريب وأتمنى أن تفيدكم...",
        "attachment": null,
        "likes_count": 12,
        "comments_count": 5,
        "is_approved": true,
        "created_at": "2026-07-25T10:00:00Z"
    }
]
```

#### POST — إنشاء منشور

**يتطلب مصادقة (JWT)**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `title` | string | نعم | عنوان المنشور |
| `content` | string | نعم | محتوى المنشور |

**مثال:**

```json
POST /api/community/posts/
{
    "title": "تجربتي في التدريب",
    "content": "أردت مشاركة تجربتي معكم..."
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 2,
    "title": "تجربتي في التدريب",
    "content": "أردت مشاركة تجربتي معكم...",
    "is_approved": false,
    "message": "تم نشر المنشور بانتظار الموافقة"
}
```

---

### 4.2 تفاصيل منشور / حذف

```
GET    api/community/posts/<int:pk>/
DELETE api/community/posts/<int:pk>/
```

#### GET — تفاصيل المنشور

**لا يتطلب مصادقة**

**استجابة ناجحة (200):**

```json
{
    "id": 1,
    "author": {
        "id": 1,
        "full_name": "سارة علي"
    },
    "title": "نصائح للتدريب الناجح",
    "content": "شاركت تجربتي...",
    "likes_count": 12,
    "comments_count": 5,
    "comments": [
        {
            "id": 1,
            "author": { "full_name": "أحمد" },
            "content": "شكراً على المشاركة!",
            "created_at": "2026-07-25T11:00:00Z"
        }
    ]
}
```

#### DELETE — حذف المنشور

**يتطلب مصادقة (JWT) — كاتب المنشور فقط**

**استجابة ناجحة (200):**

```json
{
    "message": "تم حذف المنشور بنجاح"
}
```

---

### 4.3 التعليقات

```
POST api/community/posts/<int:post_id>/comments/
```

**يتطلب مصادقة (JWT)**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `content` | string | نعم | نص التعليق |

**مثال:**

```json
POST /api/community/posts/1/comments/
{
    "content": "مشاركة مفيدة جداً!"
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 6,
    "content": "مشاركة مفيدة جداً!",
    "author": { "full_name": "سارة علي" },
    "created_at": "2026-07-25T12:00:00Z"
}
```

---

### 4.4 تقييم الشركات

```
GET    api/community/companies/<int:company_id>/ratings/
POST   api/community/companies/<int:company_id>/ratings/
```

#### GET — عرض التقييمات

**لا يتطلب مصادقة**

**استجابة ناجحة (200):**

```json
{
    "average_score": 4.2,
    "total_ratings": 15,
    "ratings": [
        {
            "id": 1,
            "trainee": { "full_name": "سارة علي" },
            "score": 5,
            "review": "بيئة عمل ممتازة وتدريب مفيد",
            "created_at": "2026-07-25T10:00:00Z"
        }
    ]
}
```

#### POST — تقييم شركة

**يتطلب مصادقة (JWT) — متدرب فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `score` | integer | نعم | التقييم (1-5) |
| `review` | string | لا | المراجعة |

**مثال:**

```json
POST /api/community/companies/1/ratings/
{
    "score": 4,
    "review": "تجربة جيدة بشكل عام"
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 2,
    "score": 4,
    "review": "تجربة جيدة بشكل عام",
    "message": "تم التقييم بنجاح"
}
```

---

## 5. الأداء (Performance) — `api/performance/`

### 5.1 الحضور اليومي

```
GET    api/performance/attendance/
POST   api/performance/attendance/
```

#### GET — سجل الحضور

**يتطلب مصادقة (JWT) — متدرب فقط**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "date": "2026-07-25",
        "check_in_time": "2026-07-25T08:00:00Z",
        "check_out_time": null,
        "status": "present"
    }
]
```

#### POST — تسجيل حضور / انصراف

**يتطلب مصادقة (JWT) — متدرب فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `action` | string | لا | `checkout` للانصراف (افتراضي: تسجيل حضور) |

**مثال — تسجيل حضور:**

```json
POST /api/performance/attendance/
{}
```

**مثال — تسجيل انصراف:**

```json
POST /api/performance/attendance/
{
    "action": "checkout"
}
```

**استجابة ناجحة (201/200):**

```json
{
    "id": 1,
    "date": "2026-07-25",
    "check_in_time": "2026-07-25T08:00:00Z",
    "status": "present",
    "message": "تم تسجيل الحضور بنجاح"
}
```

---

### 5.2 تقارير العمل

```
GET    api/performance/work-reports/
POST   api/performance/work-reports/
```

#### GET — عرض التقارير

**يتطلب مصادقة (JWT) — متدرب فقط**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "task_title": "تطوير واجهة المستخدم",
        "description": "عملت على صفحة تسجيل الدخول",
        "performance_rating": 4,
        "company_feedback": "عمل ممتاز",
        "submitted_at": "2026-07-25T10:00:00Z"
    }
]
```

#### POST — إرسال تقرير

**يتطلب مصادقة (JWT) — متدرب فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `task_title` | string | نعم | عنوان المهمة |
| `description` | string | نعم | وصف العمل |

**مثال:**

```json
POST /api/performance/work-reports/
{
    "task_title": "تطوير صفحة البحث",
    "description": "تم بناء واجهة البحث مع التصفية"
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 2,
    "task_title": "تطوير صفحة البحث",
    "description": "تم بناء واجهة البحث مع التصفية",
    "submitted_at": "2026-07-25T12:00:00Z"
}
```

---

### 5.3 تقارير الأداء الأسبوعية

```
GET    api/performance/performance-reports/
POST   api/performance/performance-reports/
```

#### GET — عرض التقارير

**يتطلب مصادقة (JWT)**

- **الشركة:** ترى تقارير متدربيها
- **المشرف:** يرى تقارير متدربيه المعينين
- **المتدرب:** يرى تقاريره

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "trainee": { "id": 1, "full_name": "سارة علي" },
        "week_number": 1,
        "performance_score": 85.5,
        "attendance_confirmed": true,
        "comments": "أداء جيد جداً",
        "ai_summary": "المتدرب يظهر تقدماً ملموساً في المهارات الأساسية",
        "ai_rating": "جيد"
    }
]
```

#### POST — إنشاء تقرير أداء

**يتطلب مصادقة (JWT) — شركة فقط**

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `trainee_id` | integer | نعم | معرف المتدرب |
| `week_number` | integer | نعم | رقم الأسبوع |
| `performance_score` | float | لا | درجة الأداء (0-100) |
| `attendance_confirmed` | boolean | لا | تأكيد الحضور |
| `comments` | string | لا | الملاحظات |

**مثال:**

```json
POST /api/performance/performance-reports/
{
    "trainee_id": 1,
    "week_number": 3,
    "performance_score": 90.0,
    "attendance_confirmed": true,
    "comments": "أداء ممتاز هذا الأسبوع"
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 3,
    "week_number": 3,
    "performance_score": 90.0,
    "message": "تم إنشاء التقرير بنجاح"
}
```

---

### 5.4 متدربي المشرف

```
GET api/performance/supervisor/trainees/
```

**يتطلب مصادقة (JWT) — مشرف فقط**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "person": {
            "full_name": "سارة علي",
            "email": "sara@test.com"
        },
        "university": "جامعة الأقصى",
        "major": "هندسة برمجيات",
        "gpa": 3.8,
        "assignment_date": "2026-07-25"
    }
]
```

---

## 6. الذكاء الاصطناعي (AI Engine) — `api/ai/`

### 6.1 رفع وتحليل السيرة الذاتية

```
POST api/ai/cv/upload/
```

**يتطلب مصادقة (JWT) — متدرب فقط**

**نوع المحتوى:** `multipart/form-data`

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `file` | file | نعم | ملف CV (PDF/DOC/DOCX، حد أقصى 5MB) |

**مثال:**

```
POST /api/ai/cv/upload/
Content-Type: multipart/form-data

file: [CV file]
```

**استجابة ناجحة (201):**

```json
{
    "id": 1,
    "file_path": "cvs/sara_cv.pdf",
    "ai_analysis": {
        "overall_score": 82,
        "section_scores": {
            "contact_info": 95,
            "education": 88,
            "experience": 75,
            "skills": 80,
            "format": 78
        },
        "suggestions": [
            "أضف خبرات عملية تتعلق بالتخصص",
            "حسّن تنسيق السيرة الذاتية"
        ],
        "strengths": [
            "معلومات اتصال واضحة",
            "تعليم متميز"
        ],
        "weaknesses": [
            "خبرة عملية محدودة",
            "غياب روابط التواصل الاجتماعي"
        ]
    },
    "ai_score": 82,
    "message": "تم تحليل السيرة الذاتية بنجاح"
}
```

---

### 6.2 المطابقة بالذكاء الاصطناعي

```
GET api/ai/match/
```

**يتطلب مصادقة (JWT) — متدرب فقط**

**استجابة ناجحة (200):**

```json
{
    "matches": [
        {
            "internship": {
                "id": 1,
                "title": "مطور Frontend",
                "company": "TechPal",
                "location": "غزة"
            },
            "match_score": 92,
            "match_reason": "توافق عالي في مهارات HTML/CSS/JS والتعليم في هندسة البرمجيات"
        },
        {
            "internship": {
                "id": 3,
                "title": "مطور ويب مبتدئ",
                "company": "CodeGaza",
                "location": "remote"
            },
            "match_score": 78,
            "match_reason": "توافق جيد في مهارات تطوير الويب"
        }
    ],
    "total_matches": 2
}
```

---

### 6.3 نتائج تحليلات CV السابقة

```
GET api/ai/cv/analysis/
```

**يتطلب مصادقة (JWT) — متدرب فقط**

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "overall_score": 82,
        "section_scores": {
            "contact_info": 95,
            "education": 88,
            "experience": 75,
            "skills": 80,
            "format": 78
        },
        "suggestions": ["أضف خبرات عملية"],
        "strengths": ["معلومات اتصال واضحة"],
        "weaknesses": ["خبرة عملية محدودة"],
        "created_at": "2026-07-25T10:00:00Z"
    }
]
```

---

## 7. لوحة التحكم (Admin Panel) — `api/admin-panel/`

> جميع نقاط النهاية في هذا القسم تتطلب **مصادقة JWT — مسؤول فقط (admin)**

### 7.1 إحصائيات لوحة التحكم

```
GET api/admin-panel/dashboard/
```

**استجابة ناجحة (200):**

```json
{
    "total_users": 50,
    "total_trainees": 30,
    "total_companies": 10,
    "total_supervisors": 5,
    "total_internships": 20,
    "open_internships": 15,
    "applications": {
        "total": 100,
        "pending": 30,
        "accepted": 50,
        "rejected": 20
    },
    "pending_companies": 3,
    "active_supervisions": 8
}
```

---

### 7.2 إدارة المستخدمين

```
GET    api/admin-panel/users/
PATCH  api/admin-panel/users/
DELETE api/admin-panel/users/
```

#### GET — عرض المستخدمين

**معاملات الاستعلام:**

| المعامل | النوع | الوصف |
|---------|-------|-------|
| `type` | string | تصفية حسب النوع: `trainee`, `company`, `supervisor`, `admin` |

**مثال:**

```
GET /api/admin-panel/users/?type=trainee
```

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "user_id": "TR1234ABCD",
        "full_name": "سارة علي",
        "email": "sara@test.com",
        "person_type": "trainee",
        "is_verified": true,
        "is_active": true,
        "created_at": "2026-07-25T10:00:00Z"
    }
]
```

#### PATCH — تحديث حالة مستخدم

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `user_id` | string | نعم | معرف المستخدم |
| `is_active` | boolean | لا | تنشيط/تعطيل |
| `is_verified` | boolean | لا | توثيق/إلغاء التوثيق |

**مثال:**

```json
PATCH /api/admin-panel/users/
{
    "user_id": "TR1234ABCD",
    "is_active": false
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم تحديث المستخدم بنجاح"
}
```

#### DELETE — حذف مستخدم

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `user_id` | string | نعم | معرف المستخدم |

**مثال:**

```json
DELETE /api/admin-panel/users/
{
    "user_id": "TR1234ABCD"
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم حذف المستخدم بنجاح"
}
```

---

### 7.3 إدارة المحتوى

```
GET    api/admin-panel/content/
PATCH  api/admin-panel/content/
DELETE api/admin-panel/content/
```

#### GET — عرض البلاغات

**استجابة ناجحة (200):**

```json
[
    {
        "id": 1,
        "reporter": { "full_name": "سارة علي" },
        "content_type": "post",
        "content_id": 5,
        "reason": "محتوى مخالف",
        "status": "pending",
        "created_at": "2026-07-25T10:00:00Z"
    }
]
```

#### PATCH — تحديث حالة البلاغ

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `report_id` | integer | نعم | معرف البلاغ |
| `status` | string | نعم | `reviewed` أو `approved` |

**مثال:**

```json
PATCH /api/admin-panel/content/
{
    "report_id": 1,
    "status": "approved"
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم تحديث حالة البلاغ"
}
```

#### DELETE — إزالة محتوى

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `report_id` | integer | نعم | معرف البلاغ |

**مثال:**

```json
DELETE /api/admin-panel/content/
{
    "report_id": 1
}
```

**استجابة ناجحة (200):**

```json
{
    "message": "تم إزالة المحتوى"
}
```

---

### 7.4 التقارير والإحصائيات

```
GET api/admin-panel/reports/
```

**استجابة ناجحة (200):**

```json
{
    "applications_by_status": {
        "pending": 30,
        "accepted": 50,
        "rejected": 20
    },
    "top_categories": [
        { "name": "تطوير الويب", "count": 25 },
        { "name": "تصميم الجرافيك", "count": 15 },
        { "name": "أمن المعلومات", "count": 10 },
        { "name": "إدارة الشبكات", "count": 8 },
        { "name": "تطوير تطبيقات الموبايل", "count": 5 }
    ],
    "total_users": 50,
    "total_internships": 20,
    "total_applications": 100
}
```

---

### 7.5 إيعاز متدرب

```
POST api/admin-panel/assign/
```

**الطلبات المطلوبة:**

| الحقل | النوع | مطلوب | الوصف |
|-------|-------|-------|-------|
| `trainee_id` | integer | نعم | معرف المتدرب |
| `supervisor_id` | integer | نعم | معرف المشرف |

**مثال:**

```json
POST /api/admin-panel/assign/
{
    "trainee_id": 1,
    "supervisor_id": 3
}
```

**استجابة ناجحة (201):**

```json
{
    "id": 1,
    "trainee": { "full_name": "سارة علي" },
    "supervisor": { "full_name": "خالد أحمد" },
    "status": "active",
    "message": "تم إيعاز المتدرب للمشرف بنجاح"
}
```

---

## ملخص نقاط النهاية

| القسم | عدد النقاط | الطريقة |
|-------|:----------:|---------|
| الحسابات (Accounts) | 11 | POST (9), GET (1), PUT (1) |
| فرص التدريب (Internships) | 9 | GET (4), POST (2), PATCH (1), PATCH+DELETE (2) |
| الرسائل (Messaging) | 6 | GET (3), POST (2), PATCH (1) |
| المجتمع (Community) | 7 | GET (3), POST (3), DELETE (1) |
| الأداء (Performance) | 7 | GET (4), POST (3) |
| الذكاء الاصطناعي (AI) | 3 | POST (1), GET (2) |
| لوحة التحكم (Admin) | 9 | GET (3), PATCH (2), DELETE (2), POST (1) |
| **المجموع** | **52** | **19 GET, 20 POST, 4 PATCH, 2 PUT, 5 DELETE** |

