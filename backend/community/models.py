"""
نماذج قاعدة البيانات لتطبيق المجتمع
تتضمن نماذج المنشورات والتعليقات وتقييمات الشركات
"""

from django.db import models
from accounts.models import Person, Trainee, CompanyProfile


# نموذج المنشورات المجتمعية
class CommunityPost(models.Model):
    """يمثل منشوراً في المجتمع يمكن للمستخدمين إنشاؤه والتفاعل معه"""
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='posts', verbose_name='الكاتب')
    title = models.CharField(max_length=300, verbose_name='العنوان')
    content = models.TextField(verbose_name='المحتوى')
    attachment = models.FileField(upload_to='community/', blank=True, null=True, verbose_name='المرفق')
    likes_count = models.IntegerField(default=0, verbose_name='عدد الإعجابات')
    comments_count = models.IntegerField(default=0, verbose_name='عدد التعليقات')
    is_approved = models.BooleanField(default=True, verbose_name='موافق عليه')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ النشر')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        verbose_name = 'منشور'
        verbose_name_plural = 'المنشورات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.author.full_name}'


# نموذج التعليقات على المنشورات
class Comment(models.Model):
    """يمثل تعليقاً على منشور في المجتمع"""
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments', verbose_name='المنشور')
    author = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='comments', verbose_name='الكاتب')
    content = models.TextField(verbose_name='المحتوى')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.full_name}: {self.content[:50]}'


# نموذج تقييمات الشركات من قبل المتدربين
class CompanyRating(models.Model):
    """يسمح للمتدربين بتقييم الشركات التي تدربوا فيها، بحد أقصى تقييم واحد لكل متدرب لكل شركة"""
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='ratings', verbose_name='الشركة')
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='company_ratings', verbose_name='المتدرب')
    score = models.IntegerField(verbose_name='التقييم')
    review = models.TextField(verbose_name='المراجعة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'تقييم شركة'
        verbose_name_plural = 'تقييمات الشركات'
        # ضمان عدم تكرار التقييم من نفس المتدرب لنفس الشركة
        unique_together = ['company', 'trainee']

    def __str__(self):
        return f'{self.trainee.person.full_name} يقيّم {self.company.company_name} ({self.score}/5)'
