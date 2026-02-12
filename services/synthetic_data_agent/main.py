from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import FastAPI
from faker import Faker

from platform_shared import a2a, config, firestore, pubsub
from platform_shared.pubsub_models import PubSubEnvelope
from platform_shared.pubsub_utils import decode_pubsub_message


fake = Faker("en_US")
app = FastAPI()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


def _generate_vendor() -> Dict[str, str]:
    return {
        "name": fake.company(),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "postalCode": fake.postcode(),
        "country": "US",
    }


def _generate_invoices(quantity: int) -> List[Dict]:
    invoices = []
    for _ in range(quantity):
        invoice_date = datetime.utcnow() - timedelta(days=fake.random_int(min=31, max=120))
        due_date = invoice_date + timedelta(days=30)
        invoices.append(
            {
                "invoiceNumber": fake.bothify(text="INV-#####"),
                "invoiceDate": invoice_date.date().isoformat(),
                "dueDate": due_date.date().isoformat(),
                "paymentTerms": "NET_30",
                "paymentStatus": "Unpaid",
                "lineItems": [
                    {
                        "description": fake.bs().capitalize(),
                        "quantity": fake.random_int(min=1, max=5),
                        "unitPrice": round(fake.pyfloat(min_value=50, max_value=500), 2),
                    }
                ],
                "currency": "USD",
            }
        )
    return invoices


@app.post("/pubsub/push")
async def handle_message(envelope: PubSubEnvelope) -> Dict[str, str]:
    message = decode_pubsub_message(envelope.message.data)
    if message.taskType != config.TOPIC_APIS_DISCOVERED:
        return {"status": "ignored"}
    plan = message.payload.get("plan", {})
    intent = plan.get("intent", {})
    quantity = int(intent.get("quantity", 1))

    data = {
        "vendor": _generate_vendor(),
        "invoices": _generate_invoices(quantity),
    }

    existing = firestore.get_context(message.contextId) or {}
    trace = existing.get("trace", []) + ["synthetic_data"]
    firestore.upsert_context(
        message.contextId,
        {
            "status": "data_generated",
            "data": data,
            "trace": trace,
        },
    )

    next_message = a2a.build_message(
        message.contextId,
        config.TOPIC_DATA_GENERATED,
        {"data": data, "plan": plan},
    )
    pubsub.publish_message(config.TOPIC_DATA_GENERATED, next_message.model_dump())
    return {"status": "ok"}
