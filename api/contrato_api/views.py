from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from contrato.models import Contrato
from contrato.services import ContractPDF
from .serializers import ContratoSerializer


"""
 View that craetes items
"""
class Post(generics.CreateAPIView):
  serializer_class = ContratoSerializer


class Update(generics.UpdateAPIView):
  queryset = Contrato.objects.all()
  serializer_class = ContratoSerializer

class GeneratePDF(APIView):
  """
  View that generates a contract PDF.
  """

  def post(self, request, format=None):
    
    # Get the contract ID from the request
    if request.content_type == "application/json":
      if "pk" in request.data:
        contract_path = ContractPDF.generate(request.data['pk'])

        return Response({"url": contract_path})

"""
 View that gets one item
"""
class Retrieve(generics.RetrieveAPIView):
  queryset = Contrato.objects.all()
  serializer_class = ContratoSerializer

