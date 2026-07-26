# ملف نماذج محرك الذكاء الاصطناعي
# يحتوي على النماذج المتعلقة بمطابقة المتدربين بالفرص التدريبية وتحليل السير الذاتية

from django.db import models
from accounts.models import Trainee


class AIMatchingResult(models.Model):
    """نموذج نتيجة مطابقة الذكاء الاصطناعي
    يخزن نتائج المطابقة بين المتدربين والفرص التدريبية مع درجة المطابقة وسبب التوصية
    """

    id = models.AutoField(primary_key=True)
    # المتدرب المرتبط بهذه النتيجة
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='ai_matches', verbose_name='المتدرب')
    # فرصة التدريب المرتبطة بهذه النتيجة
    internship = models.ForeignKey('internships.Internship', on_delete=models.CASCADE, related_name='ai_matches', verbose_name='الفرصة')
    # نسبة المطابقة بين المتدرب والفرصة (من 0 إلى 100)
    match_score = models.FloatField(verbose_name='نسبة المطابقة')
    # سبب التوصية بالفرصة للمتدرب
    reason = models.TextField(blank=True, verbose_name='سبب التوصية')
    # تاريخ إنشاء النتيجة تلقائياً
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'نتيجة مطابقة'
        verbose_name_plural = 'نتائج المطابقة'
        # ترتيب النتائج حسب أعلى نسبة مطابقة أولاً
        ordering = ['-match_score']

    def __str__(self):
        """تمثيل النصي لنتيجة المطابقة"""
        return f'{self.trainee.person.full_name} - {self.internship.title} ({self.match_score}%)'


class CVAnalysis(models.Model):
    """نموذج تحليل السيرة الذاتية
    يخزن نتائج تحليل الذكاء الاصطناعي للسيرة الذاتية للمتدربين
    """

    id = models.AutoField(primary_key=True)
    # رابط واحد-أحد للسيرة الذاتية المرتبطة بالتحليل
    cv = models.OneToOneField('accounts.CV', on_delete=models.CASCADE, related_name='analysis', verbose_name='السيرة الذاتية')
    # التقييم العام للسيرة الذاتية (من 0 إلى 100)
    overall_score = models.FloatField(default=0.0, verbose_name='التقييم العام')
    # تقييم كل قسم من أقسام السيرة الذاتية (JSON)
    sections_score = models.JSONField(null=True, blank=True, verbose_name='تقييم الأقسام')
    # اقتراحات لتحسين السيرة الذاتية (JSON)
    suggestions = models.JSONField(null=True, blank=True, verbose_name='الاقتراحات')
    # نقاط القوة في السيرة الذاتية (JSON)
    strengths = models.JSONField(null=True, blank=True, verbose_name='نقاط القوة')
    # نقاط الضعف في السيرة الذاتية (JSON)
    weaknesses = models.JSONField(null=True, blank=True, verbose_name='نقاط الضعف')
    # التحليل الخام الكامل من الذكاء الاصطناعي
    raw_analysis = models.TextField(blank=True, verbose_name='التحليل الخام')
    # تاريخ إنشاء التحليل تلقائياً
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'تحليل سيرة ذاتية'
        verbose_name_plural = 'تحليلات السيرة الذاتية'

    def __str__(self):
        """تمثيل النصي لتحليل السيرة الذاتية"""
        return f'تحليل CV - {self.cv.trainee.person.full_name}'
