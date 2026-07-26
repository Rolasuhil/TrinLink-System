# ملف إدارة لوحة تحكمjango لمحرك الذكاء الاصطناعي
# يسجل النماذج في لوحة التحكم لإدارة نتائج المطابقة وتحليلات السير الذاتية

from django.contrib import admin
from .models import AIMatchingResult, CVAnalysis


@admin.register(AIMatchingResult)
class AIMatchingResultAdmin(admin.ModelAdmin):
    """إدارة نتائج مطابقة الذكاء الاصطناعي في لوحة التحكم
    يعرض المتدرب والفرصة ونسبة المطابقة والتاريخ
    """

    # الأعمدة المعروضة في قائمة النتائج
    list_display = ['trainee', 'internship', 'match_score', 'created_at']
    # فلتر حسب نسبة المطابقة
    list_filter = ['match_score']


@admin.register(CVAnalysis)
class CVAnalysisAdmin(admin.ModelAdmin):
    """إدارة تحليلات السير الذاتية في لوحة التحكم
    يعرض السيرة الذاتية والتقييم العام وتاريخ التحليل
    """

    # الأعمدة المعروضة في قائمة التحليلات
    list_display = ['cv', 'overall_score', 'created_at']
