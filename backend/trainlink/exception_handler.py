"""
معالج الأخطاء المخصص لـ Django REST Framework
يقوم بالتعامل مع أخطاء API وإعادة صيغة الردود بشكل موحد
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


# ============================================================
# دالة معالجة الأخطاء المخصصة
# تستقبل أي خطأ يحدث أثناء معالجة طلب API
# ============================================================
def custom_exception_handler(exc, context):
    # محاولة استخدام المعالج الافتراضي لـ DRF أولاً
    # يتعامل مع أخطاء المصادقة، الصلاحيات، التنسيق، إلخ
    response = exception_handler(exc, context)

    # إذا كان المعالج الافتراضي قد أرجع رداً (أي أنه تعرف على نوع الخطأ)
    if response is not None:
        return response  # إرجاع الرد بالشكل الافتراضي

    # إذا لم يتعرف المعالج الافتراضي على الخطأ (أخطاء غير متوقعة)
    # إرجاع رد خطأ عام مع رسالة الخطأ كنص
    return Response(
        {'error': str(exc)},  # تحويل الخطأ إلى نص ووضعه في حقل error
        status=status.HTTP_500_INTERNAL_SERVER_ERROR  # كود الحالة 500: خطأ داخلي في الخادم
    )
