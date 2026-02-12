#!/bin/bash
set -euo pipefail

PROJECT_ID=${PUBSUB_PROJECT_ID:-${GOOGLE_CLOUD_PROJECT:-local-dev}}

create_topic() {
  local name=$1
  gcloud pubsub topics create "$name" --project "$PROJECT_ID" || true
}

create_push_sub() {
  local topic=$1
  local sub=$2
  local endpoint=$3
  gcloud pubsub subscriptions create "$sub" \
    --topic "$topic" \
    --project "$PROJECT_ID" \
    --push-endpoint "$endpoint" \
    --push-auth-service-account="$PUSH_SERVICE_ACCOUNT" || true
}

create_topic "scenario.received"
create_topic "scenario.interpreted"
create_topic "workflow.planned"
create_topic "apis.discovered"
create_topic "data.generated"
create_topic "workflow.executed"
create_topic "workflow.completed"

# Update PUSH_SERVICE_ACCOUNT and endpoints before running
# Example endpoints assume Cloud Run URLs with /pubsub/push
# create_push_sub "scenario.received" "intent-agent-sub" "https://intent-agent-xyz.a.run.app/pubsub/push"
# create_push_sub "scenario.interpreted" "planning-agent-sub" "https://planning-agent-xyz.a.run.app/pubsub/push"
# create_push_sub "workflow.planned" "api-reasoning-sub" "https://api-reasoning-agent-xyz.a.run.app/pubsub/push"
# create_push_sub "apis.discovered" "synthetic-data-sub" "https://synthetic-data-agent-xyz.a.run.app/pubsub/push"
# create_push_sub "data.generated" "execution-agent-sub" "https://execution-agent-xyz.a.run.app/pubsub/push"
# create_push_sub "workflow.executed" "verification-agent-sub" "https://verification-agent-xyz.a.run.app/pubsub/push"

echo "Pub/Sub topics created. Configure push subscriptions as needed."
