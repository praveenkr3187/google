from __future__ import annotations

from datetime import date
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


def _is_overdue(invoice: Dict) -> bool:
    due_date = date.fromisoformat(invoice.get("dueDate"))
    status = invoice.get("paymentStatus")
    return due_date < date.today() and status != "Paid"


@app.post("/pubsub/push")
async def handle_message(envelope: PubSubEnvelope) -> Dict[str, str]:
    message = decode_pubsub_message(envelope.message.data)
    if message.taskType != config.TOPIC_WORKFLOW_EXECUTED:
        return {"status": "ignored"}
    execution = message.payload
    invoice_ids = execution.get("invoiceIds", [])

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{config.SAP_MOCK_BASE_URL}/invoices")
        resp.raise_for_status()
        all_invoices = resp.json()

    overdue_ids: List[str] = []
    for invoice in all_invoices:
        if invoice.get("id") in invoice_ids and _is_overdue(invoice):
            overdue_ids.append(invoice.get("id"))

    result = {"overdueInvoiceIds": overdue_ids, "verified": len(overdue_ids) == len(invoice_ids)}

    existing = firestore.get_context(message.contextId) or {}
    trace = existing.get("trace", []) + ["verification"]
    firestore.upsert_context(
        message.contextId,
        {
            "status": "completed",
            "result": result,
            "trace": trace,
        },
    )

    next_message = a2a.build_message(
        message.contextId,
        config.TOPIC_WORKFLOW_COMPLETED,
        result,
    )
    pubsub.publish_message(config.TOPIC_WORKFLOW_COMPLETED, next_message.model_dump())
    return {"status": "ok"}
