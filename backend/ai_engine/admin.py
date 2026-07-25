from django.contrib import admin
from .models import AIMatchingResult, CVAnalysis


@admin.register(AIMatchingResult)
class AIMatchingResultAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'internship', 'match_score', 'created_at']
    list_filter = ['match_score']


@admin.register(CVAnalysis)
class CVAnalysisAdmin(admin.ModelAdmin):
    list_display = ['cv', 'overall_score', 'created_at']
