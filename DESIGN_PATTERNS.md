# أنماط التصميم المستخدمة في مشروع TrainLink

---

## 1. نمط Singleton (المفردة)

### الغرض
ضمان وجود نسخة واحدة فقط من إعدادات النظام تُستخدم من جميع الأجزاء.

### سبب الاختيار
نحتاج أن جميع التطبيقات السبعة (accounts, internships, ai_engine, messaging, community, performance, admin_panel) تستخدم نفس الإعدادات: قاعدة البيانات، مفتاح الأمان، إعدادات البريد الإلكتروني، ومفتاح Gemini API. لو كانت هناك عدة نسخ من الإعدادات، قد تختلف بين التطبيقات ويحدث خطأ.

### التنفيذ
يتم تطبيقه عبر ملف `settings.py` في Django:

```python
# backend/trainlink/settings.py

from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# مفتاح الأمان — نسخة واحدة لكل النظام
SECRET_KEY = config('SECRET_KEY', default='django-insecure-...')

# قاعدة البيانات — اتصال واحد
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# نموذج المستخدم الوحيد
AUTH_USER_MODEL = 'accounts.Person'

# مفاتيح الخدمات الخارجية
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
```

**كيف يعمل:** Django يقرأ الملف مرة واحدة عند التشغيل، ويخزن المتغيرات ككائن واحد. أي ملف في النظام يستخدمه عبر:
```python
from django.conf import settings
# settings.SECRET_KEY — دائماً نفس الكائن
```

---

## 2. نمط Factory (مصنع)

### الغرض
إنشاء مستخدمين بأنواع مختلفة (متدرب، شركة، مشرف) بنفس هيكل التسجيل لكن بمخرجات مختلفة.

### سبب الاختيار
كل نوع مستخدم يحتاج:
- إنشاء حساب `Person` بنوع مختلف
- إنشاء ملف تعريف خاص (Trainee أو CompanyProfile أو SupervisorProfile)
- إرسال OTP تلقائي

لو كنا نكتب كل هذا في دالة واحدة، ستكون دالة ضخمة ومعقدة. النمط Factory يفصل كل نوع في مكانه.

### التنفيذ

```python
# backend/accounts/views.py

class RegisterTraineeView(APIView):
    def post(self, request):
        serializer = RegisterTraineeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # ← يستدعي create() الخاص بمتدرب

class RegisterCompanyView(APIView):
    def post(self, request):
        serializer = RegisterCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # ← يستدعي create() الخاص بشركة

class RegisterSupervisorView(APIView):
    def post(self, request):
        serializer = RegisterSupervisorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # ← يستدعي create() الخاص بمشرف
```

كل مسلسل (serializer) يحتوي على دالة `create()` تنشئ كائناً مختلفاً:

```python
# backend/accounts/serializers.py

# مصنع المتدرب
class RegisterTraineeSerializer:
    def create(self, validated_data):
        person = Person(person_type='trainee', ...)   # نوع: متدرب
        person.save()
        trainee = Trainee.objects.create(              # ملف: Trainee
            person=person, university=..., major=...
        )
        OTPVerification.objects.create(person=person, ...)  # OTP
        return person

# مصنع الشركة
class RegisterCompanySerializer:
    def create(self, validated_data):
        person = Person(person_type='company', ...)    # نوع: شركة
        person.save()
        CompanyProfile.objects.create(                 # ملف: CompanyProfile
            person=person, company_name=...
        )
        OTPVerification.objects.create(person=person, ...)
        return person

# مصنع المشرف
class RegisterSupervisorSerializer:
    def create(self, validated_data):
        person = Person(person_type='supervisor', ...) # نوع: مشرف
        person.save()
        SupervisorProfile.objects.create(              # ملف: SupervisorProfile
            person=person, department=...
        )
        OTPVerification.objects.create(person=person, ...)
        return person
```

---

## 3. نمط Observer (مراقب)

### الغرض
إرسال إشعارات تلقائية لأطراف متعددين عند حدوث تغيير في حالة معينة.

