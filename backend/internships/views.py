from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Internship, Category, Application, SavedInternship, AcceptedTrainee
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


class InternshipListView(APIView):
    def get(self, request):
        search = request.query_params.get('search', '')
        category = request.query_params.get('category', '')
        location = request.query_params.get('location', '')
        internship_type = request.query_params.get('type', '')

        qs = Internship.objects.filter(status='open')
        if search:
            qs = qs.filter(title__icontains=search)
        if category:
            qs = qs.filter(category__id=category)
        if location:
            qs = qs.filter(location__icontains=location)
        if internship_type:
            qs = qs.filter(internship_type=internship_type)
        is_paid = request.query_params.get('is_paid', '')
        if is_paid == 'true':
            qs = qs.filter(is_paid=True)
        elif is_paid == 'false':
            qs = qs.filter(is_paid=False)

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
                'internship_type': i.get_internship_type_display(),
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
        user = get_user(request)
        if not user or user.person_type != 'company':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            company = user.company_profile
        except Exception:
            return Response({'error': 'الملف الشخصي للشركة غير موجود'}, status=status.HTTP_400_BAD_REQUEST)

        category = None
        if request.data.get('category_id'):
            try:
                category = Category.objects.get(id=request.data['category_id'])
            except Category.DoesNotExist:
                pass

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


class InternshipDetailView(APIView):
    def get(self, request, pk):
        try:
            i = Internship.objects.get(id=pk)
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'id': i.id,
            'title': i.title,
            'company': i.company.company_name,
            'company_id': i.company.id,
            'company_industry': i.company.industry or '',
            'company_size': i.company.company_size or '',
            'company_location': i.company.location or '',
            'company_about': i.company.about or '',
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
        user = get_user(request)
        if not user or user.person_type != 'company':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            i = Internship.objects.get(id=pk, company=user.company_profile)
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة أو ليس لديك صلاحية'}, status=status.HTTP_404_NOT_FOUND)

        category = i.category
        if request.data.get('category_id'):
            try:
                category = Category.objects.get(id=request.data['category_id'])
            except Category.DoesNotExist:
                pass

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
        user = get_user(request)
        if not user or user.person_type != 'company':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            i = Internship.objects.get(id=pk, company=user.company_profile)
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة أو ليس لديك صلاحية'}, status=status.HTTP_404_NOT_FOUND)
        i.delete()
        return Response({'message': 'تم حذف الفرصة بنجاح'})


class ApplicationListView(APIView):
    def get(self, request):
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.person_type == 'trainee':
            apps = Application.objects.filter(trainee=user.trainee_profile)
        elif user.person_type == 'company':
            apps = Application.objects.filter(internship__company=user.company_profile)
        else:
            apps = Application.objects.none()

        data = []
        for a in apps:
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
            })
        return Response(data)

    def post(self, request):
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            internship = Internship.objects.get(id=request.data.get('internship_id'))
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        if Application.objects.filter(internship=internship, trainee=user.trainee_profile).exists():
            return Response({'error': 'لقد قدمت على هذه الفرصة مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)

        cover_letter = request.data.get('cover_letter', '')
        resume_version = ''
        if 'resume' in request.FILES:
            resume_file = request.FILES['resume']
            resume_version = resume_file.name

        app = Application.objects.create(
            internship=internship,
            trainee=user.trainee_profile,
            resume_version=resume_version,
            cover_letter=cover_letter,
        )
        return Response({'message': 'تم التقديم بنجاح', 'id': app.id}, status=status.HTTP_201_CREATED)


class ApplicationDetailView(APIView):
    def get(self, request, pk):
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            if user.person_type == 'trainee':
                app = Application.objects.get(id=pk, trainee=user.trainee_profile)
            elif user.person_type == 'company':
                app = Application.objects.get(id=pk, internship__company=user.company_profile)
            else:
                return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        except Application.DoesNotExist:
            return Response({'error': 'الطلب غير موجود'}, status=status.HTTP_404_NOT_FOUND)

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
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        new_status = request.data.get('status')

        if user.person_type == 'company':
            try:
                app = Application.objects.get(id=pk, internship__company=user.company_profile)
            except Application.DoesNotExist:
                return Response({'error': 'الطلب غير موجود'}, status=status.HTTP_404_NOT_FOUND)
            if new_status in ['accepted', 'rejected']:
                app.status = new_status
                app.rejection_reason = request.data.get('rejection_reason', '')
                app.save()
                app.internship.update_acceptance_rate()
            return Response({'message': 'تم تحديث الحالة بنجاح'})

        elif user.person_type == 'trainee':
            try:
                app = Application.objects.get(id=pk, trainee=user.trainee_profile)
            except Application.DoesNotExist:
                return Response({'error': 'الطلب غير موجود'}, status=status.HTTP_404_NOT_FOUND)
            if new_status == 'withdrawn':
                app.status = 'withdrawn'
                app.save()
                app.internship.update_acceptance_rate()
            return Response({'message': 'تم تحديث الحالة بنجاح'})

        return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)


class SavedInternshipView(APIView):
    def get(self, request):
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        saved = SavedInternship.objects.filter(trainee=user.trainee_profile)
        data = [{'id': s.id, 'internship_id': s.internship.id, 'title': s.internship.title} for s in saved]
        return Response(data)

    def post(self, request):
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            internship = Internship.objects.get(id=request.data.get('internship_id'))
        except Internship.DoesNotExist:
            return Response({'error': 'الفرصة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        saved, created = SavedInternship.objects.get_or_create(
            trainee=user.trainee_profile, internship=internship
        )
        if not created:
            saved.delete()
            return Response({'message': 'تم إزالة الحفظ'})
        return Response({'message': 'تم الحفظ بنجاح'}, status=status.HTTP_201_CREATED)


class CategoryListView(APIView):
    def get(self, request):
        cats = Category.objects.all()
        return Response([{'id': c.id, 'name': c.name, 'description': c.description} for c in cats])
