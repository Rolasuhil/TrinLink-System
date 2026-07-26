# ملف واجهات برمجة التطبيقات لأداء النظام
# يحتوي على منطق إدارة الحضور اليومي والتقارير اليومية والأسبوعية وقائمة المتدربين للمشرف

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SupervisionAssignment, Report, WorkReport, PerformanceReport, DailyAttendance
from django.conf import settings
import jwt


def get_user(request):
    """دالة مساعدة لاستخراج بيانات المستخدم من رمز JWT في طلب التصريح
    ترجع كائن الشخص إذا كان الرمز صالحاً، أو None إذا لم يكن كذلك
    """
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    try:
        payload = jwt.decode(auth.split(' ')[1], settings.SECRET_KEY, algorithms=['HS256'])
        from accounts.models import Person
        return Person.objects.get(user_id=payload['user_id'])
    except Exception:
        return None


class DailyAttendanceView(APIView):
    """واجهة سجل الحضور اليومي
    تسمح للمتدربين بتسجيل حضورهم وانصرافهم اليومي وعرض سجل حضورهم
    """

    def get(self, request):
        """جلب سجل الحضور الكامل للمتدرب
        ترجع قائمة بجميع سجلات الحضور مع التواريخ والأوقات والحالات
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        attendance = DailyAttendance.objects.filter(trainee=user.trainee_profile)
        data = [{
            'id': a.id,
            'date': str(a.date),
            'check_in': str(a.check_in_time) if a.check_in_time else None,
            'check_out': str(a.check_out_time) if a.check_out_time else None,
            'status': a.status,
            'status_display': a.get_status_display(),
        } for a in attendance]
        return Response(data)

    def post(self, request):
        """تسجيل الحضور أو الانصراف
        - إذا لم يسجل المتدرب حضوره اليوم: يسجّل حضوره مع الوقت الحالي
        - إذا كان طلب تسجيل انصراف: يسجّل وقت الانصراف
        - إذا كان قد سجّل حضوره مسبقاً: يُرجع رسالة تأكيد
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        from django.utils import timezone
        today = timezone.now().date()
        # محاولة إنشاء سجل حضور جديد أو الحصول على السجل الحالي
        attendance, created = DailyAttendance.objects.get_or_create(
            trainee=user.trainee_profile,
            date=today,
            defaults={
                'check_in_time': timezone.now(),
                'status': request.data.get('status', 'present'),
            }
        )
        if not created:
            # إذا كان السجل موجوداً بالفعل، تحقق من طلب الانصراف
            if request.data.get('action') == 'checkout':
                attendance.check_out_time = timezone.now()
                attendance.save()
                return Response({'message': 'تم تسجيل الانصراف'})
            return Response({'message': 'لقد سجلت حضورك اليوم مسبقاً'})

        return Response({'message': 'تم تسجيل الحضور بنجاح'}, status=status.HTTP_201_CREATED)


class WorkReportView(APIView):
    """واجهة التقارير اليومية للمتدرب
    تسمح للمتدربين برفع تقارير مهامهم اليومية وعرض تقاريرهم السابقة
    """

    def get(self, request):
        """جلب جميع التقارير اليومية للمتدرب
        ترجع قائمة بالتقارير مع عناوين المهام والوصف والتقييم وملاحظات الشركة
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        reports = WorkReport.objects.filter(trainee=user.trainee_profile)
        data = [{
            'id': r.id,
            'task_title': r.task_title,
            'description': r.description,
            'submitted_at': str(r.submitted_at),
            'performance_rating': r.performance_rating,
            'company_feedback': r.company_feedback,
        } for r in reports]
        return Response(data)

    def post(self, request):
        """تقديم تقرير عمل يومي جديد
        ينشئ سجلاً جديداً بالتقرير اليومي للمتدرب
        """
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        report = WorkReport.objects.create(
            trainee=user.trainee_profile,
            task_title=request.data.get('task_title', ''),
            description=request.data.get('description', ''),
        )
        return Response({'message': 'تم رفع التقرير بنجاح', 'id': report.id}, status=status.HTTP_201_CREATED)


class PerformanceReportView(APIView):
    """واجهة تقارير الأداء الأسبوعية
    تسمح للشركات بتقييم أداء المتدربين وعرض التقارير حسب نوع المستخدم
    """

    def get(self, request):
        """جلب تقارير الأداء الأسبوعية
        - الشركة: ترى تقارير المتدربين الذين يقيّمون أداءهم
        - المشرف: يرى تقارير المتدربين المعيّنين تحت إشرافه
        - المتدرب: يرى تقارير أداءه الخاصة
        """
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        # جلب التقارير حسب نوع المستخدم
        if user.person_type == 'company':
            reports = PerformanceReport.objects.filter(company=user.company_profile)
        elif user.person_type == 'supervisor':
            # جلب المتدربين المعيّنين للمشرف ثم جلب تقاريرهم
            assignments = SupervisionAssignment.objects.filter(supervisor=user.supervisor_profile, status='active')
            trainee_ids = assignments.values_list('trainee_id', flat=True)
            reports = PerformanceReport.objects.filter(trainee_id__in=trainee_ids)
        elif user.person_type == 'trainee':
            reports = PerformanceReport.objects.filter(trainee=user.trainee_profile)
        else:
            reports = PerformanceReport.objects.none()

        data = [{
            'id': r.id,
            'trainee_name': r.trainee.person.full_name,
            'week_number': r.week_number,
            'attendance_confirmed': r.attendance_confirmed,
            'performance_score': r.performance_score,
            'comments': r.comments,
            'ai_summary': r.ai_summary,
            'submitted_at': str(r.submitted_at),
        } for r in reports]
        return Response(data)

    def post(self, request):
        """إنشاء تقرير أداء أسبوعي جديد
        فقط الشركات يمكنها تقديم تقارير الأداء للمتدربين
        """
        user = get_user(request)
        if not user or user.person_type != 'company':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        from accounts.models import Trainee
        try:
            trainee = Trainee.objects.get(id=request.data.get('trainee_id'))
        except Trainee.DoesNotExist:
            return Response({'error': 'المتدرب غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        report = PerformanceReport.objects.create(
            trainee=trainee,
            company=user.company_profile,
            week_number=request.data.get('week_number', 1),
            attendance_confirmed=request.data.get('attendance_confirmed', False),
            performance_score=request.data.get('performance_score', 0),
            comments=request.data.get('comments', ''),
        )
        return Response({'message': 'تم إرسال التقرير بنجاح', 'id': report.id}, status=status.HTTP_201_CREATED)


class SupervisorTraineesView(APIView):
    """واجهة جلب قائمة المتدربين المعيّنين للمشرف
    ترجع جميع المتدربين النشطين تحت إشراف المشرف مع معلوماتهم الأكاديمية
    """

    def get(self, request):
        """جلب قائمة المتدربين النشطين تحت إشراف المشرف
        ترجع: الاسم، الجامعة، التخصص، المعدل، تاريخ التعيين
        """
        user = get_user(request)
        if not user or user.person_type != 'supervisor':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        # جلب التعيينات النشطة فقط
        assignments = SupervisionAssignment.objects.filter(
            supervisor=user.supervisor_profile, status='active'
        )
        data = [{
            'id': a.trainee.id,
            'name': a.trainee.person.full_name,
            'university': a.trainee.university,
            'major': a.trainee.major,
            'gpa': a.trainee.gpa,
            'assignment_date': str(a.assignment_date),
        } for a in assignments]
        return Response(data)
