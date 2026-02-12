from __future__ import annotations

from typing import Dict, List

from fastapi import FastAPI
import httpx

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
    if message.taskType != config.TOPIC_DATA_GENERATED:
        return {"status": "ignored"}
    payload = message.payload
    data = payload.get("data", {})

    vendor = data.get("vendor", {})
    invoices = data.get("invoices", [])

    async with httpx.AsyncClient(timeout=30.0) as client:
        vendor_resp = await client.post(f"{config.SAP_MOCK_BASE_URL}/vendors", json=vendor)
        vendor_resp.raise_for_status()
        vendor_id = vendor_resp.json().get("id")

        invoice_ids: List[str] = []
        for invoice in invoices:
            invoice_payload = {**invoice, "vendorId": vendor_id}
            invoice_resp = await client.post(
                f"{config.SAP_MOCK_BASE_URL}/invoices", json=invoice_payload
            )
            invoice_resp.raise_for_status()
            invoice_ids.append(invoice_resp.json().get("id"))

    result = {"vendorId": vendor_id, "invoiceIds": invoice_ids}

    existing = firestore.get_context(message.contextId) or {}
    trace = existing.get("trace", []) + ["execution"]
    firestore.upsert_context(
        message.contextId,
        {
            "status": "executed",
            "execution": result,
            "trace": trace,
        },
    )

    next_message = a2a.build_message(
        message.contextId,
        config.TOPIC_WORKFLOW_EXECUTED,
        result,
    )
    pubsub.publish_message(config.TOPIC_WORKFLOW_EXECUTED, next_message.model_dump())
    return {"status": "ok"}
