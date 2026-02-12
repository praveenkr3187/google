from __future__ import annotations

from typing import Dict, Optional
from pydantic import BaseModel


class PubSubMessage(BaseModel):
    data: str
    attributes: Optional[Dict[str, str]] = None
    messageId: Optional[str] = None
    publishTime: Optional[str] = None


class PubSubEnvelope(BaseModel):
    message: PubSubMessage
    subscription: Optional[str] = None
