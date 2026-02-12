from __future__ import annotations

from typing import Dict

from .schemas import A2AMessage
from .utils import utc_now_iso


def build_message(context_id: str, task_type: str, payload: Dict) -> A2AMessage:
    return A2AMessage(
        contextId=context_id,
        taskType=task_type,
        payload=payload,
        timestamp=utc_now_iso(),
    )
