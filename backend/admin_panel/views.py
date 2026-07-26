from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from accounts.models import Person, Trainee, CompanyProfile, SupervisorProfile
from internships.models import Internship, Application, Category
from performance.models import SupervisionAssignment, PerformanceReport
from messaging.models import Notification
from .models import ContentReport
from django.conf import settings
from rest_framework.permissions import AllowAny
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


class PublicStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'total_trainees': Trainee.objects.count(),
            'total_companies': CompanyProfile.objects.count(),
            'total_internships': Internship.objects.count(),
            'open_internships': Internship.objects.filter(status='open').count(),
            'total_applications': Application.objects.count(),
        })


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
            'total_admins': Person.objects.filter(person_type='admin').count(),
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

        # Fetch real internships
        internships = Internship.objects.select_related('company', 'company__person', 'category').all()
        internship_data = []
        for i in internships:
            internship_data.append({
                'id': i.id,
                'title': i.title,
                'company': i.company.person.full_name if i.company and i.company.person else '',
                'location': getattr(i, 'location', ''),
                'status': i.status,
                'type': 'internship',
            })

        # Fetch real posts
        from community.models import CommunityPost
        posts = CommunityPost.objects.select_related('author').all()
        post_data = []
        for p in posts:
            post_data.append({
                'id': p.id,
                'title': p.content[:60] if p.content else '',
                'author': p.author.full_name if p.author else '',
                'type': 'منشور',
                'status': 'active',
                'type_label': 'post',
            })

        # Fetch categories
        categories = Category.objects.annotate(internship_count=Count('internship')).all()
        cat_data = []
        for c in categories:
            cat_data.append({
                'id': c.id,
                'name': c.name,
                'count': c.internship_count,
            })

        return Response({
            'internships': internship_data,
            'posts': post_data,
            'categories': cat_data,
            'stats': {
                'total_internships': len(internship_data),
                'active_internships': sum(1 for i in internship_data if i['status'] == 'open'),
                'draft_internships': sum(1 for i in internship_data if i['status'] == 'draft'),
                'closed_internships': sum(1 for i in internship_data if i['status'] == 'closed'),
                'total_posts': len(post_data),
                'total_categories': len(cat_data),
            }
        })

    def delete(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        content_type = request.data.get('content_type', '')
        content_id = request.data.get('content_id')

        if content_type == 'internship':
            try:
                internship = Internship.objects.get(id=content_id)
                internship.delete()
                return Response({'message': 'تم الحذف بنجاح'})
            except Internship.DoesNotExist:
                return Response({'error': 'الفرصة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)
        elif content_type == 'post':
            from community.models import CommunityPost
            try:
                post = CommunityPost.objects.get(id=content_id)
                post.delete()
                return Response({'message': 'تم الحذف بنجاح'})
            except CommunityPost.DoesNotExist:
                return Response({'error': 'المنشور غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': 'نوع المحتوى غير صحيح'}, status=status.HTTP_400_BAD_REQUEST)


class AdminReportsView(APIView):
    def get(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        from django.utils import timezone
        from datetime import timedelta
        from community.models import CompanyRating

        monthly_apps = Application.objects.values('status').annotate(count=Count('id'))
        popular_categories = Internship.objects.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # Monthly registrations (last 7 months)
        monthly_registrations = []
        now = timezone.now()
        month_names = ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']
        for i in range(6, -1, -1):
            d = now - timedelta(days=30*i)
            count = Person.objects.filter(created_at__year=d.year, created_at__month=d.month).count()
            monthly_registrations.append({'month': month_names[d.month-1], 'count': count})

        # Average rating
        avg_rating = CompanyRating.objects.aggregate(avg=Avg('score'))['avg'] or 0

        # Application stats
        total_apps = Application.objects.count()
        accepted = Application.objects.filter(status='accepted').count()
        pending = Application.objects.filter(status='pending').count()
        rejected = Application.objects.filter(status='rejected').count()

        # Weekly activity (last 7 days)
        weekly_activity = []
        day_names = ['سبت','أحد','إثن','ثلا','أرب','خمي','جمع']
        for i in range(6, -1, -1):
            d = now - timedelta(days=i)
            count = Person.objects.filter(created_at__date=d.date()).count()
            weekly_activity.append({'day': day_names[6-i], 'count': count})

        # Best companies by internship count
        best_companies = (
            Internship.objects.values('company__person__full_name')
            .annotate(internship_count=Count('id'))
            .order_by('-internship_count')[:5]
        )
        best_cos = []
        for c in best_companies:
            name = c['company__person__full_name'] or 'شركة'
            best_cos.append({'name': name, 'count': c['internship_count']})

        return Response({
            'total_users': Person.objects.count(),
            'total_internships': Internship.objects.count(),
            'total_applications': total_apps,
            'average_rating': round(avg_rating, 1),
            'applications_by_status': list(monthly_apps),
            'popular_categories': list(popular_categories),
            'monthly_registrations': monthly_registrations,
            'weekly_activity': weekly_activity,
            'success_rate': round(accepted/total_apps*100, 1) if total_apps else 0,
            'pending_rate': round(pending/total_apps*100, 1) if total_apps else 0,
            'rejected_rate': round(rejected/total_apps*100, 1) if total_apps else 0,
            'accepted_count': accepted,
            'pending_count': pending,
            'rejected_count': rejected,
            'best_companies': best_cos,
            'specialization_distribution': list(
                Trainee.objects.values('major').annotate(count=Count('id')).order_by('-count')[:5]
            ),
        })


class AssignTraineeView(APIView):
    def get(self, request):
        admin = get_admin(request)
        if not admin:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        assignments = SupervisionAssignment.objects.select_related(
            'supervisor', 'supervisor__person', 'trainee', 'trainee__person'
        ).all()

        data = []
        for a in assignments:
            data.append({
                'id': a.id,
                'trainee_name': a.trainee.person.full_name if a.trainee else '',
                'trainee_id': a.trainee.person.user_id if a.trainee else '',
                'supervisor_name': a.supervisor.person.full_name if a.supervisor else '',
                'status': a.status,
                'created_at': str(a.assignment_date) if hasattr(a, 'assignment_date') else '',
            })

        # Internships list for matching
        internships = Internship.objects.filter(status='open').select_related('company', 'company__person', 'category')
        internship_data = []
        for i in internships:
            internship_data.append({
                'id': i.id,
                'title': i.title,
                'company': i.company.person.full_name if i.company and i.company.person else '',
                'location': getattr(i, 'location', ''),
                'category': i.category.name if i.category else '',
                'internship_type': getattr(i, 'internship_type', ''),
            })

        return Response({'assignments': data, 'internships': internship_data})

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
