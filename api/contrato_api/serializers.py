from rest_framework import serializers
from contrato.models import Contrato

class ContratoSerializer(serializers.ModelSerializer):

  class Meta:
    model = Contrato
    fields = (
      'id', 
      'vendor_name', 
      'vendor_dni',
      'vendor_address',
      'vendor_province',
      'buyer_name', 
      'buyer_dni',
      'buyer_address',
      'buyer_province',
      'vehicle_brand',
      'vehicle_plate',
      'vehicle_chassis_nb',
      'vehicle_kms',
      'vehicle_value',
      'insurance_date',
      'court',
      'vendor_signature',
      'buyer_signature',
      )
