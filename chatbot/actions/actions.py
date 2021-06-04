# This files contains your custom actions which can be used to run
# custom Python code.

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
    
    #print("[SLOTS]", tracker.slots)
    #print("[LAST_MSG]", tracker.latest_message)
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
      "court",
      "vendor_signature",
      "buyer_signature"
    ]
    #extra=["vendor_province"]
    return extra
    
    return extra + slots_mapped_in_domain

  def extract_vendor_name(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:

    if not tracker.slots.get('requested_slot') == "vendor_name":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "PER" and entity['extractor'] == "SpacyEntityExtractor":
        value = entity['value']

    return { "vendor_name":  value }

  async def extract_vendor_dni(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if not tracker.slots.get('requested_slot') == "vendor_dni":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "dni" and entity['extractor'] == "RegexEntityExtractor":
        value = entity['value']

    return { "vendor_dni": value }


  async def extract_vendor_address(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if not tracker.slots.get('requested_slot') == "vendor_address":
      return {}

    value = None
    street_number = None
    
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
    
    return { "vendor_address": address }

  async def extract_vendor_province(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
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
      scores = {}
      for word in message.split(" "):
        scores[word] = {"score": 999, "prov": None}
        for prov in provinces:
          distance = editdistance.eval(word.lower(), prov.lower())
          if distance < scores[word]['score']:
            scores[word]['score'] = distance
            scores[word]['prov'] = prov
            
      # Select the lowest
      lowest = 999
      for item, data in scores.items():
        if data['score'] < lowest:
          lowest = data['score']
          value = data['prov']

    return { "vendor_province": value }

  async def extract_buyer_name(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:

    if not tracker.slots.get('requested_slot') == "buyer_name":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "PER" and entity['extractor'] == "SpacyEntityExtractor":
        value = entity['value']

    return { "buyer_name":  value }


  async def extract_buyer_address(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
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
    
    return { "buyer_address": address }

  async def extract_buyer_dni(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if not tracker.slots.get('requested_slot') == "buyer_dni":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "dni" and entity['extractor'] == "RegexEntityExtractor":
        value = entity['value']

    return { "buyer_dni": value }

  async def extract_buyer_province(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
      
    if not tracker.slots.get('requested_slot') == "buyer_province":
      return {}

    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "province" and entity['extractor'] == "RegexEntityExtractor":
        value = entity['value']

    return { "buyer_province": value }

  async def extract_vehicle_brand(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
    
    if not tracker.slots.get('requested_slot') == "vehicle_brand":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "brand" and entity['extractor'] == 'RegexEntityExtractor':
        value = entity['value']

    return { "vehicle_brand": value }
    
  async def extract_vehicle_plate(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
    
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

    return { "vehicle_plate": value }

  async def extract_vehicle_chassis_nb(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
    
    if not tracker.slots.get('requested_slot') == "vehicle_chassis_nb":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "chassis_nb" and entity['extractor'] == 'RegexEntityExtractor':
        value = entity['value']

    return { "vehicle_chassis_nb": value }


  async def extract_vehicle_kms(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
    
    if not tracker.slots.get('requested_slot') == "vehicle_kms":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "distance" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
      elif entity['entity'] == "number" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
    return { "vehicle_kms": value }

  async def extract_vehicle_value(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
    
    if not tracker.slots.get('requested_slot') == "vehicle_value":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "amount-of-money" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
      elif entity['entity'] == "number" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
    return { "vehicle_value": value }

  async def extract_insurance_date(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict) -> Dict[Text, Any]:
    
    if not tracker.slots.get('requested_slot') == "insurance_date":
      return {}
    
    value = None
    entities = tracker.latest_message['entities']
    for entity in entities:
      if entity['entity'] == "time" and entity['extractor'] == "DucklingEntityExtractor":
        value = entity['value']
        value = value.split("T")[0]

    return { "insurance_date": value }
