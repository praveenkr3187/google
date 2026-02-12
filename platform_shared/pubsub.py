import json
from typing import Dict

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import pubsub_v1

from .config import MOCK_PUBSUB, PUBSUB_PROJECT_ID


_publisher: pubsub_v1.PublisherClient | None = None


def _get_publisher() -> pubsub_v1.PublisherClient:
    global _publisher
    if _publisher is None:
        _publisher = pubsub_v1.PublisherClient()
    return _publisher


def publish_message(topic: str, message: Dict) -> str:
    if MOCK_PUBSUB:
        return "mock-publish"
    publisher = _get_publisher()
    topic_path = publisher.topic_path(PUBSUB_PROJECT_ID, topic)
    data = json.dumps(message).encode("utf-8")
    try:
        future = publisher.publish(topic_path, data=data)
        return future.result()
    except DefaultCredentialsError:
        return "mock-publish"
