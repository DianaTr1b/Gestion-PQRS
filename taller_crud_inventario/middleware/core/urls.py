from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .import views as project_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', project_views.login_view, name='login'),
    path('logout/', project_views.logout_view, name='logout'),
    path('',RedirectView.as_view(url='/inventario/', permanent=False)),
    path('inventario/',include('apps.inventario.urls')),
    path('api/sync/',include('apps.usuarios.urls')),
]
# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)