### سبب الاختيار
عندما يحدث تغيير في النظام (إرسال رسالة، تعيين متدرب لمشرف، قبول طلب)، يجب إشعار كل الأطراف المتأثرين. بدون هذا النمط، سنحتاج كتابة كود الإشعار يدوياً في كل مكان، وهذا يزيد الاحتمال الخطأ ويصعب الصيانة.

### التنفيذ

```python
# backend/messaging/views.py — عند إرسال رسالة

class MessageView(APIView):
    def post(self, request, channel_id):
        # 1. تغيير الحالة: إنشاء رسالة جديدة
        msg = Message.objects.create(
            channel=channel, sender=user,
            content=request.data.get('content', ''),
        )

        # 2. المراقب: إشعار كل المشاركين الآخرين
        recipients = channel.participants.exclude(id=user.id)
        for r in recipients:
            Notification.objects.create(
                user=r,
                notification_type='message',
                title='رسالة جديدة',
                message=f'رسالة جديدة من {user.full_name}',
                link=f'/chat/{channel_id}',
            )
```

```python
# backend/admin_panel/views.py — عند إيعاز متدرب لمشرف

class AssignTraineeView(APIView):
    def post(self, request):
        # 1. تغيير الحالة: إنشاء إشراف جديد
        assignment = SupervisionAssignment.objects.create(
            supervisor=supervisor, trainee=trainee,
        )

        # 2. المراقب: إشعار المتدرب
        Notification.objects.create(
            user=trainee.person,
            notification_type='system',
            title='تم تعيين مشرف لك',
            message=f'تم تعيين المشرف {supervisor.person.full_name}',
        )

        # 3. المراقب: إشعار المشرف
        Notification.objects.create(
            user=supervisor.person,
            notification_type='system',
            title='تم تعيين متدرب لك',
            message=f'تم تعيين المتدرب {trainee.person.full_name}',
        )
```

```python
# backend/messaging/models.py — نموذج الإشعار (المراقب)

class Notification(models.Model):
    user = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=[
        ('application', 'طلب تقديم'),
        ('message', 'رسالة'),
        ('report', 'تقرير'),
        ('alert', 'تنبيه'),
        ('system', 'نظام'),
    ])
    title = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
```

---

## 4. نمط Strategy (استراتيجية)

### الغرض
تنفيذ خوارزميات مختلفة لتحليل السيرة الذاتية والتبديل بينها وقت التشغيل حسب التوفر.

### سبب الاختيار
نظام التحليل يعمل بطريقتين:
- **Gemini API:** تحليل ذكي بالذكاء الاصطناعي (أفضل نتيجة لكن يحتاج مفتاح API واتصال إنترنت)
- **تحليل يدوي (Fallback):** قواعد حسابية بسيطة (يعمل دائماً بدون إنترنت)

يجب أن يُرجع كلتاهما نفس شكل النتيجة حتى لا تتأثر الواجهة. لو انتهى مفتاح Gemini، النظام يتحول تلقائياً للتحليل اليدوي بدون أن يشعر المستخدم.

### التنفيذ

```python
# backend/ai_engine/views.py

class CVUploadView(APIView):
    def analyze_cv(self, cv, user):
        gemini_key = getattr(settings, 'GEMINI_API_KEY', '')

        # الاستراتيجية الأولى: Gemini AI
        if gemini_key:
            try:
                client = genai.Client(api_key=gemini_key)
                prompt = f"""حلل السيرة الذاتية وقدم تقييماً شاملاً...
                أعد النتيجة بالصيغة التالية (JSON):
                {{"overall_score": رقم, "sections": {{...}},
                  "suggestions": [...], "strengths": [...], "weaknesses": [...]}}"""

                response = client.models.generate_content(
                    model='gemini-2.0-flash', contents=prompt,
                )
                return json.loads(response.text)   # ← نتيجة Gemini
            except:
                pass  # ← فشل Gemini، ننتقل للتالية

        # الاستراتيجية الثانية: تحليل يدوي (Fallback)
        return self.get_fallback_analysis(user)

    def get_fallback_analysis(self, user):
        # قواعد حسابية بسيطة
        trainee = user.trainee_profile
        edu_score = 80 if trainee.gpa >= 3.0 else 65 if trainee.gpa >= 2.5 else 50
        skills_score = 60 if trainee.major else 50
        overall = round((edu_score + 45 + skills_score + 75) / 4)

        return {
            'overall_score': overall,
            'sections': { ... },           # ← نفس شكل نتيجة Gemini
            'suggestions': ['أضف خبرات عملية...'],
            'strengths': ['...'],
            'weaknesses': ['...'],
        }
```

