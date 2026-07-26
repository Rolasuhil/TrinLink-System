"""
مسارات API لتطبيق المجتمع
تُعرّف نقاط النهاية للمنشورات والتعليقات و الإعجابات وتقييمات الشركات
"""

from django.urls import path
from . import views

urlpatterns = [
    # عرض جميع المنشورات وإنشاء منشور جديد
    path('posts/', views.PostListView.as_view(), name='post-list'),
    # عرض تفاصيل منشور معين أو حذفه
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    # الإعجاب بمنشور معين
    path('posts/<int:post_id>/like/', views.PostLikeView.as_view(), name='post-like'),
    # إضافة تعليق جديد على منشور
    path('posts/<int:post_id>/comments/', views.CommentCreateView.as_view(), name='comment-create'),
    # عرض جميع التقييمات وإضافة تقييم جديد
    path('ratings/', views.CompanyRatingFlatView.as_view(), name='company-ratings-flat'),
    # عرض تقييمات شركة محددة وإضافة تقييم لها
    path('companies/<int:company_id>/ratings/', views.CompanyRatingView.as_view(), name='company-ratings'),
]
