import os

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or "local-dev"

PUBSUB_PROJECT_ID = os.getenv("PUBSUB_PROJECT_ID", PROJECT_ID)

FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "workflow_contexts")

TOPIC_SCENARIO_RECEIVED = os.getenv("TOPIC_SCENARIO_RECEIVED", "scenario.received")
TOPIC_SCENARIO_INTERPRETED = os.getenv("TOPIC_SCENARIO_INTERPRETED", "scenario.interpreted")
TOPIC_WORKFLOW_PLANNED = os.getenv("TOPIC_WORKFLOW_PLANNED", "workflow.planned")
TOPIC_APIS_DISCOVERED = os.getenv("TOPIC_APIS_DISCOVERED", "apis.discovered")
TOPIC_DATA_GENERATED = os.getenv("TOPIC_DATA_GENERATED", "data.generated")
TOPIC_WORKFLOW_EXECUTED = os.getenv("TOPIC_WORKFLOW_EXECUTED", "workflow.executed")
TOPIC_WORKFLOW_COMPLETED = os.getenv("TOPIC_WORKFLOW_COMPLETED", "workflow.completed")

SAP_MOCK_BASE_URL = os.getenv("SAP_MOCK_BASE_URL", "http://localhost:9000")

KG_URI = os.getenv("KG_URI", "bolt://localhost:7687")
KG_USER = os.getenv("KG_USER", "neo4j")
KG_PASSWORD = os.getenv("KG_PASSWORD", "password")
KG_MODE = os.getenv("KG_MODE", "mock")  # mock or neo4j

ORCHESTRATOR_TIMEOUT_SECONDS = int(os.getenv("ORCHESTRATOR_TIMEOUT_SECONDS", "120"))

MOCK_PUBSUB = os.getenv("MOCK_PUBSUB", "false").lower() == "true"

INTENT_AGENT_URL = os.getenv("INTENT_AGENT_URL", "http://localhost:8082")
PLANNING_AGENT_URL = os.getenv("PLANNING_AGENT_URL", "http://localhost:8083")
API_REASONING_AGENT_URL = os.getenv("API_REASONING_AGENT_URL", "http://localhost:8084")
SYNTHETIC_DATA_AGENT_URL = os.getenv("SYNTHETIC_DATA_AGENT_URL", "http://localhost:8085")
EXECUTION_AGENT_URL = os.getenv("EXECUTION_AGENT_URL", "http://localhost:8086")
VERIFICATION_AGENT_URL = os.getenv("VERIFICATION_AGENT_URL", "http://localhost:8087")
