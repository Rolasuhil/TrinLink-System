# ملف واجهات برمجة التطبيقات لمحرك الذكاء الاصطناعي
# يحتوي على منطق رفع وتحليل السير الذاتية والمطابقة الذكية للمتدربين بالفرص التدريبية

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AIMatchingResult, CVAnalysis
from accounts.models import CV, Trainee, Person
from internships.models import Internship
from messaging.models import Notification
from django.conf import settings
import jwt
import json


def get_user(request):
    """دالة مساعدة لاستخراج بيانات المستخدم من رمز JWT في طلب التصريح
    ترجع كائن الشخص إذا كان الرمز صالحاً، أو None إذا لم يكن كذلك
    """
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    try:
        payload = jwt.decode(auth.split(' ')[1], settings.SECRET_KEY, algorithms=['HS256'])
        return Person.objects.get(user_id=payload['user_id'])
    except Exception:
        return None


class CVUploadView(APIView):
    """واجهة رفع وتحليل السيرة الذاتية
    تسمح للمتدربين برفع ملف سيرتهم الذاتية وتحليلها بالذكاء الاصطناعي
    """

    def post(self, request):
        """معالجة طلب رفع السيرة الذاتية
        - التحقق من صلاحية المستخدم (متدرب فقط)
        - التحقق من وجود الملف وصيغته (PDF أو Word) وحجمه (أقصاه 5MB)
        - إنشاء سجل السيرة الذاتية في قاعدة البيانات
        - تحليل السيرة الذاتية بالذكاء الاصطناعي
        - حفظ نتائج التحليل في نموذج CVAnalysis
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        cv_file = request.FILES.get('cv')
        if not cv_file:
            return Response({'error': 'يرجى رفع ملف السيرة الذاتية'}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من صيغة الملف المدعومة
        allowed = ['.pdf', '.doc', '.docx']
        ext = '.' + cv_file.name.rsplit('.', 1)[-1].lower() if '.' in cv_file.name else ''
        if ext not in allowed:
            return Response({'error': 'صيغة الملف غير مدعومة. يرجى استخدام PDF أو Word'}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من حجم الملف (الحد الأقصى 5 ميجابايت)
        if cv_file.size > 5 * 1024 * 1024:
            return Response({'error': 'حجم الملف يتجاوز 5MB'}, status=status.HTTP_400_BAD_REQUEST)

        # إنشاء سجل السيرة الذاتية في قاعدة البيانات
        cv = CV.objects.create(
            trainee=user.trainee_profile,
            file=cv_file,
            file_path=cv_file.name,
        )

        # تحليل السيرة الذاتية بالذكاء الاصطناعي وحفظ النتائج
        analysis = self.analyze_cv(cv, user)
        cv.ai_analysis = analysis
        cv.ai_score = analysis.get('overall_score', 0)
        cv.save()

        # إنشاء سجل تحليل السيرة الذاتية بالتفصيل
        CVAnalysis.objects.create(
            cv=cv,
            overall_score=analysis.get('overall_score', 0),
            sections_score=analysis.get('sections', {}),
            suggestions=analysis.get('suggestions', []),
            strengths=analysis.get('strengths', []),
            weaknesses=analysis.get('weaknesses', []),
            raw_analysis=json.dumps(analysis, ensure_ascii=False),
        )

        return Response({
            'message': 'تم رفع وتحليل السيرة الذاتية بنجاح',
            'cv_id': cv.id,
            'analysis': analysis,
        }, status=status.HTTP_201_CREATED)

    def analyze_cv(self, cv, user):
        """تحليل السيرة الذاتية باستخدام Google Gemini AI
        يرسل معلومات المتدرب وprompt متخصص إلى Gemini ويستخرج تقييماً شاملاً
        يرجع قاموساً بالنتيجة يشمل التقييم العام والتقييمات الفرعية والاقتراحات
        """
        gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
        if gemini_key:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=gemini_key)
                trainee = user.trainee_profile
                # بناء الطلب (prompt) لتحليل السيرة الذاتية بالعربية
                prompt = f"""أنت خبير في تحليل السيرة الذاتية لطلاب التدريب في فلسطين.
