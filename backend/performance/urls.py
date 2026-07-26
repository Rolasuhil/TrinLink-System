# ملف روابط URL لأداء النظام
# يعرّف نقاط النهاية (endpoints) لإدارة الحضور والتقارير اليومية والأسبوعية وقائمة المتدربين

from django.urls import path
from . import views

urlpatterns = [
    # سجل الحضور اليومي (تسجيل حضور/انصراف وعرض السجل)
    path('attendance/', views.DailyAttendanceView.as_view(), name='daily-attendance'),
    # التقارير اليومية للمتدرب (رفع وعرض مهام اليوم)
    path('work-reports/', views.WorkReportView.as_view(), name='work-reports'),
    # تقارير الأداء الأسبوعية (تقييم الشركة وعرض النتائج)
    path('performance-reports/', views.PerformanceReportView.as_view(), name='performance-reports'),
    # قائمة المتدربين المعيّنين للمشرف
    path('supervisor/trainees/', views.SupervisorTraineesView.as_view(), name='supervisor-trainees'),
]
