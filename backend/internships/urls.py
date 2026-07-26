"""
مسارات API للتدريب والتقديمات
- تعريف مسارات URL الخاصة بفرص التدريب والتقديمات
- ربط كل مسار بالـ API view المناسب له
"""

from django.urls import path
from . import views

# قائمة مسارات URL لتطبيق التدريب والتقديمات
urlpatterns = [
    # مسار عرض جميع فرص التدريب ونشر فرصة جديدة
    path('', views.InternshipListView.as_view(), name='internship-list'),
    # مسار عرض وتعديل وحذف فرصة تدريب محددة (بمعرفها)
    path('<int:pk>/', views.InternshipDetailView.as_view(), name='internship-detail'),
    # مسار عرض جميع طلبات التقديم وإنشاء طلب جديد
    path('applications/', views.ApplicationListView.as_view(), name='application-list'),
    # مسار عرض وتحديث حالة طلب تقديم محدد (بمعرفه)
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    # مسار عرض وإدارة فرص التدريب المحفوظة من قبل المتدرب
    path('saved/', views.SavedInternshipView.as_view(), name='saved-internships'),
    # مسار عرض جميع التصنيفات المتاحة
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
]
