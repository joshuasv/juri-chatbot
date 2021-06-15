from .models import Contrato

import datetime
import uuid
import base64
from io import BytesIO

from django.conf import settings
from django.db.models import Q

import PIL.Image

from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
import reportlab.platypus


MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


class ContractPDF(object):
  
  
  @staticmethod
  def generate(contract_id):
    
    # Check that all fields are filled (excluding path)
    contract_data = Contrato.objects \
      .filter(pk=contract_id) \
      .filter(vendor_name__isnull=False) \
      .filter(vendor_dni__isnull=False) \
      .filter(vendor_address__isnull=False) \
      .filter(vendor_province__isnull=False) \
      .filter(buyer_name__isnull=False) \
      .filter(buyer_dni__isnull=False) \
      .filter(buyer_address__isnull=False) \
      .filter(buyer_province__isnull=False) \
      .filter(vehicle_brand__isnull=False) \
      .filter(vehicle_plate__isnull=False) \
      .filter(vehicle_chassis_nb__isnull=False) \
      .filter(vehicle_kms__isnull=False) \
      .filter(vehicle_value__isnull=False) \
      .filter(insurance_date__isnull=False) \
      .filter(vendor_signature__isnull=False) \
      .filter(buyer_signature__isnull=False)
   
    if contract_data != None and len(contract_data) == 1:
      # Get the first element of the queryset
      contract_data = contract_data[0] 
      
      # Populate contract   
      now = datetime.datetime.now()
      content = ContractPDF.populate_content(
        contract_data.vendor_province,
        now.day,
        MONTHS[now.month],
        now.year,
        ':'.join(str(now.time()).split(":")[0:2]),
        contract_data.vendor_name,
        contract_data.vendor_dni,
        contract_data.vendor_address,
        contract_data.vendor_province,
        contract_data.buyer_name,
        contract_data.buyer_dni,
        contract_data.buyer_address,
        contract_data.buyer_province,
        contract_data.vehicle_brand,
        contract_data.vehicle_plate,
        contract_data.vehicle_chassis_nb,
        contract_data.vehicle_kms,
        contract_data.vehicle_value,
        contract_data.insurance_date.strftime('%d/%m/%Y'),
        contract_data.court,
        contract_data.vendor_signature,
        contract_data.buyer_signature)

      filename = str(uuid.uuid4()) + ".pdf"
      doc = SimpleDocTemplate(
        str(settings.MEDIA_ROOT) + "/" + filename,
        pagesize=A4,
        rightMargin=32,
        leftMargin=32,
        topMargin=28,
        bottomMargin=0)

      try: 
        pdf = doc.build(content)

        print("PDF===>", pdf)
        # Set contract object path field the document filename
        contract_data.path = doc.filename 
        contract_data.save()
        print("====>", settings.MEDIA_URL + filename)
        
        return settings.MEDIA_URL + filename 

      except Exception as e:
        print("[ERROR] Failed to create PDF contract:")
        print(e)
      
  def populate_content(location, day, month, year, time, vendor_name, 
    vendor_dni, vendor_address, vendor_province, buyer_name, buyer_dni,
    buyer_address, buyer_province, vehicle_brand, vehicle_plate, 
    vehicle_chassis_nb, vehicle_kms, vehicle_value, insurance_date, 
    court, vendor_signature, buyer_signature):
    
    content = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    ptext = '<font size="15"><b>Contrato de compraventa de un vehículo usado entre particulares</b></font>'
    content.append(Paragraph(ptext, styles['Center']))
    content.append(Spacer(1,12))

    ptext = f'<font size="12">En {location} a {day} de {month} de {year} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp  HORA: {time}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,20))

    ptext = f'<font size="12"><b>Vendedor:</b></font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))

    ptext = f'<font size="12">D. {vendor_name}, con N.I.F. nº {vendor_dni}, y domicilio en {vendor_address}, calle de {vendor_province}</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,20))

    ptext = f'<font size="12"><b>Comprador:</b></font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))

    ptext = f'<font size="12">D. {buyer_name}, con N.I.F. nº {buyer_dni}, y domicilio en {buyer_address}, calle de {buyer_province}</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,20))

    ptext = f'<font size="12"><b>Vehículo:</b></font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))

    ptext = f'<font size="12">Marca: {vehicle_brand}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))
    ptext = f'<font size="12">Matrícula: {vehicle_plate}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))
    ptext = f'<font size="12">Nº de Bastidor: {vehicle_chassis_nb}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))
    ptext = f'<font size="12">Kilómetros: {vehicle_kms}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,20))


    ptext = '<font size="12">Reunidos vendedor y comprador en la fecha del encabezamiento, manifiestan haber acordado formalizar en este <b>documento CONTRATO DE COMPRAVENTA del vehículo automóvil</b> que se especifica, en las siguientes</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,6))

    ptext = '<font size="12"><b>CONDICIONES</b></font>'
    content.append(Paragraph(ptext, styles['Center']))
    content.append(Spacer(1,6))

    ptext = f'<font size="12"><b>1ª)</b> El vendedor vende al comprador el vehículo de su propiedad anteriormente especificado por la cantidad de {vehicle_value} euros, sin incluir los impuestos correspondientes, que serán a cargo del comprador.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12"><b>2ª)</b> El vendedor declara que no pesa sobre el vehículo ninguna carga o gravamen ni impuesto, deuda o sanción pendientes de abono en la fecha de la firma de este contrato, comprometiéndose en caso contrario a regularizar tal situación a su exclusivo cargo.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12"><b>3ª)</b> El vendedor se compromete a facilitar los distintos documentos relativos al vehículo, así como a firmar cuantos documentos aparte de éste sean necesarios para que el vehículo quede correctamente inscrito a nombre del comprador en los correspondientes organismos públicos, siendo todos los gastos a cargo del comprador.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12"><b>4ª)</b> Una vez realizada la correspondiente transferencia en Tráfico, el vendedor entregará materialmente al comprador la posesión del vehículo, haciéndose el comprador cargo de cuantas responsabilidades puedan contraerse por la propiedad del vehículo y su tenencia y uso a partir de dicho momento de la entrega.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = f'<font size="12"><b>5ª)</b> El vehículo dispone de seguro en vigor hasta fecha de {insurance_date} y se encuentra al corriente respecto a las obligaciones derivadas de la ITV (Inspección Técnica de Vehículos)</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12"><b>6ª)</b> El comprador declara conocer el estado actual del vehículo, por lo que exime al vendedor de garantía por vicios o defectos que surjan con posterioridad a la entrega, salvo aquellos ocultos que tengan su origen en dolo o mala fe del vendedor.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = f'<font size="12"><b>7ª)</b> Para cualquier litigio que surja entre las partes de la interpretación o cumplimiento del presente contrato, éstas, con expresa renuncia al fuero que pudiera corresponderles, se someterán a los Juzgados y Tribunales que corresponda.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12">Y para que así conste, firman el presente contrato de compraventa, por triplicado, en la fecha y lugar arriba indicados.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12">Firma del vendedor &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp Firma del comprador</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,76))

    signature = flowable_fig(base64_to_image(vendor_signature), False)
    content.append(signature)

    signature = flowable_fig(base64_to_image(buyer_signature), True)
    content.append(signature)
    
    return content



  #def create(self):
  #  
  #  
  #  content = []

  #  print("Creo el contrato...")

class flowable_fig(reportlab.platypus.Flowable):

  def __init__(self, imgdata, inline):
    reportlab.platypus.Flowable.__init__(self)
    self.img = reportlab.lib.utils.ImageReader(imgdata)
    self.inline = inline

  def draw(self):
    if self.inline:
      self.canv.drawImage(self.img, 250, 0, height=25*mm, width=60*mm)
    else:
      self.canv.drawImage(self.img, 0, 0, height=25*mm, width=60*mm)

def base64_to_image(imgstr):
  imgdata = base64.b64decode(imgstr)
  imgbytes = BytesIO(imgdata)
  image = PIL.Image.open(imgbytes)
  bg = PIL.Image.new("RGB", image.size, (255, 255, 255))
  bg.paste(image, image)
  return bg



  
