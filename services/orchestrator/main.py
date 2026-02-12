from __future__ import annotations

import base64
import json
import time
import uuid
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from platform_shared import a2a, config, firestore, pubsub
from platform_shared.pubsub_models import PubSubEnvelope, PubSubMessage


class ScenarioRequest(BaseModel):
    scenario: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/run-scenario")
async def run_scenario(request: ScenarioRequest) -> Dict[str, Any]:
    context_id = str(uuid.uuid4())
    firestore.upsert_context(
        context_id,
        {
            "contextId": context_id,
            "status": "received",
            "scenario": request.scenario,
        },
    )

    message = a2a.build_message(
        context_id,
        config.TOPIC_SCENARIO_RECEIVED,
        {"scenario": request.scenario},
    )

    if config.MOCK_PUBSUB:
        await _run_local_pipeline(message.model_dump())
    else:
        pubsub.publish_message(config.TOPIC_SCENARIO_RECEIVED, message.model_dump())

    deadline = time.time() + config.ORCHESTRATOR_TIMEOUT_SECONDS
    while time.time() < deadline:
        context = firestore.get_context(context_id)
        if context and context.get("status") == "completed":
            return {
                "contextId": context_id,
                "result": context.get("result", {}),
                "trace": context.get("trace", []),
            }
        if context and context.get("status") == "failed":
            raise HTTPException(status_code=500, detail=context.get("error", "failed"))
        time.sleep(1.0)

    raise HTTPException(status_code=504, detail="Workflow timed out")


async def _post_pubsub(url: str, payload: Dict[str, Any]) -> None:
    data = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    envelope = PubSubEnvelope(message=PubSubMessage(data=data))
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{url}/pubsub/push", json=envelope.model_dump())
        resp.raise_for_status()


async def _run_local_pipeline(initial_message: Dict[str, Any]) -> None:
    await _post_pubsub(config.INTENT_AGENT_URL, initial_message)
    await _post_pubsub(config.PLANNING_AGENT_URL, a2a.build_message(
        initial_message["contextId"],
        config.TOPIC_SCENARIO_INTERPRETED,
        firestore.get_context(initial_message["contextId"]).get("intent", {}),
    ).model_dump())
    await _post_pubsub(config.API_REASONING_AGENT_URL, a2a.build_message(
        initial_message["contextId"],
        config.TOPIC_WORKFLOW_PLANNED,
        firestore.get_context(initial_message["contextId"]).get("plan", {}),
    ).model_dump())
    await _post_pubsub(config.SYNTHETIC_DATA_AGENT_URL, a2a.build_message(
        initial_message["contextId"],
        config.TOPIC_APIS_DISCOVERED,
        {
            "plan": firestore.get_context(initial_message["contextId"]).get("plan", {}),
            "apis": firestore.get_context(initial_message["contextId"]).get("apis", []),
        },
    ).model_dump())
    await _post_pubsub(config.EXECUTION_AGENT_URL, a2a.build_message(
        initial_message["contextId"],
        config.TOPIC_DATA_GENERATED,
        {
            "data": firestore.get_context(initial_message["contextId"]).get("data", {}),
            "plan": firestore.get_context(initial_message["contextId"]).get("plan", {}),
        },
    ).model_dump())
    await _post_pubsub(config.VERIFICATION_AGENT_URL, a2a.build_message(
        initial_message["contextId"],
        config.TOPIC_WORKFLOW_EXECUTED,
        firestore.get_context(initial_message["contextId"]).get("execution", {}),
    ).model_dump())
