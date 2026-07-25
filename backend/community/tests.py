"""
Unit Tests for community app
"""
from django.test import TestCase
from accounts.models import Person, Trainee, CompanyProfile
from .models import CommunityPost, Comment, CompanyRating


class CommunityPostModelTest(TestCase):
    """Unit tests for CommunityPost model"""

    def setUp(self):
        self.author = Person.objects.create(
            full_name='كاتب المنشور',
            email='author@test.com',
            person_type='trainee',
        )

    def test_post_creation(self):
        post = CommunityPost.objects.create(
            author=self.author,
            title='نصيحة لل متدربيين',
            content='التدريب ممتاز لبناء الخبرة',
        )
        self.assertEqual(post.title, 'نصيحة لل متدربيين')
        self.assertEqual(post.likes_count, 0)
        self.assertTrue(post.is_approved)

    def test_post_likes_increment(self):
        post = CommunityPost.objects.create(
            author=self.author,
            title='منشور',
            content='محتوى',
        )
        post.likes_count += 1
        post.save()
        post.refresh_from_db()
        self.assertEqual(post.likes_count, 1)

    def test_post_comments_count(self):
        post = CommunityPost.objects.create(
            author=self.author,
            title='منشور',
            content='محتوى',
        )
        Comment.objects.create(post=post, author=self.author, content='تعليق 1')
        Comment.objects.create(post=post, author=self.author, content='تعليق 2')
        self.assertEqual(post.comments.count(), 2)


class CommentModelTest(TestCase):
    """Unit tests for Comment model"""

    def setUp(self):
        self.author = Person.objects.create(
            full_name='معلق',
            email='commenter@test.com',
            person_type='trainee',
        )
        self.post = CommunityPost.objects.create(
            author=self.author,
            title='منشور للتعليق',
            content='محتوى التعليق',
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='تعليق رائع!',
        )
        self.assertEqual(comment.content, 'تعليق رائع!')

    def test_comment_post_link(self):
        comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='اختبار',
        )
        self.assertEqual(comment.post.title, 'منشور للتعليق')

    def test_multiple_comments(self):
        for i in range(3):
            Comment.objects.create(
                post=self.post,
                author=self.author,
                content=f'تعليق {i}',
            )
        self.assertEqual(self.post.comments.count(), 3)


class CompanyRatingModelTest(TestCase):
    """Unit tests for CompanyRating model"""

    def setUp(self):
        self.company_person = Person.objects.create(
            full_name='Rating Corp',
            email='ratingcorp@test.com',
            person_type='company',
        )
        self.company = CompanyProfile.objects.create(
            person=self.company_person,
            company_name='Rating Corp',
        )
        self.trainee_person = Person.objects.create(
            full_name='مقيّم',
            email='rater@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.trainee_person)

    def test_rating_creation(self):
        rating = CompanyRating.objects.create(
            company=self.company,
            trainee=self.trainee,
            score=4,
            review='تجربة ممتازة في الشركة',
        )
        self.assertEqual(rating.score, 4)
        self.assertEqual(rating.review, 'تجربة ممتازة في الشركة')

    def test_rating_score_range(self):
        rating = CompanyRating.objects.create(
            company=self.company,
            trainee=self.trainee,
            score=5,
            review='ممتاز',
        )
        self.assertGreaterEqual(rating.score, 1)
        self.assertLessEqual(rating.score, 5)
