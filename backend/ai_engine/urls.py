# ملف روابط URL لمحرك الذكاء الاصطناعي
# يعرّف نقاط النهاية (endpoints) لواجهات برمجة التطبيقات الخاصة بالذكاء الاصطناعي

from django.urls import path
from . import views

urlpatterns = [
    # رفع وتحليل السيرة الذاتية
    path('cv/upload/', views.CVUploadView.as_view(), name='cv-upload'),
    # المطابقة الذكية للمتدربين بالفرص التدريبية
    path('match/', views.AIMatchView.as_view(), name='ai-match'),
    # جلب قائمة تحليلات السير الذاتية
    path('cv/analysis/', views.CVAnalysisListView.as_view(), name='cv-analysis'),
]
