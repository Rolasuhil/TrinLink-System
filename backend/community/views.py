"""
 views API لتطبيق المجتمع
تتضمن واجهات برمجية لإدارة المنشورات والتعليقات و تقييمات الشركات
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CommunityPost, Comment, CompanyRating
from django.conf import settings
import jwt


# دالة مساعدة لاستخراج المستخدم من رمز JWT في رأس التصريح
def get_user(request):
    """تستخرج المستخدم الحالي من التوكن المُرسل في رأس Authorization"""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    try:
        payload = jwt.decode(auth.split(' ')[1], settings.SECRET_KEY, algorithms=['HS256'])
        from accounts.models import Person
        return Person.objects.get(user_id=payload['user_id'])
    except Exception:
        return None


# واجهة API لعرض جميع المنشورات وإنشاء منشور جديد
class PostListView(APIView):
    """عرض و إنشاء منشورات المجتمع - GET يُرجع جميع المنشورات المعتمدة، POST يُنشئ منشوراً جديداً"""
    def get(self, request):
        """إرجاع جميع المنشورات المعتمدة مرتبة من الأحدث إلى الأقدم"""
        posts = CommunityPost.objects.filter(is_approved=True)
        data = [{
            'id': p.id,
            'author_name': p.author.full_name,
            'author_type': p.author.person_type,
            'title': p.title,
            'content': p.content,
            'attachment': p.attachment.url if p.attachment else None,
            'likes_count': p.likes_count,
            'comments_count': p.comments_count,
            'created_at': str(p.created_at),
        } for p in posts]
        return Response(data)

    def post(self, request):
        """إنشاء منشور جديد بعد التحقق من هوية المستخدم"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        post = CommunityPost.objects.create(
            author=user,
            title=request.data.get('title', ''),
            content=request.data.get('content', ''),
        )
        return Response({'message': 'تم النشر بنجاح', 'id': post.id}, status=status.HTTP_201_CREATED)


