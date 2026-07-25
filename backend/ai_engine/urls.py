from django.urls import path
from . import views

urlpatterns = [
    path('cv/upload/', views.CVUploadView.as_view(), name='cv-upload'),
    path('match/', views.AIMatchView.as_view(), name='ai-match'),
    path('cv/analysis/', views.CVAnalysisListView.as_view(), name='cv-analysis'),
]
