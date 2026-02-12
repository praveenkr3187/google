from __future__ import annotations

import re
from typing import Dict

from fastapi import FastAPI

from platform_shared import a2a, config, firestore, pubsub
from platform_shared.pubsub_models import PubSubEnvelope
from platform_shared.pubsub_utils import decode_pubsub_message


app = FastAPI()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


def _extract_quantity(text: str) -> int:
    match = re.search(r"\b(\d+)\b", text)
    if match:
        return int(match.group(1))
    return 1


@app.post("/pubsub/push")
async def handle_message(envelope: PubSubEnvelope) -> Dict[str, str]:
    message = decode_pubsub_message(envelope.message.data)
    if message.taskType != config.TOPIC_SCENARIO_RECEIVED:
        return {"status": "ignored"}
    scenario = message.payload.get("scenario", "")

    intent = {
        "product": "SAP Concur Invoice",
        "domain": "Accounts Payable",
        "objects": ["Vendor", "Invoice"],
        "goal": "Overdue" if "overdue" in scenario.lower() else "Create",
        "quantity": _extract_quantity(scenario),
    }

    existing = firestore.get_context(message.contextId) or {}
    trace = existing.get("trace", []) + ["intent"]
    firestore.upsert_context(
        message.contextId,
        {
            "status": "interpreted",
            "intent": intent,
            "trace": trace,
        },
    )

    next_message = a2a.build_message(
        message.contextId,
        config.TOPIC_SCENARIO_INTERPRETED,
        intent,
    )
    pubsub.publish_message(config.TOPIC_SCENARIO_INTERPRETED, next_message.model_dump())
    return {"status": "ok"}
