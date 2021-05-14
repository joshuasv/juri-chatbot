from django.contrib import admin
from . import models

@admin.register(models.Contrato)
class ContratoAdmin(admin.ModelAdmin):
  list_display = (
    'id', 
    'vendor_name', 
    'vendor_dni', 
    'vendor_province')
