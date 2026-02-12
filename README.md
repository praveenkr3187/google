# Enterprise A2A Platform (SAP Concur MVP)

An event-driven, multi-agent platform that interprets business scenarios, plans workflows, discovers SAP APIs via a Knowledge Graph, generates synthetic data, executes mock SAP Concur API calls, verifies results, and returns created record IDs. This MVP is designed for Google Cloud with Cloud Run + Pub/Sub + Firestore.

## Architecture Summary

- **Frontend**: React (Cloud Run)
- **Agents (Cloud Run services)**:
    - Scenario Gateway / Orchestrator
    - Intent Agent
    - Planning Agent
    - API Reasoning Agent (Knowledge Graph)
    - Synthetic Data Agent
    - Execution Agent
    - Verification Agent
- **Event Bus**: Google Pub/Sub (A2A message schema)
- **State Storage**: Firestore
- **Knowledge Graph**: Neo4j (GKE/AuraDB) or mock KG
- **SAP Concur**: Mock FastAPI server

## A2A Message Schema

All messages follow:

```
{
    "contextId": "uuid",
    "taskType": "STRING",
    "payload": {},
    "timestamp": "ISO8601"
}
```

## Project Structure

```
prai-roadshow-lab-1-starter/
├── platform_shared/           # Shared A2A, Pub/Sub, Firestore, KG utilities
├── services/
│   ├── orchestrator/          # /run-scenario entry point
│   ├── intent_agent/          # scenario.received → scenario.interpreted
│   ├── planning_agent/        # scenario.interpreted → workflow.planned
│   ├── api_reasoning_agent/   # workflow.planned → apis.discovered
│   ├── synthetic_data_agent/  # apis.discovered → data.generated
│   ├── execution_agent/       # data.generated → workflow.executed
│   ├── verification_agent/    # workflow.executed → workflow.completed
│   └── mock_sap_concur/        # Mock SAP Concur APIs
├── scripts/
│   ├── seed_kg.py              # Seed Enterprise Knowledge Graph
│   └── ingest_kg.py            # Simplified ingestion pipeline
├── frontend/                   # React UI (Vite)
└── run_local.sh                # Local runner
```

## Pub/Sub Topics

- `scenario.received`
- `scenario.interpreted`
- `workflow.planned`
- `apis.discovered`
- `data.generated`
- `workflow.executed`
- `workflow.completed`

## Local Run

1. Install dependencies
     ```bash
     uv sync
     ```

2. Start local services
     ```bash
     ./run_local.sh
     ```

3. Frontend (optional)
     ```bash
     cd frontend
     npm install
     npm run dev
     ```
     Open http://localhost:5173

4. Test Orchestrator
     ```bash
     curl -X POST http://localhost:8081/run-scenario \
         -H "Content-Type: application/json" \
         -d '{"scenario": "Generate 5 overdue invoices for a US vendor in Concur"}'
     ```

## Knowledge Graph

- **Schema**: `SAPProduct`, `BusinessObject`, `APIEndpoint`
- **Relationships**:
    - `SAPProduct` → `HAS_OBJECT` → `BusinessObject`
    - `APIEndpoint` → `CREATES` → `BusinessObject`
    - `BusinessObject` → `DEPENDS_ON` → `BusinessObject`

Seed the KG:
```bash
uv run python scripts/seed_kg.py
```

## Deployment (Google Cloud)

1. **Provision**
     - Cloud Run services for each agent + mock SAP API + frontend
     - Pub/Sub topics + push subscriptions
     - Firestore (Native mode)
     - Neo4j on GKE or AuraDB (optional; mock KG supported)

2. **Deploy each Cloud Run service**
     Example for orchestrator:
     ```bash
     gcloud run deploy orchestrator \
         --source . \
         --region us-central1 \
         --set-env-vars PUBSUB_PROJECT_ID=$GOOGLE_CLOUD_PROJECT,FIRESTORE_COLLECTION=workflow_contexts
     ```

3. **Pub/Sub Push Subscriptions**
     Configure push endpoints for each agent:
     - Intent Agent → `scenario.received` → `/pubsub/push`
     - Planning Agent → `scenario.interpreted` → `/pubsub/push`
     - API Reasoning Agent → `workflow.planned` → `/pubsub/push`
     - Synthetic Data Agent → `apis.discovered` → `/pubsub/push`
     - Execution Agent → `data.generated` → `/pubsub/push`
     - Verification Agent → `workflow.executed` → `/pubsub/push`

4. **Frontend**
     Deploy `frontend/` to Cloud Run and set:
     - `VITE_ORCHESTRATOR_URL` to the orchestrator URL.

## Mock SAP Concur API

Endpoints:
- `POST /vendors`
- `POST /invoices`
- `GET /invoices`
- `POST /expenses`
- `GET /expenses`

Overdue rule:
```
dueDate < today AND paymentStatus != "Paid"
```
