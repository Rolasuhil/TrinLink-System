from django.db import models
from accounts.models import Trainee


class AIMatchingResult(models.Model):
    id = models.AutoField(primary_key=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='ai_matches', verbose_name='المتدرب')
    internship = models.ForeignKey('internships.Internship', on_delete=models.CASCADE, related_name='ai_matches', verbose_name='الفرصة')
    match_score = models.FloatField(verbose_name='نسبة المطابقة')
    reason = models.TextField(blank=True, verbose_name='سبب التوصية')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'نتيجة مطابقة'
        verbose_name_plural = 'نتائج المطابقة'
        ordering = ['-match_score']

    def __str__(self):
        return f'{self.trainee.person.full_name} - {self.internship.title} ({self.match_score}%)'


class CVAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    cv = models.OneToOneField('accounts.CV', on_delete=models.CASCADE, related_name='analysis', verbose_name='السيرة الذاتية')
    overall_score = models.FloatField(default=0.0, verbose_name='التقييم العام')
    sections_score = models.JSONField(null=True, blank=True, verbose_name='تقييم الأقسام')
    suggestions = models.JSONField(null=True, blank=True, verbose_name='الاقتراحات')
    strengths = models.JSONField(null=True, blank=True, verbose_name='نقاط القوة')
    weaknesses = models.JSONField(null=True, blank=True, verbose_name='نقاط الضعف')
    raw_analysis = models.TextField(blank=True, verbose_name='التحليل الخام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'تحليل سيرة ذاتية'
        verbose_name_plural = 'تحليلات السيرة الذاتية'

    def __str__(self):
        return f'تحليل CV - {self.cv.trainee.person.full_name}'
