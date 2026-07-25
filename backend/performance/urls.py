from django.urls import path
from . import views

urlpatterns = [
    path('attendance/', views.DailyAttendanceView.as_view(), name='daily-attendance'),
    path('work-reports/', views.WorkReportView.as_view(), name='work-reports'),
    path('performance-reports/', views.PerformanceReportView.as_view(), name='performance-reports'),
    path('supervisor/trainees/', views.SupervisorTraineesView.as_view(), name='supervisor-trainees'),
]
