import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

from rasa.shared.nlu.constants import (TEXT, METADATA)

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata

class TitleUtterance(Component):
  """
    This new component capitalizes the first letter of each word so the
    SpaCy Entity Recognizer is able recognize the PER entity used to 
    extract the name of the vendor and buyer.
  """
  
  @classmethod
  def required_components(cls) -> List[Type[Component]]:
    """Specify which components need to be present in the pipeline."""
    return []

  defaults = {}

  supported_language_list = None

  def __init__(
    self, 
    component_config: Optional[Dict[Text, Any]] = None) -> None:
    super().__init__(component_config)

  def train(
    self,
    training_data: TrainingData,
    config: Optional[RasaNLUModelConfig] = None,
    **kwargs: Any,
    ) -> None:
    pass

  def process(self, message: Message, **kwargs: Any) -> None:
    if message.get(TEXT) != None:
      message.set(TEXT, message.get(TEXT).title())

  @classmethod
  def load(
    cls,
    meta: Dict[Text, Any],
    model_dir: Text,
    model_metadata: Optional["Metadata"] = None,
    cached_component: Optional["Component"] = None,
    **kwargs: Any,
    ) -> "Component":

    if cached_component:
      return cached_component
    else:
      return cls(meta)