حلل السيرة الذاتية وقدم تقييماً شاملاً.

معلومات المتدرب:
- الاسم: {user.full_name}
- التخصص: {trainee.major or 'غير محدد'}
- الجامعة: {trainee.university or 'غير محدد'}
- المعدل: {trainee.gpa or 'غير محدد'}

أعد النتيجة بالصيغة التالية فقط (JSON فقط، بدون أي نص إضافي):
{{
  "overall_score": رقم من 0 إلى 100,
  "sections": {{
    "education": {{"score": رقم, "comment": "تعليق بالعربي"}},
    "experience": {{"score": رقم, "comment": "تعليق بالعربي"}},
    "skills": {{"score": رقم, "comment": "تعليق بالعربي"}},
    "format": {{"score": رقم, "comment": "تعليق بالعربي"}}
  }},
  "suggestions": ["اقتراح 1", "اقتراح 2", "اقتراح 3"],
  "strengths": ["نقطة قوة 1", "نقطة قوة 2"],
  "weaknesses": ["نقطة ضعف 1", "نقطة ضعف 2"]
}}"""
                # إرسال الطلب إلى Gemini واستخراج النتيجة
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt,
                )
                text = response.text.strip()
                # إزالة علامات الكود البرمجي إذا وُجدت في الاستجابة
                if text.startswith('```'):
                    text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
                return json.loads(text)
            except Exception as e:
                pass

        # استخدام التحليل الاحتياطي إذا فشل الاتصال بـ Gemini
        return self.get_fallback_analysis(user)

    def get_fallback_analysis(self, user):
        """تحليل احتياطي للسيرة الذاتية بدون استخدام الذكاء الاصطناعي
        يعتمد فقط على بيانات المتدرب (المعدل والتخصص) لإعطاء تقييم تقريبي
        """
        trainee = getattr(user, 'trainee_profile', None)
        major = trainee.major if trainee else ''
        gpa = trainee.gpa if trainee else 0

        # حساب درجات الأقسام بناءً على المعدل والتخصص
        edu_score = 80 if gpa and gpa >= 3.0 else 65 if gpa and gpa >= 2.5 else 50
        exp_score = 45
        skills_score = 60 if major else 50
        fmt_score = 75

        overall = round((edu_score + exp_score + skills_score + fmt_score) / 4)

        # اقتراحات عامة لتحسين السيرة الذاتية
        suggestions = [
            'أضف خبرات تطوعية أو مشاريع عملية تثبت مهاراتك',
            'حسّن المهارات التقنية وحدد مستويات إتقان كل أداة',
            'أضف شهادات مهنية أو دورات تدريبية مكتملة',
            'استخدم كلمات مفتاحية من وصف الوظيفة المستهدفة',
            'أضف رابط GitHub أو Portfolio لعرض أعمالك',
        ]

        # تحديد نقاط القوة بناءً على البيانات المتاحة
        strengths = []
        if gpa and gpa >= 3.0:
            strengths.append('معدل تراكمي ممتاز')
        if major:
            strengths.append(f'تخصص {major} موثق')
        strengths.extend(['التنسيق الأساسي جيد', 'المعلومات الشخصية موجودة'])

        # تحديد نقاط الضعف
        weaknesses = []
        if exp_score < 60:
            weaknesses.append('يحتاج إلى خبرات عملية أكثر')
        weaknesses.extend(['لا توجد شهادات مهنية مدرجة', 'يجب تضمين روابط أعمال سابقة'])

        return {
            'overall_score': overall,
            'sections': {
                'education': {'score': edu_score, 'comment': 'التعليم جيد' if edu_score >= 70 else 'يحتاج تحسين'},
                'experience': {'score': exp_score, 'comment': 'يحتاج المزيد من الخبرات العملية'},
                'skills': {'score': skills_score, 'comment': 'المهارات مقبولة لكن يمكن تحسينها'},
                'format': {'score': fmt_score, 'comment': 'التنسيق جيد'},
            },
            'suggestions': suggestions,
            'strengths': strengths,
            'weaknesses': weaknesses,
        }


class AIMatchView(APIView):
    """واجهة المطابقة الذكية للمتدربين بالفرص التدريبية
    تحسب نسبة توافق كل متدرب مع كل فرصة تدريبية مفتوحة
    """

    def get(self, request):
        """جلب أفضل فرص التدريب المتوافقة مع المتدرب
        - التحقق من صلاحية المستخدم (متدرب فقط)
        - حساب نسبة المطابقة مع كل فرصة مفتوحة
        - تصفية الفرص ذات النسبة العالية (أكثر من 30%)
        - ترتيب النتائج وعرض أعلى 10 فرص
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        trainee = user.trainee_profile
        internships = Internship.objects.filter(status='open')

        matches = []
        for internship in internships:
            score = self.calculate_match(trainee, internship)
            # فقط الفرص التي نسبة مطابقتها أكثر من 30%
            if score > 30:
                matches.append({
                    'internship_id': internship.id,
                    'title': internship.title,
                    'company': internship.company.company_name,
                    'company_initials': internship.company.company_name[:2],
                    'category': internship.category.name if internship.category else '',
                    'location': internship.location,
                    'internship_type': internship.internship_type,
                    'duration': internship.duration,
                    'is_paid': internship.is_paid,
                    'salary': internship.salary if internship.is_paid else 0,
                    'match_score': score,
                    'reason': self.get_match_reason(trainee, internship, score),
                })

        # ترتيب النتائج من أعلى نسبة مطابقة إلى أقلها
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return Response({'matches': matches[:10]})

    def calculate_match(self, trainee, internship):
        """حساب نسبة مطابقة المتدرب مع فرصة تدريبية معينة
        تبدأ من 50% وتزداد بناءً على: تطابق التخصص، المعدل التراكمي، الجامعة، ونوع الفرصة
        """
        score = 50
        # مكافأة تطابق التخصص مع فئة الفرصة
        if trainee.major and internship.category:
            if trainee.major.lower() in internship.category.name.lower() or internship.category.name.lower() in trainee.major.lower():
                score += 25
        # مكافأة المعدل التراكمي العالي
        if trainee.gpa and trainee.gpa >= 3.0:
            score += 10
        elif trainee.gpa and trainee.gpa >= 2.5:
            score += 5
        # مكافأة وجود الجامعة
        if trainee.university:
            score += 5
        # مكافأة الفرصة عن بُعد
        if internship.internship_type == 'remote':
            score += 5
        return min(score, 98)

    def get_match_reason(self, trainee, internship, score):
        """توليد سبب المطابقة بناءً على تفاصيل المتدرب والفرصة
        ترجع نصاً يشرح لماذا هذه الفرصة مناسبة للمتدرب
        """
        reasons = []
        if trainee.major and internship.category:
            if trainee.major.lower() in internship.category.name.lower():
                reasons.append('مطابقة في التخصص')
        if trainee.gpa and trainee.gpa >= 3.0:
            reasons.append('معدل تراكمي ممتاز')
        if score >= 80:
            reasons.append('فرصة مثالية لملفك الشخصي')
        elif score >= 60:
            reasons.append('فرصة مناسبة لمهاراتك')
        return ' | '.join(reasons) if reasons else 'مطابقة عامة'


class CVAnalysisListView(APIView):
    """واجهة جلب قائمة تحليلات السير الذاتية
    ترجع جميع تحليلات السير الذاتية للمتدرب المسجل
    """

    def get(self, request):
        """جلب جميع تحليلات السير الذاتية للمتدرب
        ترجع قائمة بجميع التحليلات مع التقييمات والاقتراحات
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        analyses = CVAnalysis.objects.filter(cv__trainee=user.trainee_profile)
        data = [{
            'id': a.id,
            'cv_id': a.cv.id,
            'overall_score': a.overall_score,
            'sections': a.sections_score,
            'suggestions': a.suggestions,
            'strengths': a.strengths,
            'weaknesses': a.weaknesses,
            'created_at': str(a.created_at),
        } for a in analyses]
        return Response(data)