**الalkresult:** كلا الاستراتيجيتين تُرجع نفس الهيكل (`overall_score`, `sections`, `suggestions`, `strengths`, `weaknesses`). الواجهة لا تعرف أيهما استُخدمت.

---

## 5. نمط MVC (Model-View-Controller)

### الغرض
فصل النظام إلى ثلاث طبقات مستقلة: البيانات، المنطق، العرض.

### سبب الاختيار
- **سهولة الصيانة:** تعديل شكل الصفحة لا يؤثر على قاعدة البيانات
- **سهولة التعاون:** مطور الواجهة يعمل على HTML/CSS، ومطور الخادم يعمل على Python
- **إعادة الاستخدام:** نفس الـ API تُستخدم للويب والموبايل

### التنفيذ

**الطبقة الأولى — Model (البيانات):**

```python
# backend/internships/models.py

class Internship(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=300)
    description = models.TextField()
    deadline = models.DateField()
    status = models.CharField(max_length=20, default='open')

    def update_acceptance_rate(self):       # ← منطق أعمال متعلق بالبيانات
        total = self.applications.count()
        accepted = self.applications.filter(status='accepted').count()
        self.acceptance_rate = (accepted / total * 100) if total > 0 else 0
        self.save()
```

**الطبقة الثانية — View/Controller (منطق الأعمال):**

```python
# backend/internships/views.py

class InternshipListView(APIView):
    def get(self, request):                 # ← يستقبل طلب HTTP
        search = request.query_params.get('search', '')
        qs = Internship.objects.filter(status='open')  # ← يستعلم من Model
        if search:
            qs = qs.filter(title__icontains=search)
        return Response(data)               # ← يُرجع استجابة JSON

    def post(self, request):                # ← يستقبل طلب إنشاء
        internship = Internship.objects.create(  # ← ينشئ في Model
            company=company, title=..., ...
        )
        return Response({'id': internship.id}, status=201)
```

**الطبقة الثالثة — Template/View (العرض):**

```html
<!-- frontend/pages/trainee/08-trainee-dashboard.html -->

<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <title>TrainLink — لوحة تحكم المتدرب</title>
    <style>
        :root { --primary: #5B4FCF; }
        .sidebar { background: #1E1B2E; }
        /* ... أنماط العرض فقط ... */
    </style>
</head>
<body>
    <!-- شريط جانبي، بطاقات إحصائية، محتوى الصفحة -->
    <!-- يجلب البيانات من API عبر JavaScript -->
    <script>
        fetch('/api/internships/')
            .then(res => res.json())
            .then(data => renderInternships(data));
    </script>
</body>
</html>
```

---

## ملخص الأنماط

| # | النمط | الغرض الرئيسي | الملفات الرئيسية |
|---|-------|--------------|-----------------|
| 1 | Singleton | نسخة إعدادات واحدة للنظام كله | `trainlink/settings.py` |
| 2 | Factory | إنشاء مستخدمين بأنواع مختلفة | `accounts/views.py` + `serializers.py` |
| 3 | Observer | إشعارات تلقائية عند تغيير الحالة | `messaging/views.py` + `admin_panel/views.py` |
| 4 | Strategy | تحليل CV بطرق مختلفة مع fallback | `ai_engine/views.py` |
| 5 | MVC | فصل البيانات عن المنطق عن العرض | `models.py` + `views.py` + `*.html` |

---

**المشروع:** TrainLink — منصة البحث عن فرص التدريب
**المجامعة:** جامعة الأقصى — غزة
**المقرر:** هندسة البرمجيات
**المشرف:** المهندس فراس العجلة
**المطورة:** رولا سهيل أبو الدهن
