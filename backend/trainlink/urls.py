from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
import os

FRONTEND_DIR = os.path.join(settings.BASE_DIR.parent, 'frontend')


def serve_frontend(request, path=''):
    from django.http import FileResponse, Http404
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(file_path):
        return static_serve(request, path, document_root=FRONTEND_DIR)
    raise Http404


from django.shortcuts import redirect


urlpatterns = [
    path('', lambda r: redirect('pages/public/01-home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/internships/', include('internships.urls')),
    path('api/chat/', include('messaging.urls')),
    path('api/community/', include('community.urls')),
    path('api/performance/', include('performance.urls')),
    path('api/ai/', include('ai_engine.urls')),
    path('api/admin-panel/', include('admin_panel.urls')),
    re_path(r'^(?P<path>pages/.*)$', serve_frontend, name='frontend'),
    re_path(r'^(?P<path>css/.*)$', serve_frontend, name='frontend-css'),
    re_path(r'^(?P<path>js/.*)$', serve_frontend, name='frontend-js'),
    re_path(r'^(?P<path>assets/.*)$', serve_frontend, name='frontend-assets'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
