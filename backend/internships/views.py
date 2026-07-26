"""
دوال API للتدريب والتقديمات
- عرض ونشر فرص التدريب (القائمة والتفاصيل والتعديل والحذف)
- عرض وإنشاء وتحديث طلبات التقديم
- إدارة الفopport المحفوظة من قبل المتدربين
- عرض التصنيفات المتاحة
- حساب نسبة التطابق بين مهارات المتدرب ومتطلبات الفرصة
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Internship, Category, Application, SavedInternship, AcceptedTrainee
from django.conf import settings
import jwt


# ──────────────────────────────────────────────
# دالة مساعدة: استخراج المستخدم من رمز JWT
# ──────────────────────────────────────────────
def get_user(request):
    """تقوم بقراءة رمز JWT من ترويسة Authorization واستخراج بيانات المستخدم المصادق عليه"""
    auth = request.headers.get('Authorization', '')  # جلب ترويسة المصادقة
    if not auth.startswith('Bearer '):
        return None  # الترويسة غير صالحة
    try:
        # فك تشفير الرمز باستخدام المفتاح السري
        payload = jwt.decode(auth.split(' ')[1], settings.SECRET_KEY, algorithms=['HS256'])
        from accounts.models import Person
        # جلب المستخدم من قاعدة البيانات بناءً على user_id الموجود في الرمز
        return Person.objects.get(user_id=payload['user_id'])
    except Exception:
        return None  # فشل فك التشفير أو المستخدم غير موجود


# ══════════════════════════════════════════════════════════════
# عرض ونشر فرص التدريب
# ══════════════════════════════════════════════════════════════
class InternshipListView(APIView):
    """عرض جميع فرص التدريب المفتوحة مع إمكانية التصفية، ونشر فرصة جديدة من قبل الشركة"""

    def get(self, request):
        """جلب جميع فرص التدريب المفتوحة مع دعم عوامل التصفية (بحث بالاسم، التصنيف، الموقع، النوع، الحالة المدفوعة)"""
        # قراءة معايير البحث من رابط الطلبة (query parameters)
        search = request.query_params.get('search', '')
        category = request.query_params.get('category', '')
        location = request.query_params.get('location', '')
        internship_type = request.query_params.get('type', '')

        # البدء بجلب الفرص المفتوحة فقط
        qs = Internship.objects.filter(status='open')

        # تطبيق عوامل التصفية بناءً على المعايير المطلوبة
        if search:
            qs = qs.filter(title__icontains=search)  # بحث جزئي في العنوان
        if category:
            qs = qs.filter(category__id=category)  # تصفية حسب التصنيف
        if location:
            qs = qs.filter(location__icontains=search)  # تصفية حسب الموقع
        if internship_type:
            qs = qs.filter(internship_type=internship_type)  # تصفية حسب النوع

        # تصفية حسب حالة الدفع (مدفوع أو مجاني)
        is_paid = request.query_params.get('is_paid', '')
        if is_paid == 'true':
            qs = qs.filter(is_paid=True)
        elif is_paid == 'false':
            qs = qs.filter(is_paid=False)

        # تحويل بيانات الفرص إلى قائمة قاموسية للإرجاع كاستجابة JSON
        data = []
        for i in qs:
            data.append({
                'id': i.id,
                'title': i.title,
                'company': i.company.company_name,
                'company_logo': i.company.logo.url if i.company.logo else None,
                'category': i.category.name if i.category else '',
                'description': i.description,
                'requirements': i.requirements,
                'location': i.location,
                'internship_type': i.get_internship_type_display(),  # اسم النوع بالعربية
                'start_date': str(i.start_date),
                'end_date': str(i.end_date),
                'deadline': str(i.deadline),
                'available_positions': i.available_positions,
                'acceptance_rate': i.acceptance_rate,
                'is_paid': i.is_paid,
                'learning_outcomes': i.learning_outcomes,
                'additional_skills': i.additional_skills,
                'has_certificate': i.has_certificate,
                'work_days': i.work_days,
                'created_at': str(i.created_at),
            })
        return Response(data)

    def post(self, request):
        """نشر فرصة تدريب جديدة من قبل شركة مصرح لها (يتطلب مصادقة JWT ونوع مستخدم 'company')"""
        # التحقق من هوية المستخدم وصلاحيته
        user = get_user(request)
        if not user or user.person_type != 'company':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        # جلب ملف الشركة المرتبط بالمستخدم
        try:
            company = user.company_profile
        except Exception:
            return Response({'error': 'الملف الشخصي للشركة غير موجود'}, status=status.HTTP_400_BAD_REQUEST)

        # جلب التصنيف المحدد إن وُجد
        category = None
        if request.data.get('category_id'):
            try:
                category = Category.objects.get(id=request.data['category_id'])
            except Category.DoesNotExist:
                pass  # إذا لم يُوجد التصنيف، تُترك الفرصة بدون تصنيف

        # إنشاء سجل فرصة التدريب الجديدة بالبيانات المرسلة
        internship = Internship.objects.create(
            company=company,
            category=category,
            title=request.data.get('title', ''),
            description=request.data.get('description', ''),
            requirements=request.data.get('requirements', ''),
            deadline=request.data.get('deadline'),
            available_positions=request.data.get('available_positions', 1),
            location=request.data.get('location', ''),
            internship_type=request.data.get('internship_type', 'onsite'),
            start_date=request.data.get('start_date'),
            end_date=request.data.get('end_date'),
            is_paid=request.data.get('is_paid', False),
            learning_outcomes=request.data.get('learning_outcomes', ''),
            additional_skills=request.data.get('additional_skills', ''),
            has_certificate=request.data.get('has_certificate', False),
            work_days=request.data.get('work_days', ''),
        )
        return Response({'message': 'تم نشر الفرصة بنجاح', 'id': internship.id}, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════
# تفاصيل فرصة تدريب محددة: جلب وتعديل وحذف
# ══════════════════════════════════════════════════════════════
class InternshipDetailView(APIView):
    """عرض تفاصيل فرصة تدريب محددة، وتعديلها أو حذفها من قبل الشركة المالكة"""

    def get(self, request, pk):
        """جلب جميع تفاصيل فرصة تدريب محددة بواسطة معرفها (pk)"""
        try:
            i = Internship.objects.get(id=pk)
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        # إرجاع جميع تفاصيل الفرصة مع معلومات الشركة المرتبطة
        return Response({
            'id': i.id,
            'title': i.title,
            'company': i.company.company_name,
            'company_id': i.company.id,
            'company_industry': i.company.industry or '',  # مجال صناعة الشركة
            'company_size': i.company.company_size or '',  # حجم الشركة
            'company_location': i.company.location or '',  # موقع الشركة
            'company_about': i.company.about or '',  # نبذة عن الشركة
            'category': i.category.id if i.category else None,
            'category_name': i.category.name if i.category else '',
            'description': i.description,
            'requirements': i.requirements,
            'location': i.location,
            'internship_type': i.internship_type,
            'internship_type_display': i.get_internship_type_display(),
            'start_date': str(i.start_date),
            'end_date': str(i.end_date),
            'deadline': str(i.deadline),
            'available_positions': i.available_positions,
            'acceptance_rate': i.acceptance_rate,
            'is_paid': i.is_paid,
            'learning_outcomes': i.learning_outcomes,
            'additional_skills': i.additional_skills,
            'has_certificate': i.has_certificate,
            'work_days': i.work_days,
            'status': i.status,
        })

    def put(self, request, pk):
        """تعديل بيانات فرصة تدريب موجودة - متاح فقط للشركة المالكة للفرصة"""
        # التحقق من صلاحية المستخدم
        user = get_user(request)
        if not user or user.person_type != 'company':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        # التأكد من أن الفرصة تابعة للشركة الحالية
        try:
            i = Internship.objects.get(id=pk, company=user.company_profile)
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة أو ليس لديك صلاحية'}, status=status.HTTP_404_NOT_FOUND)

        # تحديث التصنيف إذا تم تمرير معرف جديد
        category = i.category
        if request.data.get('category_id'):
            try:
                category = Category.objects.get(id=request.data['category_id'])
            except Category.DoesNotExist:
                pass

        # تحديث جميع الحقول بقيم جديدة أو الاحتفاظ بالقيم الحالية إذا لم تُرسل
        i.title = request.data.get('title', i.title)
        i.description = request.data.get('description', i.description)
        i.requirements = request.data.get('requirements', i.requirements)
        i.location = request.data.get('location', i.location)
        i.internship_type = request.data.get('internship_type', i.internship_type)
        i.category = category
        i.start_date = request.data.get('start_date', i.start_date)
        i.end_date = request.data.get('end_date', i.end_date)
        i.deadline = request.data.get('deadline', i.deadline)
        i.available_positions = request.data.get('available_positions', i.available_positions)
        i.is_paid = request.data.get('is_paid', i.is_paid)
        i.learning_outcomes = request.data.get('learning_outcomes', i.learning_outcomes)
        i.additional_skills = request.data.get('additional_skills', i.additional_skills)
        i.has_certificate = request.data.get('has_certificate', i.has_certificate)
        i.work_days = request.data.get('work_days', i.work_days)
        i.status = request.data.get('status', i.status)
        i.save()
        return Response({'message': 'تم تحديث الفرصة بنجاح'})

    def delete(self, request, pk):
        """حذف فرصة تدريب - متاح فقط للشركة المالكة للفرصة"""
        # التحقق من صلاحية المستخدم
        user = get_user(request)
        if not user or user.person_type != 'company':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        # التأكد من أن الفرصة تابعة للشركة الحالية
        try:
            i = Internship.objects.get(id=pk, company=user.company_profile)
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة أو ليس لديك صلاحية'}, status=status.HTTP_404_NOT_FOUND)
        i.delete()
        return Response({'message': 'تم حذف الفرصة بنجاح'})


# ──────────────────────────────────────────────────────────
# دالة مساعدة: حساب نسبة التطابق بين المتدرب والفرصة
# ──────────────────────────────────────────────────────────
def calc_match_percentage(trainee, internship):
    """تحسب نسبة التطابق بين مهارات المتدرب ومتطلبات الفرصة
    - المتطلبات الإلزامية تحسب بوزن 70%
    - المهارات الإضافية تحسب بوزن 30%
    - تُرجع نسبة مئوية صحيحة (0-100)"""

    # استخراج مهارات المتدرب من ملفه الشخصي وتحويلها لمجموعة (set)
    trainee_skills = set()
    if hasattr(trainee, 'trainee_profile') and trainee.trainee_profile.skills:
        trainee_skills = {s.strip().lower() for s in trainee.trainee_profile.skills.split(',') if s.strip()}

    # استخراج المتطلبات الإلزامية من وصف الفرصة
    required = set()
    if internship.requirements:
        required = {s.strip().lower() for s in internship.requirements.split(',') if s.strip()}

    # استخراج المهارات الإضافية (المفضلة لكن غير الإلزامية)
    optional = set()
    if internship.additional_skills:
        optional = {s.strip().lower() for s in internship.additional_skills.split(',') if s.strip()}

    # دمج جميع المتطلبات معاً
    all_needed = required | optional
    if not all_needed:
        return 0  # لا توجد متطلبات = لا يوجد تطابق

    # حساب المهارات المتطابقة
    matched = trainee_skills & all_needed

    if not required:
        # إذا لا توجد متطلبات إلزامية، يُحسب النسبة من المهارات الإضافية فقط
        return round(len(matched) / len(all_needed) * 100) if all_needed else 0

    # حساب درجة المتطلبات الإلزامية (وزن 70%)
    matched_req = trainee_skills & required
    req_score = (len(matched_req) / len(required)) * 70 if required else 0

    # حساب درجة المهارات الإضافية (وزن 30%)
    opt_score = (len(matched & optional) / len(optional)) * 30 if optional else 0

    return round(req_score + opt_score)


# ══════════════════════════════════════════════════════════════
# عرض وإدارة طلبات التقديم
# ══════════════════════════════════════════════════════════════
class ApplicationListView(APIView):
    """عرض جميع طلبات التقديم للمتدرب أو الشركة، وإنشاء طلب تقديم جديد"""

    def get(self, request):
        """جلب طلبات التقديم حسب نوع المستخدم:
        - المتدرب: يرى طلباته الخاصة فقط
        - الشركة: ترى جميع الطلبات المقدمة على فرصها
        - يُحسب نسبة التطابق للمتدرب تلقائياً
        """
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        # تصفية الطلبات حسب نوع المستخدم
        if user.person_type == 'trainee':
            # المتدرب يرى طلباته الخاصة فقط
            apps = Application.objects.filter(trainee=user.trainee_profile)
        elif user.person_type == 'company':
            # الشركة ترى الطلبات المقدمة على فرصها فقط
            apps = Application.objects.filter(internship__company=user.company_profile)
        else:
            apps = Application.objects.none()  # لا توجد طلبات للأنواع الأخرى

        # تحويل الطلبات إلى قائمة قاموسية مع معلومات تفصيلية
        data = []
        for a in apps:
            # حساب نسبة التطابق فقط إذا كان المستخدم متدرباً
            match = calc_match_percentage(a.trainee.person, a.internship) if user.person_type == 'trainee' else 0
            data.append({
                'id': a.id,
                'internship_id': a.internship.id,
                'internship_title': a.internship.title,
                'company_name': a.internship.company.company_name,
                'company_id': a.internship.company.id,
                'trainee_name': a.trainee.person.full_name,
                'status': a.status,
                'status_display': a.get_status_display(),
                'application_date': str(a.application_date),
                'rejection_reason': a.rejection_reason,
                'location': a.internship.location,
                'internship_type': a.internship.internship_type,
                'internship_type_display': a.internship.get_internship_type_display(),
                'is_paid': a.internship.is_paid,
                'work_days': a.internship.work_days,
                'available_positions': a.internship.available_positions,
                'has_certificate': a.internship.has_certificate,
                'deadline': str(a.internship.deadline),
                'match_percentage': match,
            })
        return Response(data)

    def post(self, request):
        """تقديم طلب تدريب جديد على فرصة محددة - متاح فقط للمتدربين
        - يتحقق من عدم تكرار التقديم لنفس الفرصة
        - يدعم رفع ملف السيرة الذاتية ورسالة التقديم
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        # البحث عن الفرصة المطلوبة
        try:
            internship = Internship.objects.get(id=request.data.get('internship_id'))
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        # التحقق من عدم تقديم مسبق على نفس الفرصة
        if Application.objects.filter(internship=internship, trainee=user.trainee_profile).exists():
            return Response({'error': 'لقد قدمت على هذه الفرصة مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)

        # جلب رسالة التقديم وملف السيرة الذاتية
        cover_letter = request.data.get('cover_letter', '')
        resume_version = ''
        if 'resume' in request.FILES:
            resume_file = request.FILES['resume']
            resume_version = resume_file.name  # حفظ اسم الملف فقط

        # إنشاء سجل طلب التقديم
        app = Application.objects.create(
            internship=internship,
            trainee=user.trainee_profile,
            resume_version=resume_version,
            cover_letter=cover_letter,
        )
        return Response({'message': 'تم التقديم بنجاح', 'id': app.id}, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════
# تفاصيل طلب تقديم محدد: جلب وتحديث الحالة
# ══════════════════════════════════════════════════════════════
class ApplicationDetailView(APIView):
    """عرض تفاصيل طلب تقديم محدد وتحديث حالته (قبول/رفض/سحب)"""

    def get(self, request, pk):
        """جلب تفاصيل طلب تقديم محدد بناءً على نوع المستخدم:
        - المتدرب يرى طلبه الخاص فقط
        - الشركة ترى الطلبات المقدمة على فرصها فقط
        """
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            if user.person_type == 'trainee':
                # المتدرب يرى طلبه فقط
                app = Application.objects.get(id=pk, trainee=user.trainee_profile)
            elif user.person_type == 'company':
                # الشركة ترى الطلبات المقدمة على فرصها فقط
                app = Application.objects.get(id=pk, internship__company=user.company_profile)
            else:
                return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        except Application.DoesNotExist:
            return Response({'error': 'الطلب غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        # إرجاع تفاصيل الطلب
        return Response({
            'id': app.id,
            'internship_title': app.internship.title,
            'trainee_name': app.trainee.person.full_name,
            'status': app.status,
            'status_display': app.get_status_display(),
            'application_date': str(app.application_date),
            'rejection_reason': app.rejection_reason,
            'cover_letter': app.cover_letter,
        })

    def patch(self, request, pk):
        """تحديث حالة طلب التقديم:
        - الشركة يمكنها قبول أو رفض الطلب
        - المتدرب يمكنه سحب طلبه
        - يُحدّث نسبة القبول تلقائياً بعد أي تغيير
        """
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        new_status = request.data.get('status')

        if user.person_type == 'company':
            # الشركة تراجع الطلب: قبول أو رفض
            try:
                app = Application.objects.get(id=pk, internship__company=user.company_profile)
            except Application.DoesNotExist:
                return Response({'error': 'الطلب غير موجود'}, status=status.HTTP_404_NOT_FOUND)
            if new_status in ['accepted', 'rejected']:
                app.status = new_status
                app.rejection_reason = request.data.get('rejection_reason', '')  # سبب الرفض (إن وُجد)
                app.save()
                # تحديث نسبة القبول في الفرصة بعد تغيير حالة الطلب
                app.internship.update_acceptance_rate()
            return Response({'message': 'تم تحديث الحالة بنجاح'})

        elif user.person_type == 'trainee':
            # المتدرب يمكنه سحب طلبه فقط
            try:
                app = Application.objects.get(id=pk, trainee=user.trainee_profile)
            except Application.DoesNotExist:
                return Response({'error': 'الطلب غير موجود'}, status=status.HTTP_404_NOT_FOUND)
            if new_status == 'withdrawn':
                app.status = 'withdrawn'
                app.save()
                # تحديث نسبة القبول بعد سحب الطلب
                app.internship.update_acceptance_rate()
            return Response({'message': 'تم تحديث الحالة بنجاح'})

        return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)


# ══════════════════════════════════════════════════════════════
# إدارة فرص التدريب المحفوظة
# ══════════════════════════════════════════════════════════════
class SavedInternshipView(APIView):
    """عرض وحفظ وإزالة فرص التدريب المحفوظة من قبل المتدرب"""

    def get(self, request):
        """جلب جميع فرص التدريب المحفوظة من قبل المتدرب المسجّل دخوله"""
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        # جلب جميع الفopport المحفوظة للمتدرب
        saved = SavedInternship.objects.filter(trainee=user.trainee_profile)
        data = [{'id': s.id, 'internship_id': s.internship.id, 'title': s.internship.title} for s in saved]
        return Response(data)

    def post(self, request):
        """حفظ فرصة تدريب أو إزالة حفظها (نظام التبديل: toggle)
        - إذا كانت الفرصة محفوظة مسبقاً تُزال من الحفظ
        - إذا لم تكن محفوظة تُضاف إلى المحفظة
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        # البحث عن الفرصة المطلوبة
        try:
            internship = Internship.objects.get(id=request.data.get('internship_id'))
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        # محاولة جلب السجل أو إنشاؤه (نظام toggle)
        saved, created = SavedInternship.objects.get_or_create(
            trainee=user.trainee_profile, internship=internship
        )
        if not created:
            # السجل موجود مسبقاً → إزالة الحفظ
            saved.delete()
            return Response({'message': 'تم إزالة الحفظ'})
        # سجل جديد → تم الحفظ بنجاح
        return Response({'message': 'تم الحفظ بنجاح'}, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════
# عرض التصنيفات المتاحة
# ══════════════════════════════════════════════════════════════
class CategoryListView(APIView):
    """عرض جميع التصنيفات المتاحة في النظام (مثل: هندسة، تكنولوجيا، تسويق...)"""

    def get(self, request):
        """جلب جميع التصنيفات مع أسمائها وأوصافها"""
        cats = Category.objects.all()
        return Response([{'id': c.id, 'name': c.name, 'description': c.description} for c in cats])
