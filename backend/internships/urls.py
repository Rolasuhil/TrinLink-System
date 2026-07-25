from django.urls import path
from . import views

urlpatterns = [
    path('', views.InternshipListView.as_view(), name='internship-list'),
    path('<int:pk>/', views.InternshipDetailView.as_view(), name='internship-detail'),
    path('applications/', views.ApplicationListView.as_view(), name='application-list'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    path('saved/', views.SavedInternshipView.as_view(), name='saved-internships'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
]
