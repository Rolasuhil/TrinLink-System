from django.contrib import admin
from .models import Category, Internship, Application, SavedInternship, AcceptedTrainee


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'category', 'location', 'internship_type', 'status', 'deadline']
    list_filter = ['status', 'internship_type', 'category']
    search_fields = ['title', 'company__company_name']
    date_hierarchy = 'created_at'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'internship', 'status', 'application_date']
    list_filter = ['status']
    search_fields = ['trainee__person__full_name', 'internship__title']


@admin.register(SavedInternship)
class SavedInternshipAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'internship', 'saved_at']


@admin.register(AcceptedTrainee)
class AcceptedTraineeAdmin(admin.ModelAdmin):
    list_display = ['application', 'department', 'joining_date', 'supervisor']
