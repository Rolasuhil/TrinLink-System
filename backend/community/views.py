from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CommunityPost, Comment, CompanyRating
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


class PostListView(APIView):
    def get(self, request):
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
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)

        post = CommunityPost.objects.create(
            author=user,
            title=request.data.get('title', ''),
            content=request.data.get('content', ''),
        )
        return Response({'message': 'تم النشر بنجاح', 'id': post.id}, status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    def get(self, request, pk):
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
        user = get_user(request)
        if not user:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            post = CommunityPost.objects.get(id=pk, author=user)
            post.delete()
            return Response({'message': 'تم الحذف بنجاح'})
        except CommunityPost.DoesNotExist:
            return Response({'error': 'غير موجود'}, status=status.HTTP_404_NOT_FOUND)


class CommentCreateView(APIView):
    def post(self, request, post_id):
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


class CompanyRatingView(APIView):
    def get(self, request, company_id):
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
