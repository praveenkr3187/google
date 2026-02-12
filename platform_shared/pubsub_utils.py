import base64
import json
from typing import Dict

from .schemas import A2AMessage


def decode_pubsub_message(encoded_data: str) -> A2AMessage:
    decoded = base64.b64decode(encoded_data).decode("utf-8")
    data: Dict = json.loads(decoded)
    return A2AMessage.model_validate(data)
