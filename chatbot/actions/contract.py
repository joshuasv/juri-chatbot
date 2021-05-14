import datetime
import base64
from io import BytesIO

import PIL.Image

from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
import reportlab.platypus

class Contract():
  
  def __init__(self, vendor_name, vendor_dni, vendor_address, 
    vendor_province, buyer_name, buyer_dni, buyer_address, 
    buyer_province, vehicle_brand, vehicle_plate, vehicle_chassis_nb, 
    vehicle_kms, vehicle_value, insurance_date, court, 
    vendor_signature, buyer_signature):

    now = datetime.datetime.now()
    self.location = vendor_province;
    self.day = now.day;
    self.month = now.month;
    self.year = now.year;
    self.time = ':'.join(str(now.time()).split(":")[0:2]) 
    self.vendor_name = vendor_name
    self.vendor_dni = vendor_dni
    self.vendor_address = vendor_address
    self.vendor_province = vendor_province
    self.buyer_name = buyer_name
    self.buyer_dni = buyer_dni
    self.buyer_address = buyer_address
    self.buyer_province = buyer_province
    self.vehicle_brand = vehicle_brand
    self.vehicle_plate = vehicle_plate
    self.vehicle_chassis_nb = vehicle_chassis_nb
    self.vehicle_kms = vehicle_kms
    self.vehicle_value = vehicle_value
    self.insurance_date = insurance_date
    self.court = court
    self.vendor_signature = vendor_signature
    self.buyer_signature = buyer_signature

  def create(self):
    
    doc = SimpleDocTemplate(
      "contrato-v2.pdf",
      pagesize=A4,
      rightMargin=32,
      leftMargin=32,
      topMargin=28,
      bottomMargin=0)
    
    content = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    
    # The actual content of the contract
    ptext = '<font size="15"><b>Contrato de compraventa de un vehículo usado entre particulares</b></font>'
    content.append(Paragraph(ptext, styles['Center']))
    content.append(Spacer(1,12))

    ptext = f'<font size="12">En {self.location} a {self.day} de {self.month} de {self.year} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp  HORA: {self.time}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,20))

    ptext = f'<font size="12"><b>Vendedor:</b></font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))

    ptext = f'<font size="12">D. {self.vendor_name}, con N.I.F. no {self.vendor_dni}, y domicilio en {self.vendor_address}, calle de {self.vendor_province}</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,20))

    ptext = f'<font size="12"><b>Comprador:</b></font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))

    ptext = f'<font size="12">D. {self.buyer_name}, con N.I.F. no {self.buyer_dni}, y domicilio en {self.buyer_address}, calle de {self.buyer_province}</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,20))

    ptext = f'<font size="12"><b>Vehículo:</b></font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))

    ptext = f'<font size="12">Marca: {self.vehicle_brand}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))
    ptext = f'<font size="12">Matrícula: {self.vehicle_plate}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))
    ptext = f'<font size="12">Nº de Bastidor: {self.vehicle_chassis_nb}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,6))
    ptext = f'<font size="12">Kilómetros: {self.vehicle_kms}</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,20))


    ptext = '<font size="12">Reunidos vendedor y comprador en la fecha del encabezamiento, manifiestan haber acordado formalizar en este <b>documento CONTRATO DE COMPRAVENTA del vehículo automóvil</b> que se especifica, en las siguientes</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,6))

    ptext = '<font size="12"><b>CONDICIONES</b></font>'
    content.append(Paragraph(ptext, styles['Center']))
    content.append(Spacer(1,6))

    ptext = f'<font size="12"><b>1ª)</b> El vendedor vende al comprador el vehículo de su propiedad anteriormente especificado por la cantidad de {self.vehicle_value} euros, sin incluir los impuestos correspondientes, que serán a cargo del comprador.</font>'
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

    ptext = f'<font size="12"><b>5ª)</b> El vehículo dispone de seguro en vigor hasta fecha de {self.insurance_date} y se encuentra al corriente respecto a las obligaciones derivadas de la ITV (Inspección Técnica de Vehículos)</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12"><b>6ª)</b> El comprador declara conocer el estado actual del vehículo, por lo que exime al vendedor de garantía por vicios o defectos que surjan con posterioridad a la entrega, salvo aquellos ocultos que tengan su origen en dolo o mala fe del vendedor.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = f'<font size="12"><b>7ª)</b> Para cualquier litigio que surja entre las partes de la interpretación o cumplimiento del presente contrato, éstas, con expresa renuncia al fuero que pudiera corresponderles, se someterán a los Juzgados y Tribunales de {self.court} </font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12">Y para que así conste, firman el presente contrato de compraventa, por triplicado, en la fecha y lugar arriba indicados.</font>'
    content.append(Paragraph(ptext, styles['Justify']))
    content.append(Spacer(1,10))

    ptext = '<font size="12">Firma del vendedor &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp Firma del comprador</font>'
    content.append(Paragraph(ptext, styles['Normal']))
    content.append(Spacer(1,76))

    signature = flowable_fig(base64_to_image(self.vendor_signature), False)
    content.append(signature)

    signature = flowable_fig(base64_to_image(self.buyer_signature), True)
    content.append(signature)

    doc.build(content)
    print("Creo el contrato...")

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



  
