from django.urls import path
from .views import Post, Retrieve, Update, GeneratePDF

app_name = 'contrato_api'

urlpatterns = [
  path('', Post.as_view(), name='create'),
  path('<int:pk>', Retrieve.as_view(), name='retrieve'),
  path('update/<int:pk>', Update.as_view(), name='update'),
  path('generate', GeneratePDF.as_view(), name='generate'),
]