# واجهة API لعرض تفاصيل منشور معين أو حذفه
class PostDetailView(APIView):
    """عرض تفاصيل منشور واحد مع تعليقاته أو حذفه إذا كان الكاتب هو المستخدم الحالي"""
    def get(self, request, pk):
        """إرجاع تفاصيل منشور محدد بناءً على المعرّف"""
        try:
            post = CommunityPost.objects.get(id=pk)
        except CommunityPost.DoesNotExist:
            return Response({'error': 'المنشور غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        comments = post.comments.all()
        return Response({
            'id': post.id,
            'author_name': post.author.full_name,
            'title': post.title,
            'content': post.content,
            'likes_count': post.likes_count,
            'created_at': str(post.created_at),
            'comments': [{
                'id': c.id,
                'author_name': c.author.full_name,
                'content': c.content,
                'created_at': str(c.created_at),
            } for c in comments],
        })

    def delete(self, request, pk):
        """حذف منشور - يُسمح فقط للكاتب بحذف منشوره"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            post = CommunityPost.objects.get(id=pk, author=user)
            post.delete()
            return Response({'message': 'تم الحذف بنجاح'})
        except CommunityPost.DoesNotExist:
            return Response({'error': 'غير موجود'}, status=status.HTTP_404_NOT_FOUND)


# واجهة API لإضافة تعليق جديد على منشور
class CommentCreateView(APIView):
    """إضافة تعليق جديد على منشور محدد، ويُزداد عدّاد التعليقات تلقائياً"""
    def post(self, request, post_id):
        """إنشاء تعليق جديد بعد التحقق من صلاحية المستخدم ووجود المنشور"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post = CommunityPost.objects.get(id=post_id)
        except CommunityPost.DoesNotExist:
            return Response({'error': 'المنشور غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        comment = Comment.objects.create(
            post=post,
            author=user,
            content=request.data.get('content', ''),
        )
        post.comments_count += 1
        post.save()
        return Response({'message': 'تمت إضافة التعليق', 'id': comment.id}, status=status.HTTP_201_CREATED)


# واجهة API لإدارة تقييمات الشركات بناءً على معرّف الشركة
class CompanyRatingView(APIView):
    """عرض تقييمات شركة محددة أو إضافة تقييم جديد لها"""
    def get(self, request, company_id):
        """إرجاع جميع تقييمات شركة محددة مع متوسط التقييم وعدد التقييمات"""
        ratings = CompanyRating.objects.filter(company_id=company_id)
        data = [{
            'id': r.id,
            'trainee_name': r.trainee.person.full_name,
            'score': r.score,
            'review': r.review,
            'created_at': str(r.created_at),
        } for r in ratings]
        avg = ratings.values_list('score', flat=True)
        avg_score = sum(avg) / len(avg) if avg else 0
        return Response({'ratings': data, 'average_score': round(avg_score, 1), 'total': len(data)})

    def post(self, request, company_id):
        """إضافة تقييم جديد لشركة - متاح فقط للمتدربين"""
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        from accounts.models import CompanyProfile
        try:
            company = CompanyProfile.objects.get(id=company_id)
        except CompanyProfile.DoesNotExist:
            return Response({'error': 'الشركة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        rating = CompanyRating.objects.create(
            company=company,
            trainee=user.trainee_profile,
            score=request.data.get('score', 5),
            review=request.data.get('review', ''),
        )
        return Response({'message': 'تم التقييم بنجاح'}, status=status.HTTP_201_CREATED)


# واجهة API للإعجاب بالمنشورات
class PostLikeView(APIView):
    """إضافة إعجاب لمنشور معين وزيادة عدّاد الإعجابات"""
    def post(self, request, post_id):
        """زيادة عدد إعجابات منشور بمعرّف محدد بعد التحقق من هوية المستخدم"""
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            post = CommunityPost.objects.get(id=post_id)
        except CommunityPost.DoesNotExist:
            return Response({'error': 'المنشور غير موجود'}, status=status.HTTP_404_NOT_FOUND)
        post.likes_count += 1
        post.save(update_fields=['likes_count'])
        return Response({'message': 'تم الإعجاب', 'likes_count': post.likes_count})


# واجهة API شاملة لإدارة تقييمات الشركات بدون تحديد شركة معينة
class CompanyRatingFlatView(APIView):
    """عرض آخر 10 تقييمات لجميع الشركات أو إضافة تقييم جديد"""
    def get(self, request):
        """إرجاع آخر 10 تقييمات مرتبة من الأحدث مع بيانات الشركة والمتدرب"""
        ratings = CompanyRating.objects.select_related(
            'company', 'company__person', 'trainee', 'trainee__person'
        ).order_by('-created_at')[:10]

        data = []
        for r in ratings:
            data.append({
                'id': r.id,
                'company_name': r.company.company_name if r.company else '',
                'trainee_name': r.trainee.person.full_name if r.trainee and r.trainee.person else '',
                'score': r.score,
                'review': r.review,
                'created_at': str(r.created_at),
            })
        return Response(data)

    def post(self, request):
        """إضافة تقييم جديد لشركة محددة - يتطلب تحديد company_id"""
        user = get_user(request)
        if not user or user.person_type != 'trainee':
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        company_id = request.data.get('company_id')
        if not company_id:
            return Response({'error': 'company_id مطلوب'}, status=status.HTTP_400_BAD_REQUEST)

        from accounts.models import CompanyProfile
        try:
            company = CompanyProfile.objects.get(id=company_id)
        except CompanyProfile.DoesNotExist:
            return Response({'error': 'الشركة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        rating = CompanyRating.objects.create(
            company=company,
            trainee=user.trainee_profile,
            score=request.data.get('score', 5),
            review=request.data.get('review', ''),
        )
        return Response({'message': 'تم التقييم بنجاح'}, status=status.HTTP_201_CREATED)
