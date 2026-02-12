from __future__ import annotations

from typing import Dict, List

from fastapi import FastAPI

from platform_shared import a2a, config, firestore, pubsub
from platform_shared.knowledge_graph import KnowledgeGraphClient
from platform_shared.pubsub_models import PubSubEnvelope
from platform_shared.pubsub_utils import decode_pubsub_message


app = FastAPI()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/pubsub/push")
async def handle_message(envelope: PubSubEnvelope) -> Dict[str, str]:
    message = decode_pubsub_message(envelope.message.data)
    if message.taskType != config.TOPIC_WORKFLOW_PLANNED:
        return {"status": "ignored"}
    plan = message.payload
    intent = plan.get("intent", {})
    objects: List[str] = intent.get("objects", ["Vendor", "Invoice"])

    kg = KnowledgeGraphClient()
    apis = [api.model_dump() for api in kg.discover_apis(objects)]
    kg.close()

    payload = {"apis": apis, "plan": plan}

    existing = firestore.get_context(message.contextId) or {}
    trace = existing.get("trace", []) + ["api_reasoning"]
    firestore.upsert_context(
        message.contextId,
        {
            "status": "apis_discovered",
            "apis": apis,
            "trace": trace,
        },
    )

    next_message = a2a.build_message(
        message.contextId,
        config.TOPIC_APIS_DISCOVERED,
        payload,
    )
    pubsub.publish_message(config.TOPIC_APIS_DISCOVERED, next_message.model_dump())
    return {"status": "ok"}
