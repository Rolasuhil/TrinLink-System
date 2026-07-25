from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Person, Trainee, CompanyProfile, SupervisorProfile
from internships.models import Internship, Application, Category
from performance.models import SupervisionAssignment, PerformanceReport
from messaging.models import Notification
from .models import ContentReport
from django.conf import settings
import jwt


def get_admin(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    try:
        payload = jwt.decode(auth.split(' ')[1], settings.SECRET_KEY, algorithms=['HS256'])
        user = Person.objects.get(user_id=payload['user_id'])
        if user.person_type != 'admin':
            return None
        return user
    except Exception:
        return None


class AdminDashboardView(APIView):
    def get(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'total_users': Person.objects.count(),
            'total_trainees': Trainee.objects.count(),
            'total_companies': CompanyProfile.objects.count(),
            'total_supervisors': SupervisorProfile.objects.count(),
            'total_internships': Internship.objects.count(),
            'open_internships': Internship.objects.filter(status='open').count(),
            'total_applications': Application.objects.count(),
            'pending_applications': Application.objects.filter(status='pending').count(),
            'accepted_applications': Application.objects.filter(status='accepted').count(),
            'rejected_applications': Application.objects.filter(status='rejected').count(),
            'pending_companies': Person.objects.filter(person_type='company', is_verified=False).count(),
            'active_supervisions': SupervisionAssignment.objects.filter(status='active').count(),
        })


class ManageUsersView(APIView):
    def get(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        users = Person.objects.all()
        person_type = request.query_params.get('type', '')
        if person_type:
            users = users.filter(person_type=person_type)

        data = [{
            'id': u.id,
            'user_id': u.user_id,
            'full_name': u.full_name,
            'email': u.email,
            'person_type': u.person_type,
            'person_type_display': u.get_person_type_display(),
            'is_verified': u.is_verified,
            'is_active': u.is_active,
            'created_at': str(u.created_at),
        } for u in users]
        return Response(data)

    def patch(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.data.get('user_id')
        try:
            user = Person.objects.get(id=user_id)
        except Person.DoesNotExist:
            return Response({'error': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        if 'is_active' in request.data:
            user.is_active = request.data['is_active']
        if 'is_verified' in request.data:
            user.is_verified = request.data['is_verified']
        user.save()

        return Response({'message': 'تم التحديث بنجاح'})

    def delete(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.data.get('user_id')
        try:
            user = Person.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'تم الحذف بنجاح'})
        except Person.DoesNotExist:
            return Response({'error': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)


class ManageContentView(APIView):
    def get(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        reports = ContentReport.objects.all()
        data = [{
            'id': r.id,
            'reported_by': r.reported_by.full_name,
            'content_type': r.content_type,
            'content_id': r.content_id,
            'reason': r.reason,
            'status': r.status,
            'created_at': str(r.created_at),
        } for r in reports]
        return Response(data)

    def patch(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        report_id = request.data.get('report_id')
        try:
            report = ContentReport.objects.get(id=report_id)
            report.status = request.data.get('status', 'approved')
            report.reviewed_by = admin
            report.save()
            return Response({'message': 'تم التحديث'})
        except ContentReport.DoesNotExist:
            return Response({'error': 'البلاغ غير موجود'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        report_id = request.data.get('report_id')
        try:
            report = ContentReport.objects.get(id=report_id)
            report.status = 'removed'
            report.reviewed_by = admin
            report.save()
            return Response({'message': 'تمت الإزالة'})
        except ContentReport.DoesNotExist:
            return Response({'error': 'البلاغ غير موجود'}, status=status.HTTP_404_NOT_FOUND)


class AdminReportsView(APIView):
    def get(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        from django.db.models import Count
        monthly_apps = Application.objects.values('status').annotate(count=Count('id'))
        popular_categories = Internship.objects.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        return Response({
            'applications_by_status': list(monthly_apps),
            'popular_categories': list(popular_categories),
            'total_users': Person.objects.count(),
            'total_internships': Internship.objects.count(),
            'total_applications': Application.objects.count(),
        })


class AssignTraineeView(APIView):
    def post(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        trainee_id = request.data.get('trainee_id')
        supervisor_id = request.data.get('supervisor_id')

        try:
            trainee = Trainee.objects.get(id=trainee_id)
            supervisor = SupervisorProfile.objects.get(id=supervisor_id)
        except (Trainee.DoesNotExist, SupervisorProfile.DoesNotExist):
            return Response({'error': 'المتدرب أو المشرف غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        assignment, created = SupervisionAssignment.objects.get_or_create(
            supervisor=supervisor,
            trainee=trainee,
            defaults={'status': 'active'},
        )

        Notification.objects.create(
            user=trainee.person,
            notification_type='system',
            title='تم تعيين مشرف لك',
            message=f'تم تعيين المشرف {supervisor.person.full_name} لمتابعتك',
        )
        Notification.objects.create(
            user=supervisor.person,
            notification_type='system',
            title='تم تعيين متدرب لك',
            message=f'تم تعيين المتدرب {trainee.person.full_name} تحت إشرافك',
        )

        return Response({'message': 'تم الربط بنجاح'}, status=status.HTTP_201_CREATED)
