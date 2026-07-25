from django.contrib import admin
from .models import CommunityPost, Comment, CompanyRating


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['is_approved']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content', 'created_at']


@admin.register(CompanyRating)
class CompanyRatingAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'company', 'score', 'created_at']
    list_filter = ['score']
