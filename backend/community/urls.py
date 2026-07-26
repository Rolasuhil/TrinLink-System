from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('posts/<int:post_id>/comments/', views.CommentCreateView.as_view(), name='comment-create'),
    path('ratings/', views.CompanyRatingFlatView.as_view(), name='company-ratings-flat'),
    path('companies/<int:company_id>/ratings/', views.CompanyRatingView.as_view(), name='company-ratings'),
]
