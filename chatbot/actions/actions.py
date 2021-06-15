# This files contains your custom actions which can be used to run
# custom Python code.

import re
import json
import requests
import datetime
import editdistance

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.types import DomainDict


BASE_URL = "http://127.0.0.1:8001"
BASE_URL_API = "http://127.0.0.1:8001/api/"



# https://www.carqueryapi.com/api/0.3/?callback=?&cmd=getModels&make=audi

def calculate_editdistance(sentence, elements):
  to_ret = None
  start = None
  end = None
  scores = {}
  for word in sentence.split(" "):
    scores[word] = { "score": 999, "data": None }
    for element in elements:
      distance = editdistance.eval(word.lower(), element.lower())
      if distance < scores[word]['score']:
        scores[word]['score'] = distance
        scores[word]['data'] = element
  # Select the lowest
  lowest = 999 
  for item, data in scores.items():
    if data['score'] < lowest:
      lowest = data['score']
      to_ret = data['data']
      start, end = re.search(item, sentence).span()

  return to_ret, (start, end)
  

class ActionChangeSlot(Action):


  text_mappings = {
    "vendor_name": "el nombre del vendedor",
    "vendor_dni": "el DNI del vendedor",
    "vendor_address": "la dirección del vendedor",
    "vendor_province": "la provincia del vendedor",
    "buyer_name": "el nombre del comprador",
    "buyer_dni": "el DNI del comprador",
    "buyer_address": "la dirección del comprador",
    "buyer_province": "la provincia del comprador",
    "vehicle_brand": "la marca del coche",
    "vehicle_plate": "la matrícula del coche",
    "vehicle_chassis_nb": "el nº de bastidor",
    "vehicle_kms": "los kilómetros que tiene el coche",
    "vehicle_price": "el precio de venta del coche",
    "insurance_date": "la fecha de validez del seguro",
    #"court": "los Juzgados y Tribunales"
  }
  
  def name(self):
    return "action_change_slot"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
  
    slot_to_change = tracker.slots['slot_to_change'] 
    
    text = "¡Vaya! Veo que quieres cambiar {0}".format(self.text_mappings[slot_to_change])
    dispatcher.utter_message(text=text)

    return [
      SlotSet(key=slot_to_change, value=None),
      SlotSet(key="requested_slot", value=slot_to_change)
    ]



class ActionCreateContract(Action):
  
  def name(self):
    return "action_create_contract"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
    # If contract_id slot was filled do nothing 
    if tracker.slots['contract_id'] == None:
      
      response = requests.post(BASE_URL_API)
      
      # check if request was successful
      if response.status_code == 201:
        contract_id = json.loads(response.text)['id']

        return [SlotSet(key="contract_id", value=contract_id)]
      else:
        text = "Hubo un error de conexión."
        dispatcher.utter_message(text=text)
        
        return []
    else: # if contract_id slot is not empty
      # check if user really wants to create a new contract 
      return [FollowupAction(name="action_confirm_new_contract")]
    
    return []


