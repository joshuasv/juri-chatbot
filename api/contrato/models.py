from django.db import models
from django.conf import settings


class Contrato(models.Model):
  
  vendor_name = models.CharField(max_length=100, null=True, blank=True)
  vendor_dni = models.CharField(max_length=9, null=True, blank=True)
  vendor_address = models.CharField(max_length=150, null=True, blank=True)
  vendor_province = models.CharField(max_length=50, null=True, blank=True)
  buyer_name = models.CharField(max_length=50, null=True, blank=True)
  buyer_dni = models.CharField(max_length=9, null=True, blank=True)
  buyer_address = models.CharField(max_length=150, null=True, blank=True)
  buyer_province = models.CharField(max_length=50, null=True, blank=True)
  vehicle_brand = models.CharField(max_length=50, null=True, blank=True)
  vehicle_plate = models.CharField(max_length=20, null=True, blank=True)
  vehicle_chassis_nb = models.CharField(max_length=8, null=True, blank=True)
  vehicle_kms = models.FloatField(null=True, blank=True)
  vehicle_value = models.FloatField(null=True, blank=True)
  insurance_date = models.DateField(null=True, blank=True)
  court = models.CharField(max_length=50, null=True, blank=True)
  vendor_signature = models.TextField(null=True, blank=True)
  buyer_signature = models.TextField(null=True, blank=True)
  path = models.FilePathField(path=settings.MEDIA_ROOT, null=True, blank=True)

  

  def __str__(self):
    return f"{self.vendor_name}"
  
