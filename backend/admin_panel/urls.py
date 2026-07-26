# ملف روابط URL للوحة تحكم المدير
# يعرّف نقاط النهاية (endpoints) لإدارة المستخدمين والمحتوى والتقارير والتعيينات

from django.urls import path
from . import views

urlpatterns = [
    # لوحة تحكم المدير الرئيسية (إحصائيات شاملة)
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    # إدارة المستخدمين (عرض، تعديل، حذف)
    path('users/', views.ManageUsersView.as_view(), name='manage-users'),
    # إدارة المحتوى (فرص التدريب، المنشورات، الفئات)
    path('content/', views.ManageContentView.as_view(), name='manage-content'),
    # التقارير الإدارية المتقدمة
    path('reports/', views.AdminReportsView.as_view(), name='admin-reports'),
    # تعيين المتدربين للمشرفين
    path('assign/', views.AssignTraineeView.as_view(), name='assign-trainee'),
    # الإحصائيات العامة (متاحة للجميع بدون تسجيل دخول)
    path('public-stats/', views.PublicStatsView.as_view(), name='public-stats'),
]