class ActionSubmitForm(Action):

  def name(self) -> Text:
    return "action_submit_form"

  async def run(
    self,
    dispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    contract_id = tracker.slots['contract_id']
    
    if contract_id != None and contract_id != '':
      # Save current slots to API
      data = {
        "vendor_name": tracker.slots['vendor_name'],
        "vendor_dni": tracker.slots['vendor_dni'],
        "vendor_address": tracker.slots['vendor_address'],
        "vendor_province": tracker.slots['vendor_province'],
        "buyer_name": tracker.slots['buyer_name'],
        "buyer_dni": tracker.slots['buyer_dni'],
        "buyer_address": tracker.slots['buyer_address'],
        "buyer_province": tracker.slots['buyer_province'],
        "vehicle_brand": tracker.slots['vehicle_brand'],
        "vehicle_plate": tracker.slots['vehicle_plate'],
        "vehicle_chassis_nb": tracker.slots['vehicle_chassis_nb'],
        "vehicle_kms": tracker.slots['vehicle_kms'],
        "vehicle_value": tracker.slots['vehicle_value'],
        "insurance_date": datetime.datetime.strptime(tracker.slots['insurance_date'], "%Y-%m-%d").date(),
        "court": tracker.slots['court'],
        "vendor_signature": tracker.slots['vendor_signature'],
        "buyer_signature": tracker.slots['buyer_signature']
      }
      response = requests.put(BASE_URL_API + "update/" + str(contract_id),
        data=data)

      if response.status_code == 200:
        # Generate the PDF and display a message with its URL
        data = {"pk": tracker.slots['contract_id']}
        response = requests.post(BASE_URL_API + "generate", json=data)
        
        data = json.loads(response.text)
        if "url" in data:
          url = data['url']
          text = f'Aquí está el documento: <a href="{BASE_URL}{url}" target="_blank">{BASE_URL}{url}</a>'
          dispatcher.utter_message(text=text)
    
      return []

class ValidateContractForm(FormValidationAction):
  
  def name(self):
    return "validate_contract_form"

  async def required_slots(
    self,
    slots_mapped_in_domain: List[Text],
    dispatcher: "CollectingDispatcher",
    tracker: "Tracker",
    domain: "DomainDict",
    ) -> Optional[List[Text]]:
    
    extra = [
      "vendor_name", 
      "vendor_dni",
      "vendor_address", 
      "vendor_province",
      "buyer_name",
      "buyer_dni",
      "buyer_address",
      "buyer_province",
      "vehicle_brand",
      "vehicle_plate",
      "vehicle_chassis_nb",
      "vehicle_kms",
      "vehicle_value",
      "insurance_date",
      "vendor_signature",
      "buyer_signature"
    ]
   
    return extra + slots_mapped_in_domain

  def extract_vendor_name(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:

    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}

    if not tracker.slots.get('requested_slot') == "vendor_name":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "PER" and entity['extractor'] == "SpacyEntityExtractor":
        value = entity['value']

    tracker.slots['slot_to_change'] = None
    return { "vendor_name":  value }

  async def extract_vendor_dni(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      

    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      
    if not tracker.slots.get('requested_slot') == "vendor_dni":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "dni" and entity['extractor'] == "RegexEntityExtractor":
        value = entity['value']

    tracker.slots['slot_to_change'] = None
    return { "vendor_dni": value }


  async def extract_vendor_address(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      

    abreviations = {
      "Avenida": [r"[Aa]vda\.?", r"[Aa]v\.?",r"[Aa]venida"],
      "Calle": [r"[Cc]/?", r"[Cc]\.?", r"[Cc]l\.?", r"[Cc]alle"],
      "Paseo": [r"p\.?º?", r"[Pp]aseo"]
    }

    floor = r"[0-9](º|ª)?\s*[a-zA-Z]"
    
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      
    if not tracker.slots.get('requested_slot') == "vendor_address":
      return {}

    value = None
    street_number = None
    closest_st_nb = 999 
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "LOC" and entity['extractor'] == "SpacyEntityExtractor":
        value = entity['value']
        st_name_start = entity['start']
        st_name_end = entity['end']
      if entity['entity'] == "number" and entity['extractor'] == "DucklingEntityExtractor":
        # Get the closest value to the street name
        st_nb_start = entity['start']
        st_nb_end = entity['end']
        if st_name_end:
          dist = abs(st_name_end - st_nb_start)
          if dist < closest_st_nb:
            closest_st_nb = dist
            street_number = entity['value']

    if not value:
      for entity in entities:
        if entity['entity'] == "PER" and entity['extractor'] == "SpacyEntityExtractor":
          value = entity['value']
    st_type = "" 
    bajo = ""
    piso = ""
    for word in tracker.latest_message['text'].split(" "):
      # Check for street abreviations
      for abrev, l in abreviations.items():
        for regex_str in l:
          regex = re.compile("^" + regex_str + "$")
          if regex.match(word):
            st_type = word
            break
        if st_type != "":
          break
      if st_type != "":
        break
      
    for word in tracker.latest_message['text'].split(" "):
      # Check if it's bajo
      if re.compile(r"^[Bb]ajo$").match(word):
        bajo = "Bajo"
    # Check if it has floor
    check_floor = re.compile(floor).search(tracker.latest_message['text']) 
    if check_floor != None:
      piso = check_floor.group()   
    
    if street_number:
      address = f"{value}, {street_number}"
    else:
      address = value 
    if st_type != "" and not st_type in address:
      address = st_type + " " + address

    if piso != "":
      address = address + " " + piso.upper()
    elif bajo != "":
      address = address + " " + bajo

    tracker.slots['slot_to_change'] = None
    return { "vendor_address": address }

  async def extract_vendor_province(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:

    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      
    if not tracker.slots.get('requested_slot') == "vendor_province":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "province" and entity['extractor'] == "RegexEntityExtractor":
        value = entity['value']
    
    # We didn't find any matches, calculate the editdistance between 
    # the provinces and all the words in the message
    if not value:
      provinces = ["Coruña", "Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Baleares", "Barcelona", "Burgos", "Cáceres", "Cádiz", "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca", "Girona", "Granada", "Guadalajara", "Gipuzkoa", "Huelva", "Huesca", "Jaén", "La Rioja", "Las Palmas", "León", "Lérida", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra", "Ourense", "Palencia", "Pontevedra", "Salamanca", "Segovia", "Sevilla", "Soria", "Tarragona", "Santa Cruz de Tenerife", "Teruel", "Toledo", "Valencia", "Valladolid", "Vizcaya", "Zamora", "Zaragoza", "Ceuta", "Melilla"]
      message = tracker.latest_message['text']
      value, _ = calculate_editdistance(message, provinces)

    tracker.slots['slot_to_change'] = None
    return { "vendor_province": value }

  async def extract_buyer_name(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      

    if not tracker.slots.get('requested_slot') == "buyer_name":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "PER" and entity['extractor'] == "SpacyEntityExtractor":
        value = entity['value']

    tracker.slots['slot_to_change'] = None
    return { "buyer_name":  value }


  async def extract_buyer_address(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      
    if not tracker.slots.get('requested_slot') == "buyer_address":
      return {}

    value = None
    street_number = None
    spacy_ents = []
    
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "LOC" and entity['extractor'] == "SpacyEntityExtractor":
        value = entity['value']
      if entity['entity'] == "number" and entity['extractor'] == "DucklingEntityExtractor" and value != None:
        street_number = entity['value']

    if street_number:
      address = f"{value}, {street_number}"
    else:
      address = value 
    
    tracker.slots['slot_to_change'] = None
    return { "buyer_address": address }

  async def extract_buyer_dni(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      
      
    if not tracker.slots.get('requested_slot') == "buyer_dni":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "dni" and entity['extractor'] == "RegexEntityExtractor":
        value = entity['value']

    tracker.slots['slot_to_change'] = None
    return { "buyer_dni": value }

  async def extract_buyer_province(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:

    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      
    if not tracker.slots.get('requested_slot') == "buyer_province":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "province" and entity['extractor'] == "RegexEntityExtractor":
        value = entity['value']
    
    # We didn't find any matches, calculate the editdistance between 
    # the provinces and all the words in the message
    if not value:
      provinces = ["Coruña", "Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Baleares", "Barcelona", "Burgos", "Cáceres", "Cádiz", "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca", "Girona", "Granada", "Guadalajara", "Gipuzkoa", "Huelva", "Huesca", "Jaén", "La Rioja", "Las Palmas", "León", "Lérida", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra", "Ourense", "Palencia", "Pontevedra", "Salamanca", "Segovia", "Sevilla", "Soria", "Tarragona", "Santa Cruz de Tenerife", "Teruel", "Toledo", "Valencia", "Valladolid", "Vizcaya", "Zamora", "Zaragoza", "Ceuta", "Melilla"]
      message = tracker.latest_message['text']
      value, _ = calculate_editdistance(message, provinces)

    tracker.slots['slot_to_change'] = None
    return { "buyer_province": value }

  async def extract_vehicle_brand(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      
    if not tracker.slots.get('requested_slot') == "vehicle_brand":
      return {}
    
    value = None
    start = None
    end = 0 
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "brand" and entity['extractor'] == 'RegexEntityExtractor':
        value = entity['value']
        start = entity['start']
        end = entity['end']

        
    if not value:
      vehicle_brands = ["Abarth", "Alfa Romeo", "Aston Martin", "Audi", "Austin", "Bentley", "Bmw", "Cadillac", "Chevrolet", "Chrysler", "Citroen", "Dacia", "Daewoo", "Daihatsu", "Dodge", "Ferrari", "Fiat", "Ford", "Galloper", "Honda", "Hummer", "Hyundai", "Infiniti", "Isuzu", "Jaguar", "Jeep", "Kia", "Lada", "Lamborghini", "Lancia", "Land Rover", "Lexus", "Lotus", "Maserati", "Mazda", "Mercedes-Benz", "Mercedes", "MG", "Mini", "Mitsubishi", "Nissan", "Opel", "Peugeot", "Pontiac", "Porsche", "Renault", "Rolls-Royce", "Rover", "Saab", "Seat", "Skoda", "Smart", "Ssangyong", "Subaru", "Suzuki", "Talbot", "Tata", "Toyota", "Volkswagen", "Volvo"] 
      message = tracker.latest_message['text']
      value, (start, end) = calculate_editdistance(message, vehicle_brands)
      
    # Try to grab the model from the text 
    message = tracker.latest_message['text'][end:]
    # Make car API call
    headers = { "User-Agent": "PostmanRuntime/7.26.8" }
    brands = requests.get("https://www.carqueryapi.com/api/0.3/?callback=?&cmd=getModels&make="+value.lower(), headers=headers) 
    if brands.status_code == 200:
      brand_data = json.loads(brands.text[2:len(brands.text)-2])["Models"]
      models = [model['model_name'] for model in brand_data]
      # Search for a model in the message
      possible_model = None
      for model in models:
        found = re.search(model.replace(" ", "").lower(), message.replace(" ", "").lower())
        if found:
          possible_model = model     
          break
      # If not model found try find one with closest distance
      if not possible_model:
        possible_model, _ = calculate_editdistance(message, models)
      
    if possible_model:
      value = value + " " + possible_model

    tracker.slots['slot_to_change'] = None
    return { "vehicle_brand": value }
    
  async def extract_vehicle_plate(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
      
    if not tracker.slots.get('requested_slot') == "vehicle_plate":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "plate" and entity['extractor'] == "RegexEntityExtractor":
        value = entity['value']

        # Remove unwanted characters
        if value != None:
          value = value.replace(" ", "").replace("-", "").upper()

    tracker.slots['slot_to_change'] = None
    return { "vehicle_plate": value }

  async def extract_vehicle_chassis_nb(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
    
    if not tracker.slots.get('requested_slot') == "vehicle_chassis_nb":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "chassis_nb" and entity['extractor'] == 'RegexEntityExtractor':
        value = entity['value']

    tracker.slots['slot_to_change'] = None
    return { "vehicle_chassis_nb": value }


  async def extract_vehicle_kms(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
    
    if not tracker.slots.get('requested_slot') == "vehicle_kms":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "distance" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
      elif entity['entity'] == "number" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
    tracker.slots['slot_to_change'] = None
    return { "vehicle_kms": value }

  async def extract_vehicle_value(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
    
    if not tracker.slots.get('requested_slot') == "vehicle_value":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "amount-of-money" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
      elif entity['entity'] == "number" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
    tracker.slots['slot_to_change'] = None
    return { "vehicle_value": value }

  async def extract_insurance_date(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if tracker.latest_message['intent']['name'] == "change_slot" and tracker.latest_message['intent']['confidence'] > .99 and tracker.slots['slot_to_change'] != None:
      return {}
    
    if not tracker.slots.get('requested_slot') == "insurance_date":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "time" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
        value = value.split("T")[0]

    tracker.slots['slot_to_change'] = None
    return { "insurance_date": value }
