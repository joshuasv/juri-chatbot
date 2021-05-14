from django.urls import path
from django.views.generic import TemplateView

app_name = 'contrato'

urlpatterns = [
  path('', TemplateView.as_view(template_name='contrato/index.html')),
]
