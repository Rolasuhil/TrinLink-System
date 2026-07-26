"""
ملف مسارات URL الرئيسي لمشروع TrainLink
يحدد جميع مسارات API والصفحات الثابتة ولوحة الإدارة
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
import os

# ============================================================
# مجلد الواجهة الأمامية (Frontend)
# يُستخدم لخدمة ملفات HTML/CSS/JS الثابتة
# ============================================================
FRONTEND_DIR = os.path.join(settings.BASE_DIR.parent, 'frontend')


# ============================================================
# دالة لخدمة ملفات الواجهة الأمامية
# تُعيد ملفات HTML/CSS/JS من مجلد frontend/
# ============================================================
def serve_frontend(request, path=''):
    from django.http import FileResponse, Http404
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(file_path):
        return static_serve(request, path, document_root=FRONTEND_DIR)
    raise Http404


from django.shortcuts import redirect


# ============================================================
# قائمة مسارات URL الرئيسية
# ============================================================
urlpatterns = [
    # --- الصفحة الرئيسية: إعادة توجيه للصفحة الأولى ---
    path('', lambda r: redirect('pages/public/01-home.html'), name='home'),

    # --- لوحة إدارة Django ---
    path('admin/', admin.site.urls),

    # --- مسارات API للتطبيقات ---
    path('api/auth/', include('accounts.urls')),        # API المصادقة والحسابات
    path('api/internships/', include('internships.urls')),  # API التدريب العملي
    path('api/chat/', include('messaging.urls')),       # API المراسلة
    path('api/community/', include('community.urls')),  # API المجتمع
    path('api/performance/', include('performance.urls')),  # API الأداء والتقييم
    path('api/ai/', include('ai_engine.urls')),         # API الذكاء الاصطناعي
    path('api/admin-panel/', include('admin_panel.urls')),  # API لوحة الإدارة

    # --- مسارات خدمة ملفات الواجهة الأمامية ---
    re_path(r'^(?P<path>pages/.*)$', serve_frontend, name='frontend'),        # صفحات HTML
    re_path(r'^(?P<path>css/.*)$', serve_frontend, name='frontend-css'),      # ملفات CSS
    re_path(r'^(?P<path>js/.*)$', serve_frontend, name='frontend-js'),        # ملفات JavaScript
    re_path(r'^(?P<path>assets/.*)$', serve_frontend, name='frontend-assets'), # الأصول الثابتة (صور، خطوط)
]

# ============================================================
# في وضع التطوير: خدمة ملفات الوسائط والثابتة عبر Django
# ============================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    # ملفات الوسائط المرفوعة
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # الملفات الثابتة
