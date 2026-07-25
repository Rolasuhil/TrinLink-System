from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SupervisionAssignment, Report, WorkReport, PerformanceReport, DailyAttendance
from django.conf import settings
import jwt


def get_user(request):
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
    def get(self, request):
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
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        from django.utils import timezone
        today = timezone.now().date()
        attendance, created = DailyAttendance.objects.get_or_create(
            trainee=user.trainee_profile,
            date=today,
            defaults={
                'check_in_time': timezone.now(),
                'status': request.data.get('status', 'present'),
            }
        )
        if not created:
            if request.data.get('action') == 'checkout':
                attendance.check_out_time = timezone.now()
                attendance.save()
                return Response({'message': 'تم تسجيل الانصراف'})
            return Response({'message': 'لقد سجلت حضورك اليوم مسبقاً'})

        return Response({'message': 'تم تسجيل الحضور بنجاح'}, status=status.HTTP_201_CREATED)


class WorkReportView(APIView):
    def get(self, request):
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
    def get(self, request):
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.person_type == 'company':
            reports = PerformanceReport.objects.filter(company=user.company_profile)
        elif user.person_type == 'supervisor':
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
    def get(self, request):
        user = get_user(request)
        if not user or user.person_type != 'supervisor':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

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
