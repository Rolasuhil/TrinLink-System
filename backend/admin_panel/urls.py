from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('users/', views.ManageUsersView.as_view(), name='manage-users'),
    path('content/', views.ManageContentView.as_view(), name='manage-content'),
    path('reports/', views.AdminReportsView.as_view(), name='admin-reports'),
    path('assign/', views.AssignTraineeView.as_view(), name='assign-trainee'),
    path('public-stats/', views.PublicStatsView.as_view(), name='public-stats'),
]
