from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('contrato.urls', namespace='contrato')),
    path('admin/', admin.site.urls),
    path('api/', include('contrato_api.urls', namespace='contrato_api')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
