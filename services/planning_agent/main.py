from __future__ import annotations

from typing import Dict, List

from fastapi import FastAPI

from platform_shared import a2a, config, firestore, pubsub
from platform_shared.pubsub_models import PubSubEnvelope
from platform_shared.pubsub_utils import decode_pubsub_message


app = FastAPI()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/pubsub/push")
async def handle_message(envelope: PubSubEnvelope) -> Dict[str, str]:
    message = decode_pubsub_message(envelope.message.data)
    if message.taskType != config.TOPIC_SCENARIO_INTERPRETED:
        return {"status": "ignored"}
    intent = message.payload

    steps: List[Dict] = [
        {"stepId": "create_vendor", "action": "create", "object": "Vendor", "dependsOn": []},
        {"stepId": "create_invoice", "action": "create", "object": "Invoice", "dependsOn": ["create_vendor"]},
        {"stepId": "leave_unpaid", "action": "update", "object": "Invoice", "dependsOn": ["create_invoice"]},
        {"stepId": "verify_overdue", "action": "verify", "object": "Invoice", "dependsOn": ["leave_unpaid"]},
    ]

    plan = {"steps": steps, "intent": intent}

    existing = firestore.get_context(message.contextId) or {}
    trace = existing.get("trace", []) + ["planning"]
    firestore.upsert_context(
        message.contextId,
        {
            "status": "planned",
            "plan": plan,
            "trace": trace,
        },
    )

    next_message = a2a.build_message(
        message.contextId,
        config.TOPIC_WORKFLOW_PLANNED,
        plan,
    )
    pubsub.publish_message(config.TOPIC_WORKFLOW_PLANNED, next_message.model_dump())
    return {"status": "ok"}
