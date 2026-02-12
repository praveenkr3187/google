#!/bin/bash

# Kill any existing processes on these ports
echo "Stopping any existing processes on ports 8081-8087 and 9000..."
lsof -ti:8081,8082,8083,8084,8085,8086,8087,9000 | xargs kill -9 2>/dev/null

export SAP_MOCK_BASE_URL=${SAP_MOCK_BASE_URL:-"http://localhost:9000"}
export PUBSUB_PROJECT_ID=${PUBSUB_PROJECT_ID:-"local-dev"}
export MOCK_PUBSUB=${MOCK_PUBSUB:-"true"}

echo "Starting Mock SAP Concur API on port 9000..."
uv run uvicorn services.mock_sap_concur.main:app --host 0.0.0.0 --port 9000 &
MOCK_SAP_PID=$!

echo "Starting Orchestrator on port 8081..."
uv run uvicorn services.orchestrator.main:app --host 0.0.0.0 --port 8081 &
ORCHESTRATOR_PID=$!

echo "Starting Intent Agent on port 8082..."
uv run uvicorn services.intent_agent.main:app --host 0.0.0.0 --port 8082 &
INTENT_PID=$!

echo "Starting Planning Agent on port 8083..."
uv run uvicorn services.planning_agent.main:app --host 0.0.0.0 --port 8083 &
PLANNING_PID=$!

echo "Starting API Reasoning Agent on port 8084..."
uv run uvicorn services.api_reasoning_agent.main:app --host 0.0.0.0 --port 8084 &
API_REASONING_PID=$!

echo "Starting Synthetic Data Agent on port 8085..."
uv run uvicorn services.synthetic_data_agent.main:app --host 0.0.0.0 --port 8085 &
DATA_PID=$!

echo "Starting Execution Agent on port 8086..."
uv run uvicorn services.execution_agent.main:app --host 0.0.0.0 --port 8086 &
EXECUTION_PID=$!

echo "Starting Verification Agent on port 8087..."
uv run uvicorn services.verification_agent.main:app --host 0.0.0.0 --port 8087 &
VERIFICATION_PID=$!

echo "All services started!"
echo "Orchestrator: http://localhost:8081"
echo "Intent Agent: http://localhost:8082"
echo "Planning Agent: http://localhost:8083"
echo "API Reasoning Agent: http://localhost:8084"
echo "Synthetic Data Agent: http://localhost:8085"
echo "Execution Agent: http://localhost:8086"
echo "Verification Agent: http://localhost:8087"
echo "Mock SAP API: http://localhost:9000"
echo "Note: Pub/Sub topics and push subscriptions must be configured for end-to-end flow."
echo ""
echo "Press Ctrl+C to stop all agents."

# Wait for all processes
trap "kill $MOCK_SAP_PID $ORCHESTRATOR_PID $INTENT_PID $PLANNING_PID $API_REASONING_PID $DATA_PID $EXECUTION_PID $VERIFICATION_PID; exit" INT
wait
